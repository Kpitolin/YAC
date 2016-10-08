import unittest
from context import indexing


# Just execute the script to run the tests for now (see the two last lines)
class TokenizationTestCase(unittest.TestCase):
	#def setUp(self):

	#Indexing tests cases
	def test_indexing_string_split_one_doc(self):

		stringNormalOneDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(indexing.Index().createIndexFromText(stringNormalOneDoc), {"<DOCID>":{1:1.0/11}, "</DOCID>":{1:1.0/11},  "<DOC>":{1:1.0/11}, "</DOC>": {1:1.0/11},"1": {1:1.0/11}, "The": {1:1.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "the":{1:1.0/11}, "new":{1:1.0/11},"Gorbachev":{1:1.0/11}})
	

	def test_indexing_string_split_two_docs(self):

		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of the new Gorbachev
		</DOC>"""
		self.assertEqual(indexing.Index().createIndexFromText(stringNormalDoc), { "<DOCID>":{1:1.0/11, 2:1.0/11}, "</DOCID>":{1:1.0/11, 2:1.0/11},  "<DOC>":{1:1.0/11, 2:1.0/11}, "</DOC>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "The": {1:1.0/11}, "the": {2:1.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "the":{1:1.0/11, 2:2.0/11}, "new":{1:1.0/11, 2:1.0/11},"Gorbachev":{1:1.0/11, 2:1.0/11}})


	def test_indexing_string_split_two_docs_special_characters(self):

		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""
		self.assertEqual(indexing.Index().createIndexFromText(stringNormalDoc), { "<DOCID>":{1:1.0/11, 2:1.0/11}, "</DOCID>":{1:1.0/11, 2:1.0/11},  "<DOC>":{1:1.0/11, 2:1.0/11}, "</DOC>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "The": {1:1.0/11}, "the": {2:1.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "the":{1:1.0/11, 2:2.0/11}, "new":{1:1.0/11, 2:1.0/11},"Gorbachev":{1:1.0/11, 2:1.0/11}})

	#def tearDown(self):

if __name__=='__main__':
	unittest.main()