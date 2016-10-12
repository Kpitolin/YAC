import nltk, re, os, string
from os import listdir
from os.path import isfile, join
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()


def filter_punctuation(text):

    CHARACTERS_TO_KEEP = "-<>/"
    characters_to_remove = string.punctuation
    for ch in CHARACTERS_TO_KEEP:
        characters_to_remove = characters_to_remove.replace(ch,"")
    pattern = r"[{}]".format(characters_to_remove)
    return str(re.sub(pattern,"",text))

class TextFileList:
    """
    A class representing a list of textfiles as formatted in LATimes corpus

    Usage for tokenization of all files in folderpath:

    test_file_list = TextFileList.file_list_from_path("folderpath")
    print(test_file_list.tokenize_text_files_by_doc_split())
    """

    def __init__(self, filenames_list):
        self.filenames_list = filenames_list



    def tokenize_text_files_by_doc_nltk(self, without_tags=False):
            """ Extracts the words out of text files with NLTK word_tokenize method"""

            dictionnary_doc_words = {}

            for filepath in self.filenames_list:
                with open(filepath,'r') as raw_text:
                    dictionnary_doc_words = TextFile.tokenize_string_by_doc_nltk(raw_text, without_tags, dictionnary_doc_words)

            return dictionnary_doc_words

    def tokenize_text_files_by_doc_split(self, without_tags=False):
            """Extracts the words out of text files with split method"""
            dictionnary_doc_words = {}

            for filepath in self.filenames_list:
                with open(filepath,'r') as raw_text:
                    dictionnary_doc_words = TextFile.tokenize_string_by_doc_split(raw_text, without_tags, dictionnary_doc_words)

            return dictionnary_doc_words

    @classmethod
    def file_list_from_path(cls, folderpath):
        """http://stackoverflow.com/a/3207973
        Creates a TextFileList instance from a folderpath
        It enumerates the files in that folder (non-recursive)
		"""

        pattern_file_title =  r"la\d+"

        files = [join(folderpath, f) for f in listdir(folderpath) if isfile(join(folderpath, f)) and re.match(pattern_file_title, f)]
        return cls(files)

class TextFile:
    """A class representing a textfile as formatted in LATimes corpus

    Usage for tokenization of pathToFile:

    testFile = TextFile("pathToFile")
    print(testFile.tokenize_text_file_by_doc_nltk())
	"""

    def __init__(self, filepath):
        self.filepath = filepath # '../Downloads/latimes/la010189'

    def delete_file(self):
        try:
            os.remove(self.filepath)
        except OSError:
            print("File does not exist")

    def write(self, string_content):
        with open(self.filepath,'w') as text_file:
            return text_file.write(string_content)

    @staticmethod
    def tokenize_string_split(text, filter_tags=False, remove_stopwords=False, case_sensitive=False, with_stemming=False):
        tokens = []
        # Extract the tokens out of the raw text
        stop_words = stopwords.words('english')

        if not case_sensitive:
            text = text.lower()
        pattern_split = r'\s+'
        text = filter_punctuation(text)
        tokens = re.split(pattern_split,TextFile.filter_tags(text)) if filter_tags else re.split(pattern_split, text)
        tokens = list(filter(lambda item: item != "", tokens))
        words = [x for x in tokens if not remove_stopwords or x.lower() not in stop_words]
        terms = []
        if with_stemming:
            terms = [porter_stemmer.stem(word) for word in words]
        else:
            terms = words
            return tokens

    def tokenize_text_file_by_doc_nltk(self, without_tags=False):
        """Extracts the words out of a text file with NLTK word_tokenize method"""

        with open(self.filepath,'r') as raw_text:
            return TextFile.tokenize_string_by_doc_nltk(raw_text,without_tags)

        return {}



    def tokenize_text_file_by_doc_split(self, without_tags=False):
        """Extracts the words out of a text file with split method"""

        with open(self.filepath,'r') as raw_text:
            return TextFile.tokenize_string_by_doc_split(raw_text, without_tags)

        return {}


    @staticmethod
    def filter_tags(string):
        """Returns a string without tags"""

        doc = nltk.regexp_tokenize(string, r"</?[\w]+>", gaps=True)
        doc = list(map(lambda item: re.sub(r"(\n|\t)", "", item), doc))
        doc = list(filter(lambda item: item != "", doc))
        doc = "".join(doc)

        return doc

    # Execute nltk.download() to download corpora before executing that function
    @staticmethod
    def tokenize_string_by_doc_nltk(text, without_tags=False, dictionnary_doc_words={}):
        """Extracts the words out of a string
        Creates an hashmap <docId, listOfWords> for each document
        See http://www.nltk.org/howto/tokenize.html for more details on nltk.tokenize
		"""

        doc_word_list = []
        doc_id = ''
        lines = []

        # Textfile
        if hasattr(text, 'readlines'):
            lines = text
            # Multi-line string
        elif isinstance(text,str):
            lines = text.splitlines(False)

        for line in lines:

            line = filter_punctuation(line)
            # Extract the tokens out of the raw text
            tokens = nltk.word_tokenize(TextFile.filter_tags(line)) if without_tags else nltk.word_tokenize(line)
            doc_word_list += tokens
            pattern_doc_id = r"<DOCID>\s(\d+)\s</DOCID>"
            pattern_doc_end = r"</DOC>"

            match = re.search(pattern_doc_id, line)
            if match:
                # Extract the docid from the line : the first group in the regex (what's between parenthesis)
                doc_id = int(match.group(1))

            elif re.search(pattern_doc_end, line) and doc_word_list != [] and doc_id != '':
                # If we reached the end of the document, insert tokens in hashmap and flush variables
                dictionnary_doc_words[doc_id] = doc_word_list
                doc_word_list = []
                del doc_id

        return dictionnary_doc_words


    @staticmethod
    def tokenize_string_by_doc_split(text, without_tags=False, dictionnary_doc_words={}):
        """Extracts the words out of a string
        Creates an hashmap <docId, listOfWords> for each document
        See https://docs.python.org/2/library/re.html#re.split for more details on re.split
		"""

        doc_word_list = []
        doc_id = ''
        lines = []

        # Textfile
        if hasattr(text, 'readlines'):
            lines = text
        # Multi-line string
        elif isinstance(text,str):
            lines = text.splitlines(False)

        for line in lines:

            line = filter_punctuation(line)
            # Extract the tokens out of the raw text
            pattern_split = r'\s+'
            tokens = re.split(pattern_split,TextFile.filter_tags(line)) if without_tags else re.split(pattern_split, line)
            tokens = list(filter(lambda item: item != "", tokens))
            doc_word_list += tokens
            pattern_doc_id = r"<DOCID>\s(\d+)\s</DOCID>"
            pattern_doc_end = r"</DOC>"

            match = re.search(pattern_doc_id, line)
            if match:
                # Extract the docid from the line : the first group in the regex (what's between parenthesis)
                doc_id = int(match.group(1))

            elif re.search(pattern_doc_end, line) and doc_word_list != [] and doc_id != '':
                # If we reached the end of the document, insert tokens in hashmap and flush variables
                dictionnary_doc_words[doc_id] = doc_word_list
                doc_word_list = []
                del doc_id

        return dictionnary_doc_words

    @classmethod
    def new_file(cls, filepath):
        file = open(filepath,'w')
        file.close()
        return cls(filepath)
