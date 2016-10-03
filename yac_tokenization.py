import nltk, unittest, re, os

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

	def tokenizeTextFileByDocNltk(self):
		""" Extracts the words out of a text file
		"""

		with open(self.filepath,'r') as raw_text:
			return TextFile.tokenizeStringByDocNltk(raw_text)

		return {}

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
		lines = ""

		#textfile
		if hasattr(text, 'readlines'):
			lines = text
		#multi-line string 
		elif isinstance(text,str):
			lines = text.splitlines(False)

		for line in lines:
			#extract the tokens out of the raw text
			if without_tags:
				tokens = TextFile.filterTags(line)
				tokens = nltk.word_tokenize(tokens)
			else:
				tokens = nltk.word_tokenize(line)


			doc_word_list += tokens
			pattern_doc_id = r"<DOCID>\s(\d)+\s</DOCID>"
			pattern_doc_end = r"</DOC>"

			match = re.search(pattern_doc_id, line)
			if match:
				#extract the docid from the line : the first group in the regex (what's between parenthesis)
				doc_id = int(match.group(1))

			elif re.search(pattern_doc_end, line) and doc_word_list != [] and doc_id != '':
				#if we reached the end of the document, insert tokens in hashmap and flush variables
				dictionnary_doc_words[doc_id] = doc_word_list
				del doc_word_list
				del doc_id

		return dictionnary_doc_words

	@staticmethod
	def filterTags(string):
		"""Returns a string without tags"""
	
		doc = nltk.regexp_tokenize(string, r"</?[\w]+>", gaps=True)
		doc = list(map(lambda item: re.sub(r"(\n|\t)", "", item), doc))
		doc = list(filter(lambda item: item != "", doc))
		doc = "".join(doc)

		return doc

	@classmethod
	def new_file(cls,filepath):
		file = open(filepath,'w')
		file.close()
		return cls(filepath)





# Just execute the script to run the tests for now (see the two last lines)
class TokenizationTestCase(unittest.TestCase):
	def setUp(self):
		self.textFileNF = TextFile("")
		self.emptyFile = TextFile.new_file("emptyTest.txt")


	def test_tokenize_file_notFound(self):
		with self.assertRaises(IOError):
			self.textFileNF.tokenizeTextFileByDocNltk()

	def test_filterTags_empty(self):
		self.assertEqual(TextFile.filterTags(""), "")

	def test_filterTags_normal(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(TextFile.filterTags(stringNormalOneDoc), " 1 The onset of the new Gorbachev")

	def test_filterTags_no_break_lines(self):

		stringNormalOneDoc = ("<DOC>"
		"<DOCID> 1 </DOCID>"
		"The onset of the new Gorbachev"
		"</DOC>")
		self.assertEqual(TextFile.filterTags(stringNormalOneDoc), " 1 The onset of the new Gorbachev")

	def test_tokenize_file_empty(self):
		self.assertEqual(self.emptyFile.tokenizeTextFileByDocNltk(),{})

	def test_tokenize_one_document_string_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(TextFile.tokenizeStringByDocNltk(stringNormalOneDoc),{1: ['<', 'DOC', '>', '<', 'DOCID', '>', '1', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>']})

	def test_tokenize_one_document_string_normal_no_special_characters_without_tags(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(TextFile.tokenizeStringByDocNltk(stringNormalOneDoc,True),{1: ['1','The', 'onset', 'of', 'the', 'new', 'Gorbachev']})



	def test_tokenize_one_document_file_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		testFile = TextFile.new_file("stringNormalOneDoc")
		testFile.write(stringNormalOneDoc)
		self.assertEqual(testFile.tokenizeTextFileByDocNltk(),{1: ['<', 'DOC', '>', '<', 'DOCID', '>', '1', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>']})
		testFile.deleteFile()
		
	#def test_tokenize_one_document_without_doc_tag_start(self):
	#	self.assertEqual(TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})
	#def test_tokenize_one_document_without_doc_tag_end(self):
	#	self.assertEqual(TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})
	#def test_tokenize_one_document_without_doc_tags(self):
	#	self.assertEqual(TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})

	#def test_tokenize_without_docno_tag_start(self):
	#	self.assertEqual(TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})
	#def test_tokenize_without_docno_tag_end(self):
	#	self.assertEqual(TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})
	#def test_tokenize_without_docno_tags(self):
	#	self.assertEqual(TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})

	def tearDown(self):
		self.emptyFile.deleteFile()



if __name__=='__main__':
	unittest.main()

