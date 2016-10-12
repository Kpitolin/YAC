"""This file allows you to create an Inverted Index."""

import glob
import re
import tokenization
import score

PATTERN_DOC_ID = r"<DOCID>\s(\d+)\s</DOCID>"
PATTERN_DOC_END = r"</DOC>"


class Index:
    """Example of inv_index :
    { "term 1": {1:1}, "term 2": {3:1}, "term 3":{2:1, 4:1}}
    The inner dictionnary is structured that way : {doc_id:score} both are int for now
	"""

    doc_id_list = []

    def __init__(self, file_path_format = "", filter_tags=False, remove_stopwords=False, case_sensitive=False, with_stemming=False):
        self.file_path_format = file_path_format
        self.filter_tags = filter_tags
        self.inv_index = {}
        self.remove_stopwords = remove_stopwords
        self.case_sensitive = case_sensitive
        self.with_stemming = with_stemming

    def create_index_from_file_format(self):
        """Creates the Inverted Index for a file or multiple file of the same format
        For now, the score is just the frequency of the term in the document


        Usage for every file starting with la (outside of this module):
        inv_index = indexing.Index("../../../../Downloads/latimes/la*").create_index_from_file_format()

        Usage for a file
        inv_index = indexing.Index("../../../../Downloads/latimes/la010189").create_index_from_file_format()
		"""

        if self.file_path_format != "":
            #filling of the Inverted Index
            for filename in glob.glob(self.file_path_format):
                lines = open(filename, 'r')
                self.inv_index = self.create_index_from_text(lines)

        return self.inv_index

    # We had a pb in inv_index => if you execute the function two times in a row with default parameters, inv_index has a value the second time
    def create_index_from_text(self, text):
        """Creates the Inverted Index for a text

        Usage
        a = indexing.Index().create_index_from_text(textMultiline)
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
                # Extract the docid from the line : the first group in the regex (what's between parenthesis)
                doc_id = int(match.group(1))
                self.doc_id_list.append(doc_id)
            elif re.search(PATTERN_DOC_END, line) and doc != '' and doc_id != '':
                # If we reached the end of the document, insert tokens in hashmap and flush variables

                words = tokenization.TextFile.tokenize_string_split(doc, self.filter_tags, self.remove_stopwords, self.case_sensitive, self.with_stemming)

                # For the time being, we just calculate the frequency of each term and put it as the score
                # Avoid ZeroDivisionError
                if len(words) > 0:
                    score = 1.0/len(words)
                    for word in words:
                        if not word in self.inv_index:
                            self.inv_index[word] = {}
                        if not doc_id in self.inv_index[word]:
                            self.inv_index[word][doc_id] = score
                        else:
                            self.inv_index[word][doc_id] += score
                    # Flush variables before passing to the next document
                    doc = ''
                    del doc_id

        return self.inv_index


    def calculate_all_scores_memory(self):
        """Replaces the temporary score by the tf idf in each item of the index dictionnary"""

        for term,term_plist in self.inv_index.iteritems():
            for doc_id in self.inv_index[term]:
                self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(term_plist), len(self.doc_id_list))


    # DO NOT USE : impossible to know which terms the function has already been applied to
    def calculate_terms_in_query_scores_memory(self, query):
        """Replaces the temporary score by the tf idf in each item of the index dictionnary that's in the query"""

        for term in score.get_terms(query):
            #print list(self.inv_index.iteritems())
            print("Term query {}".format(term))

            if term in self.inv_index:
                print("Term in plist {}".format(term))
                term_plist = self.inv_index[term]
                for doc_id in term_plist:
                    self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(term_plist), len(self.doc_id_list))
