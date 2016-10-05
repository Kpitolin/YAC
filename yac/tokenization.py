import nltk, re, os

class TextFile:
	"""
	A class representing a textfile as formatted in LATimes corpus

	Usage for tokenization of pathToFile:

	testFile = TextFile("pathToFile")
	print(testFile.tokenizeTextFileByDocNltk())
	"""
	def __init__(self, filepath):
		self.filepath = filepath # '../Downloads/latimes/la010189'

	def deleteFile(self):
		try:
			os.remove(self.filepath)
		except OSError:
			print("File does not exist")

	def write(self, stringContent):
		with open(self.filepath,'w') as text_file:
			return text_file.write(stringContent)

	def tokenizeTextFileByDocNltk(self,without_tags=False):
		""" Extracts the words out of a text file
		"""

		with open(self.filepath,'r') as raw_text:
			return TextFile.tokenizeStringByDocNltk(raw_text,without_tags)

		return {}

	@staticmethod
	def filterTags(string):
		"""Returns a string without tags
		"""
	
		doc = nltk.regexp_tokenize(string, r"</?[\w]+>", gaps=True)
		doc = list(map(lambda item: re.sub(r"(\n|\t)", "", item), doc))
		doc = list(filter(lambda item: item != "", doc))
		doc = "".join(doc)

		return doc

	# execute nltk.download() to download corpora before executing that function
	@staticmethod
	def tokenizeStringByDocNltk(text, without_tags=False):
		""" Extracts the words out of a string
			Creates an hashmap <docId, listOfWords> for each document 
			See http://www.nltk.org/howto/tokenize.html for more details on nltk.tokenize
		"""
		dictionnary_doc_words = {}
		doc_word_list = []
		doc_id = ''
		lines = []

		#textfile
		if hasattr(text, 'readlines'):
			lines = text
			#multi-line string 
		elif isinstance(text,str):
			lines = text.splitlines(False)

		for line in lines:

			#extract the tokens out of the raw text
			#replace word_tokenize with re.split see https://docs.python.org/2/library/re.html#re.split
			tokens = nltk.word_tokenize(TextFile.filterTags(line)) if without_tags else nltk.word_tokenize(line)
			doc_word_list += tokens
			pattern_doc_id = r"<DOCID>\s(\d+)\s</DOCID>"
			pattern_doc_end = r"</DOC>"

			match = re.search(pattern_doc_id, line)
			if match:
				#extract the docid from the line : the first group in the regex (what's between parenthesis)
				doc_id = int(match.group(1))

			elif re.search(pattern_doc_end, line) and doc_word_list != [] and doc_id != '':
				#if we reached the end of the document, insert tokens in hashmap and flush variables
				dictionnary_doc_words[doc_id] = doc_word_list
				doc_word_list = []
				del doc_id

		return dictionnary_doc_words

	@classmethod
	def new_file(cls,filepath):
		file = open(filepath,'w')
		file.close()
		return cls(filepath)
