""" This file allows you to create an Inverted Index. """

import glob
import re
import tokenization
import score
import time
import sys
from blist import sorteddict, sortedlist


PATTERN_DOC_ID = r"<DOCID>\s(\d+)\s</DOCID>"
PATTERN_DOC_END = r"</DOC>"


class Index:
    """ Example of inv_index :
    { "term 1": {1:1}, "term 2": {3:1}, "term 3":{2:1, 4:1}}
    The inner dictionnary is structured that way : {doc_id:score} both are int for now
    """

    @property
    def current_doc_index(self):
        return self._current_doc_index
    @current_doc_index.setter
    def current_doc_index(self, value):
        self._current_doc_index = value

    @property
    def doc_limit(self):
        return self._doc_limit

    @doc_limit.setter
    def doc_limit(self, value):
        self._doc_limit = value

    @property
    def memory_limit(self):
        return self._memory_limit
    @memory_limit.setter
    def memory_limit(self, value):
        self._memory_limit = value


    def __init__(self, memory_limit = 1000000, filter_tags=False, remove_stopwords=False, case_sensitive=False, with_stemming=False):
        self.memory_limit = memory_limit # Max size of self.inv_index in bytes, if reached in merge-based mode it is saved in file
        self.filter_tags = filter_tags
        self.inv_index = {} # Contains the whole index in in-memory mode
        self.remove_stopwords = remove_stopwords
        self.case_sensitive = case_sensitive
        self.with_stemming = with_stemming
        self.indexed = False


        self._doc_id_list = []
        self._pl_file_list = [] # Contains names of the partial index files in merge-based mode
        self._current_doc_index = 0
        self._doc_quantity = 0
        self.offset = 1;

        self.dict_file_term = sorteddict()
        self.dict_term_pl = dict()

        self.dict_terms_offset = dict()


    def index(self, file_path_format):
        self.file_path_format = file_path_format
        self.in_memory = True # If true the entire index will be keep in memory, else merge-based method is used
        if self.in_memory:
            self.index_in_memory()
        else:
            self.index_in_file()
        self.indexed = True
        return self.indexed

    def use_existing_index(self):
        if os.path.isfile("Offsets") and os.path.isfile("InvertedFile"):
            self.in_memory = False
            self.indexed = True
            self.load_offsets()
            return True
        return False

    ########## INDEXING IN FILE ##########

    def index_in_file(self):
        """ Creates the Inverted Index for a file or multiple file of the same format using
        For now, the score is just the frequency of the term in the document

        Usage for every file starting with la (outside of this module):
        inv_index = indexing.Index("../../../../Downloads/latimes/la*").createIndexFromFileFormat()

        Usage for a file
        inv_index = indexing.Index("../../../../Downloads/latimes/la010189").createIndexFromFileFormat()
        """

        if self.file_path_format != "":
            for filename in sorted(glob.glob(self.file_path_format)):
                lines = open(filename, 'r')
                self.index_in_partial_file(lines)
            # TODO No merge if all the index is in memory
            if not self.in_memory:
                self.save_index_to_file() # Write the last file
                self.merge_partial_indexs()


    def index_in_partial_file(self, text):
        """ Creates partial indexe in self.inv_index

        We read text from the stream doc by doc until we reach self.memory_limit
        Everytime, we update a map {term :[<docId, Score>]} the posting list [<docId, Score>] must be ordered by docId
        """

        lines = [] # The lines of the file that is being indexed
        if hasattr(text, 'readlines'): # Textfile
            lines = text
        elif isinstance(text, str): # Multi-line string
            lines = text.splitlines(False)

        doc_id = '' # The id of the doc we are actually looking at
        doc = '' # The text already read from the doc we are looking at
        for line in lines:
            match = re.search(PATTERN_DOC_ID, line)
            if match:
                # Extraction of the doc id from the line : the first group in the regex (what's between parenthesis)
                doc_id = int(match.group(1))
                doc = ''
            elif re.search(PATTERN_DOC_END, line) and doc != '':
                words = tokenization.TextFile.tokenize_string_split(doc, self.filter_tags, self.remove_stopwords, self.case_sensitive, self.with_stemming)
                # For the time being, we just calculate the frequency of each term and put it as the score
                if len(words) > 0: # If the document has at least a term to index
                    self._doc_id_list.append(doc_id)
                    score = 1.0/len(words)
                    for word in words:
                        if word not in self.inv_index:
                            self.inv_index[word] = [(doc_id, score)]
                        else:
                            lastDocIndex = len(self.inv_index[word]) - 1
                            (docIdTemp, scoreTemp) = self.inv_index[word][lastDocIndex]
                            if doc_id != docIdTemp:
                                self.inv_index[word].append((doc_id, score))
                            else:
                                self.inv_index[word].pop()
                                self.inv_index[word].append((docIdTemp, score + scoreTemp))
                    if sys.getsizeof(self.inv_index) >= self.memory_limit: # If we reached the memory limit
                        self.save_index_to_file()
                        self.inv_index = {}
            else:
                doc += '\n' + line

    def save_index_to_file(self):
        """ Creates a file following this format :
        term
        Posting List
        term
        Posting List

        Then adds the filename to self._pl_file_list
        """

        filename = "partialIndex" + str(time.clock())
        with open(filename,"a+") as f:
            sorted_index = sorted(self.inv_index)
            for word in sorted_index :
                f.write(word+"\n")
                f.write(self.pair_list_to_text(self.inv_index[word]))
                f.write("\n")

        if len(sorted_index) > 0:
            self._pl_file_list.append(filename)


    def merge_partial_indexs(self):
        """ It reads the ith term of each file, find the lowest term (alphabetical order) and updates a data structure [filename : <term, line>] ordered by term and filename
        Calls write_merged_pl

        dictFile is a data structure {filename: content} that allows us to have the state of everything open file saved (with the cursor at the last line read)
        """

        term = ''
        dictFile = {}
        #fileFinished=list()#
        # Initialization: open all the inverted file and read the first term into the dictionary of terms sorted by key
        for ifilename in self._pl_file_list :
            dictFile[ifilename] = open(ifilename, "r");
            self.read_terms_from_i_file(dictFile[ifilename],ifilename)
        # Pop the first term of the dictionary and update the dic by reading the following lines of the file
        while bool(self.dict_file_term):
            element = self.dict_file_term.popitem() # Returns the pair <term, [filename]> with the lowest key (sorteddict)
            pl = self.dict_term_pl[element[0]]
            #dictFile[ifilename]
            #dictFile[ifilename].close()
            if(self.write_merged_pl(element[0], pl)):
                for ifilename in element[1]:
                    if not self.read_terms_from_i_file(dictFile[ifilename], ifilename):
                        dictFile[ifilename].close()
                        del dictFile[ifilename]
            else:
                return False
        # After readind 100 (configurable) terms in memory ,flush them into the final inverted File
        self.save_offsets()

    def read_terms_from_i_file(self, f, ifilename):
        """ X """

        pattern_term = r"<?/?\w+"
        term = f.readline()
        pl = f.readline().rstrip()
        if len(term) != 0 and not re.match(pattern_term,term):
            return self.read_terms_from_i_file(f,ifilename)
        elif len(term) == 0 :
            return False
        if term not in self.dict_file_term.keys():
            self.dict_file_term[term] = sortedlist([ifilename])
            self.dict_term_pl[term] = [pl]
        else:
            (self.dict_file_term[term]).add(ifilename)
            index_0 = (self.dict_file_term[term]).index(ifilename)
            (self.dict_term_pl[term]).insert(index_0,pl)
        return True

    def write_merged_pl(self, term, pl):
        """ Creates a single file for the posting lists. format :
        PL;PL2;PL3 and so on
        It writes each posting list from offsetMin to offsetMax
        It also writes a dic {term : <offsetMin, offsetMax>}
        """

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
                (doc_id, scoreTemp) = map(float,list_pls[index])
                scoreTemp *= score.inverse_document_frequency(len(list_pls), len(self._doc_id_list))
                list_pls[index] = (doc_id, scoreTemp)
        return list_pls

    # TODO : Use pickle module to save the dict
    def save_offsets(self):
        """ Saves the nb of docs to file
        It also writes a dic {term : <offsetMin, offsetMax>}
        """

        with open('Offsets', "w") as offsets_file:
            offsets_file.write(self.dict_to_text(self.dict_terms_offset))

    # TODO : Use pickle module to load the dict
    # TODO : Try
    def load_offsets(self):
        """ Loads offsets from the file where it has been previously saved """

        with open('Offsets', "r") as f:
            text = f.readline()
            tuple_list = text.rstrip().split(";")[:-1]
            for index in range(len(tuple_list)):
                pair = tuple_list[index].split(",")
                self.dict_terms_offset[pair[0]] = int(pair[1])


    ########## INDEXING IN MEMORY ##########

    def index_in_memory(self):
        """ Creates the Inverted Index for a file or multiple file of the same format
        For now, the score is just the frequency of the term in the document


        Usage for every file starting with la (outside of this module):
        inv_index = indexing.Index("../../../../Downloads/latimes/la*").createIndexFromFileFormat()

        Usage for a file
        inv_index = indexing.Index("../../../../Downloads/latimes/la010189").createIndexFromFileFormat()
        """

        if self.file_path_format != "":
            #filling of the Inverted Index
            for filename in sorted(glob.glob(self.file_path_format)):
                lines = open(filename, 'r')
                self.inv_index = self.index_text_in_memory(lines)
            update_scores_with_idf()
        return self.inv_index

    # We had a pb in inv_index => if you execute the function two times in a row with default parameters, inv_index has a value the second time
    def index_text_in_memory(self, text):
        """ Creates the Inverted Index for a text

        Usage
        a = indexing.Index().index_text_in_memory(textMultiline)
        """

        doc_id = ''
        doc = ''
        lines = []

        #textfile
        if hasattr(text, 'readlines'):
            lines = text
        #multi-line string
        elif isinstance(text,str):
            lines = text.splitlines(False)

        for line in lines:
            doc += line
            match = re.search(PATTERN_DOC_ID, line)
            if match:
                #extract the docid from the line : the first group in the regex (what's between parenthesis)
                doc_id = int(match.group(1))
            elif re.search(PATTERN_DOC_END, line) and doc != '' and doc_id != '':
                #if we reached the end of the document, insert tokens in hashmap and flush variables

                words = tokenization.TextFile.tokenize_string_split(doc, self.filter_tags, self.remove_stopwords, self.case_sensitive, self.with_stemming)

                # for the time being, we just calculate the frequency of each term and put it as the score
                if len(words) > 0:
                    self._doc_id_list.append(doc_id)
                    score = 1.0/len(words)
                    for word in words:
                        if not word in self.inv_index:
                            self.inv_index[word] = {}
                        if not doc_id in self.inv_index[word]:
                            self.inv_index[word][doc_id] = score
                        else:
                            self.inv_index[word][doc_id] += score
                    # flush variables before passing to the next document
                    doc = ''
                    del doc_id

        return self.inv_index


    def update_scores_with_idf(self):
        """ Replaces the temporary score by the tf idf in each item of the index dictionnary """

        for term, pl in self.inv_index.iteritems():
            for doc_id in self.inv_index[term]:
                self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(pl), len(self._doc_id_list))

    # TODO A quoi sert cette methode ?
    # def calculate_terms_in_query_scores_memory(self, query):
    #     """ Replaces the temporary score by the tf idf in each item of the index dictionnary that's in the query """
    #
    #     for term in score.get_terms(query):
    #         #print list(self.inv_index.iteritems())
    #         if term in self.inv_index:
    #             pl = self.inv_index[term]
    #             for doc_id in pl:
    #                 self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(pl), len(self._doc_id_list))

    ########## CONVERTION FUNCTIONS ##########

    def pair_list_to_text(self,pl):
        """ Transforms a posting list [<docId, Score>] in text with comas and semi colons :
            docId, Score;  docId, Score;
        """

        text = ""
        for (item1, item2) in pl:
            text = text + str(item1)+","+ str(item2)+";"
        return text

    def dict_to_text(self,pl):
        """ X """

        text = ""
        for item1, item2 in pl.iteritems():
            text = text + str(item1)+","+ str(item2)+";"
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
