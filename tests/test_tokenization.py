import unittest
from context import tokenization


# Just execute the script to run the tests for now (see the two last lines)
class TokenizationTestCase(unittest.TestCase):
	def setUp(self):
		self.emptyFile = tokenization.TextFile.new_file("emptyTest.txt")

	# Filter test cases
	def test_filter_tags_empty(self):
		self.assertEqual(tokenization.TextFile.filter_tags(""), "")

	def test_filter_tags_normal(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.filter_tags(stringNormalOneDoc), " 1 The onset of the new Gorbachev")

	def test_filter_tags_no_break_lines(self):

		stringNormalOneDoc = ("<DOC>"
		"<DOCID> 1 </DOCID>"
		"The onset of the new Gorbachev"
		"</DOC>")
		self.assertEqual(tokenization.TextFile.filter_tags(stringNormalOneDoc), " 1 The onset of the new Gorbachev")


	#Tokenize test cases (NLTK)
	def test_tokenize_nltk_nltk_file_notFound(self):
		textFileNF = tokenization.TextFile("")
		with self.assertRaises(IOError):
			textFileNF.tokenize_text_file_by_doc_nltk()


	def test_tokenize_nltk_file_empty(self):
		self.assertEqual(self.emptyFile.tokenize_text_file_by_doc_nltk(),{})

	def test_tokenize_nltk_one_document_string_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenize_string_by_doc_nltk(stringNormalOneDoc),{1: ['<', 'DOC', '>', '<', 'DOCID', '>', '1', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>']})

	def test_tokenize_nltk_two_documents_string_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenize_string_by_doc_nltk(stringNormalOneDoc),{1: ['<', 'DOC', '>', '<', 'DOCID', '>', '1', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>'], 2: ['<', 'DOC', '>', '<', 'DOCID', '>', '2', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>']})


	def test_tokenize_nltk_one_document_string_normal_no_special_characters_without_tags(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenize_string_by_doc_nltk(stringNormalOneDoc,True),{1: ['1','The', 'onset', 'of', 'the', 'new', 'Gorbachev']})

	def test_tokenize_nltk_two_documents_string_normal_no_special_characters_without_tags(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenize_string_by_doc_nltk(stringNormalOneDoc,True),{1: ['1','The', 'onset', 'of', 'the', 'new', 'Gorbachev'], 2: ['2','The', 'onset', 'of', 'the', 'new', 'Gorbachev']})


	def test_tokenize_nltk_one_document_file_normal_no_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		tFile = tokenization.TextFile.new_file("stringNormalOneDoc")
		tFile.write(stringNormalOneDoc)
		self.assertEqual(tFile.tokenize_text_file_by_doc_nltk(),{1: ['<', 'DOC', '>', '<', 'DOCID', '>', '1', '<', '/DOCID', '>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '<', '/DOC', '>']})
		tFile.delete_file()
		

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
		self.assertEqual(tokenization.TextFile.tokenize_string_by_doc_split(stringNormalOneDoc),{1: ['<DOC>', '<DOCID>', '1', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>'], 2: ['<DOC>', '<DOCID>', '2', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>']})

	def test_tokenize_split_two_documents_string_normal_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenize_string_by_doc_split(stringNormalOneDoc),{1: ['<DOC>', '<DOCID>', '1', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>'], 2: ['<DOC>', '<DOCID>', '2', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>']})


	def test_tokenize_split_two_documents_string_normal_special_characters(self):
		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		The onset of the new Gorbachev!
		</DOC>"""
		self.assertEqual(tokenization.TextFile.tokenize_string_by_doc_split(stringNormalOneDoc),{1: ['<DOC>', '<DOCID>', '1', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>'], 2: ['<DOC>', '<DOCID>', '2', '</DOCID>', 'The', 'onset', 'of', 'the', 'new', 'Gorbachev', '</DOC>']})


	def test_tokenize_string_split_one_doc_no_special_characters(self):

		stringNormalOneDoc = """<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>
		"""
		self.assertEqual(tokenization.TextFile.tokenize_string_split(stringNormalOneDoc), ['<doc>', '<docid>', '1', '</docid>', 'the', 'onset', 'of', 'the', 'new', 'gorbachev', '</doc>'])


	def tearDown(self):
		self.emptyFile.delete_file()

if __name__=='__main__':
	unittest.main()
