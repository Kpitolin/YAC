""" This file allows you to create an Inverted Index. """

import glob
import re
import time
import sys
import pickle
import os
from blist import sorteddict, sortedlist

import tokenization
import score


PATTERN_DOC_ID = r"<DOCID>\s(\d+)\s</DOCID>"
PATTERN_DOC_END = r"</DOC>"


class Index:
    """ Example of inv_index :
    { "term 1": {1:1}, "term 2": {3:1}, "term 3":{2:1, 4:1}}
    The inner dictionnary is structured that way : {doc_id:score} both are int for now
    """

    @property
    def memory_limit(self):
        return self.memory_limit
    @memory_limit.setter
    def memory_limit(self, value):
        self.memory_limit = value


    def __init__(self, memory_limit = 1000000, filter_tags=False, remove_stopwords=False, case_sensitive=False, with_stemming=False):
        self.memory_limit = memory_limit # Max size of self.inv_index in bytes, if reached in merge-based mode it is saved in file
        self.filter_tags = filter_tags
        self.inv_index = {} # Contains the whole index in in-memory mode
        self.remove_stopwords = remove_stopwords
        self.case_sensitive = case_sensitive
        self.with_stemming = with_stemming
        self.indexed = False

        self._doc_id_list = [] # Contains the ids of the documents indexed
        self._partial_files_names = [] # Contains the filenames of the partial index in merge-based mode
        self.dict_terms_offset = dict() # Keep the line where each term is in InvertedFile
        self.offset = 1;

        self.dict_file_term = sorteddict()
        self.dict_term_pl = dict()


    def index_files(self, file_path_format):
        self.in_memory = True # True if the entire index is kept in memory, else merge-based method is used
        for filename in glob.glob(file_path_format):
            lines = open(filename, 'r')
            self.index_documents(lines)
        # No merge if all the index is in memory
        if self.in_memory:
            self.update_scores_with_idf()
        else:
            self.write_partial_index() # Write the last file
            self.merge_partial_indexs()
        self.indexed = True
        return self.indexed

    def index_text(self, text, in_memory = True):
        self.in_memory = in_memory
        self.index_documents(text)
        # No merge if all the index is in memory
        if self.in_memory:
            self.update_scores_with_idf()
        else:
            self.write_partial_index() # Write the last file
            self.merge_partial_indexs()
        self.indexed = True
        return self.indexed

    # Revoir la valeur retournee
    def use_existing_index(self):
        """  """

        if os.path.isfile("Offsets") and os.path.isfile("InvertedFile"):
            self.in_memory = False
            self.indexed = True
            # Load offsets from the file where it has been previously saved
            with open('Offsets', "r") as f:
                self.dict_terms_offset = pickle.load(f)
            return True
        return False

    def index_documents(self, text):
        """ Indexes documents """
        lines = [] # The lines of the file that is being indexed
        if hasattr(text, 'readlines'): # Textfile
            lines = text
        elif isinstance(text, str): # Multi-line string
            lines = text.splitlines(False)

        doc_id = '' # The id of the doc we are actually looking at
        doc = '' # The text already read from the doc we are looking at
        for line in lines:
            doc += '\n' + line
            match = re.search(PATTERN_DOC_ID, line)
            if match:
                # Extraction of the doc id from the line : the first group in the regex (what's between parenthesis)
                doc_id = int(match.group(1))
            elif re.search(PATTERN_DOC_END, line) and doc_id != '':
                words = tokenization.TextFile.tokenize_string_split(doc, self.filter_tags, self.remove_stopwords, self.case_sensitive, self.with_stemming)
                # For the time being, we just calculate the frequency of each term and put it as the score
                if len(words) > 0: # If the document has at least a term to index
                    self._doc_id_list.append(doc_id)
                    score = 1.0/len(words)
                    for word in words:
                        if word not in self.inv_index:
                            self.inv_index[word] = {}
                        if doc_id not in self.inv_index[word]:
                            self.inv_index[word][doc_id] = score
                        else:
                            self.inv_index[word][doc_id] += score
                    if sys.getsizeof(self.inv_index) >= self.memory_limit: # If we reached the memory limit
                        self.write_partial_index()
                        self.in_memory = False
                        self.inv_index = {}
                doc_id = ''
                doc = ''

        return self.inv_index

    def update_scores_with_idf(self):
        """ Replaces the temporary score by the tf idf in each item of the index dictionnary """

        for term, pl in self.inv_index.iteritems():
            for doc_id in self.inv_index[term]:
                self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(pl), len(self._doc_id_list))


    def write_partial_index(self):
        """ Creates a file following this format :
        term
        Posting List
        term
        Posting List

        Then adds the filename to self._partial_files_names
        """

        filename = "partialIndex" + str(time.clock())
        with open(filename,"a+") as f:
            sorted_terms = sorted(self.inv_index)
            for word in sorted_terms :
                f.write(word+"\n")
                f.write(self.posting_list_to_text(self.inv_index[word]))
                f.write("\n")

        if len(sorted_terms) > 0:
            self._partial_files_names.append(filename)

    # def save_index(self):
    #     if self.indexed:
    #         if self.in_memory:
    #             for term in self.inv_index:
    #
    #     else:
    #         print "Can't save index if it has not been idexed !"


    # TODO Changer le fonctionnement de dictFile
    def merge_partial_indexs(self):
        """ "It reads the ith term of each file, find the lowest term (alphabetical order)
        and updates a data structure [filename : <term, line>] ordered by term and filename
        Calls save_final_pl_to_file

        dictFileLine is a data structure {filename: line} that allows us to have the last cursor position of everything file saved
        """

        term = ''
        dictFileLine = {}
        #fileFinished=list()#
        # Initialization: open all the inverted file and read the first term into the dictionary of terms sorted by key
        for partial_file_name in self._partial_files_names:
            with open(partial_file_name, "r+") as file_content:
                self.read_terms_from_i_file(file_content, partial_file_name)
                dictFileLine[partial_file_name] = file_content.tell()
        # Pop the first term of the dictionary and update the dic by reading the following lines of the file
        while bool(self.dict_file_term):
            term, partial_files_names = self.dict_file_term.popitem() # Returns the pair <term, [filename]> with the lowest key (sorteddict)
            pl = self.dict_term_pl[term]
            if self.write_merged_pl(term, pl):
                for partial_file_name in partial_files_names:
                    file_content = open(partial_file_name, "r+")
                    if partial_file_name in dictFileLine:
                        file_content.seek(dictFileLine[partial_file_name])
                    if not self.read_terms_from_i_file(file_content, partial_file_name):
                        file_content.close()
                        del file_content
                        del dictFileLine[partial_file_name]
                    else:
                        dictFileLine[partial_file_name] = file_content.tell()
            else:
                return False
        # Save the offsets in a file
        with open('Offsets', "w") as f:
            pickle.dump(self.dict_terms_offset, f)

    def read_terms_from_i_file(self, f, partial_file_name):
        """ X """

        pattern_term = r"-?<?/?\w+"
        term = f.readline()
        pl = f.readline().rstrip()
        if len(term) != 0 and not re.match(pattern_term, term):
            return self.read_terms_from_i_file(f, partial_file_name) # if we didn't find a term, we try again until end of file
        elif len(term) == 0 :
            return False
        if term not in self.dict_file_term.keys():
            self.dict_file_term[term] = sortedlist([partial_file_name])
            self.dict_term_pl[term] = [pl]
        else:
            (self.dict_file_term[term]).add(partial_file_name)
            index_0 = (self.dict_file_term[term]).index(partial_file_name)
            (self.dict_term_pl[term]).insert(index_0, pl)
        return True

    def write_merged_pl(self, term, pl):
        """ Writes the complete pl of term in the file containing the final Inverted Index """

        list_pls = self.calculate_all_term_pl_scores(pl)

        with open('InvertedFile', "a+") as inverted_file:
            inverted_file.write(self.pair_list_to_text(list_pls)+"\n")
            self.dict_terms_offset[term.rstrip()] = self.offset
            self.offset += 1
        return True

    def calculate_all_term_pl_scores(self, pl):
        """ Modify final inverted file to write final score for each doc in each pl """

        list_pls = []
        for sring_pls in pl:
            list_pls = list_pls + self.text_to_pair_list(sring_pls)
        list_pls = sorted(list_pls, key=lambda x: x[0])
        for index in range(len(list_pls)):
                (doc_id, score_temp) = map(float, list_pls[index])
                score_temp *= score.inverse_document_frequency(len(list_pls), len(self._doc_id_list))
                list_pls[index] = (doc_id, score_temp)
        return list_pls

    ########## CONVERTION FUNCTIONS ##########

    def posting_list_to_text(self, pl):
        """ Transforms a posting list {<doc_id, score>} in text with comas and semi colons :
            docId, Score;  docId, Score;
        """

        text = ""
        for key, value in pl.iteritems():
            text = text + str(key) + "," + str(value) + ";"
        return text

    def pair_list_to_text(self, pl):
        """ Transforms a posting list [<docId, Score>] in text with comas and semi colons :
            docId, Score;  docId, Score;
        """

        text = ""
        for key, value in pl:
            text = text + str(key) + "," + str(value) + ";"
        return text

    def text_to_pair_list(self, text):
        """ Transforms a text (docId, Score;  docId, Score;) to a posting list [<docId, Score>] """

        lines = []
        pair_list = []
        #textfile
        if hasattr(text, 'readlines'):
            lines = text
        #multi-line string
        elif isinstance(text,str):
            lines = text.splitlines(False)
        for line in lines:
            pair_list = text.rstrip().split(";")[:-1]
            for index in range(len(pair_list)):
                pair = pair_list[index].split(",")
                pair_list[index] = (pair[0],pair[1])
        return pair_list

    ########## UNUSED FUNCTIONS ##########

    def read_terms_from_i_file_with_line_deleting(self,f,ifilename):
        pattern_term = r"-?<?/?\w+"
        term = f.readline()
        pl = f.readline().rstrip()
        if len(term) != 0 and not re.match(pattern_term,term):
            return self.read_terms_from_i_file_with_line_deleting(f,ifilename) # if we didn't find a term, we try again until end of file
        elif len(term) == 0 :
            return False
        if term not in self.dict_file_term.keys():
            self.dict_file_term[term] =sortedlist([ifilename])
            self.dict_term_pl[term] = [pl]
        else:
            (self.dict_file_term[term]).add(ifilename)
            index_0 = (self.dict_file_term[term]).index(ifilename)
            (self.dict_term_pl[term]).insert(index_0,pl)
        self.remove_lines_from_last_cursor_position(f) # we remove the two lines we just read
        return True

    def remove_lines_from_file_start(self,file_object,nb_lines_to_remove):
        """
        In a file already open (so we can read and write), for example in r+ mode,
        we want to remove the nb_lines_to_remove from """
        file_object.seek(0) # go to beginning of file
        data = file_object.read().splitlines(True) # save the lines of the file in list
        file_object.seek(0) # go to beginning of file
        if len(data) < nb_lines_to_remove:
            file_object.write("")
        else:
            file_object.writelines(data[nb_lines_to_remove:]) # writes lines minus the first nb_lines_to_remove ones
        #print data[0:nb_lines_to_remove]
        file_object.truncate() # the file size is reduced to remove the rest
        file_object.close()


    def remove_lines_from_last_cursor_position(self,file_object):
        """
        In a file already open (so we can read and write), for example in r+ mode,
        we want to remove the nb_lines_to_remove from """
        data = file_object.read().splitlines(True) # save the lines of the file in list
        file_object.seek(0) # go to beginning of file
        file_object.writelines(data)
        file_object.truncate() # the file size is reduced to remove the rest
        file_object.close()


    def read_terms_in_file_line_dic(self):
        """It reads the ith term of each file, find the lowest term (alphabetical order)
            and updates a data structure [filename : <term, line>] ordered by term and filename
            Calls save_final_pl_to_file

            dictFileLine is a data structure {filename: line} that allows us to have the last cursor position of everything file saved
        """
        term=''
        dictFileLine = {}
        # Initialization: open all the inverted file and read the first term into the dictionary of terms sorted by key
        for ifilename in self._pl_file_list :
            with open(ifilename, "r+") as file_content:
                self.read_terms_from_i_file(file_content,ifilename)
                dictFileLine[ifilename] = file_content.tell()
        # Pop the first term of the dictionary and update the dic by reading the following lines of the file
        while bool(self.dict_file_term):
            element = self.dict_file_term.popitem() # return the pair <term, [filename]> with the lowest key (sorteddict)
            pl=self.dict_term_pl[element[0]]
            if(self.save_final_pl_to_file(element[0],pl)):
                for ifilename in element[1]:
                    file_content = open(ifilename, "r+")
                    if ifilename in dictFileLine:
                        file_content.seek(dictFileLine[ifilename])
                    if(self.read_terms_from_i_file(file_content,ifilename) == False):
                        file_content.close()
                        del file_content
                        del dictFileLine[ifilename]
                    else:
                        dictFileLine[ifilename] = file_content.tell()

            else:
                return False
        # After readind 100 (configurable) terms in memory ,flush them into the final inverted File
        self.save_extra_file()
