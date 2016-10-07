import unittest
from context import tokenization


# Just execute the script to run the tests for now (see the two last lines)
class TokenizationTestCase(unittest.TestCase):
	def setUp(self):
		self.emptyFile = tokenization.TextFile.new_file("emptyTest.txt")

	# Filter test cases
	def test_filterTags_empty(self):
		self.assertEqual(tokenization.TextFile.filterTags(""), "")

	def test_filterTags_normal(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.filterTags(stringNormalOneDoc), " 1 The onset of the new Gorbachev")

	def test_filterTags_no_break_lines(self):

		stringNormalOneDoc = ("<DOC>"
		"<DOCID> 1 </DOCID>"
		"The onset of the new Gorbachev"
		"</DOC>")
		self.assertEqual(tokenization.TextFile.filterTags(stringNormalOneDoc), " 1 The onset of the new Gorbachev")


	#Tokenize test cases (NLTK)
	def test_tokenize_nltk_nltk_file_notFound(self):
		textFileNF = tokenization.TextFile("")
		with self.assertRaises(IOError):
			textFileNF.tokenizeTextFileByDocNltk()


	def test_tokenize_nltk_file_empty(self):
		self.assertEqual(self.emptyFile.tokenizeTextFileByDocNltk(),{})

	def test_tokenize_nltk_one_document_string_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk(stringNormalOneDoc),{1: ['<', 'DOC', '>', '<', 'DOCID', '>', '1', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>']})

	def test_tokenize_nltk_two_documents_string_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk(stringNormalOneDoc),{1: ['<', 'DOC', '>', '<', 'DOCID', '>', '1', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>'], 2: ['<', 'DOC', '>', '<', 'DOCID', '>', '2', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>']})


	def test_tokenize_nltk_one_document_string_normal_no_special_characters_without_tags(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk(stringNormalOneDoc,True),{1: ['1','The', 'onset', 'of', 'the', 'new', 'Gorbachev']})

	def test_tokenize_nltk_two_documents_string_normal_no_special_characters_without_tags(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk(stringNormalOneDoc,True),{1: ['1','The', 'onset', 'of', 'the', 'new', 'Gorbachev'], 2: ['2','The', 'onset', 'of', 'the', 'new', 'Gorbachev']})


	def test_tokenize_nltk_one_document_file_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		tFile = tokenization.TextFile.new_file("stringNormalOneDoc")
		tFile.write(stringNormalOneDoc)
		self.assertEqual(tFile.tokenizeTextFileByDocNltk(),{1: ['<', 'DOC', '>', '<', 'DOCID', '>', '1', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>']})
		tFile.deleteFile()
		
	#def test_tokenize_nltk_one_document_without_doc_tag_start(self):
	#	self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})
	#def test_tokenize_nltk_one_document_without_doc_tag_end(self):
	#	self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})
	#def test_tokenize_nltk_one_document_without_doc_tags(self):
	#	self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})

	#def test_tokenize_nltk_without_docno_tag_start(self):
	#	self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})
	#def test_tokenize_nltk_without_docno_tag_end(self):
	#	self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})
	#def test_tokenize_nltk_without_docno_tags(self):
	#	self.assertEqual(tokenization.TextFile.tokenizeStringByDocNltk('emptyFile'),{"":""})

	#Tokenize test cases (Split)
	def test_tokenize_split_two_documents_string_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenizeStringByDocSplit(stringNormalOneDoc),{1: ['<DOC>', '<DOCID>', '1', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>'], 2: ['<DOC>', '<DOCID>', '2', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>']})


	def test_tokenize_split_two_documents_string_normal_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		The onset of the new Gorbachev!
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenizeStringByDocSplit(stringNormalOneDoc),{1: ['<DOC>', '<DOCID>', '1', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>'], 2: ['<DOC>', '<DOCID>', '2', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>']})


	def test_tokenize_string_split_one_doc(self):

		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>
		"""
		self.assertEqual(tokenization.TextFile.tokenizeStringSplit(stringNormalOneDoc), ['<DOC>', '<DOCID>', '1', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>'])


	def tearDown(self):
		self.emptyFile.deleteFile()

if __name__=='__main__':
	unittest.main()
