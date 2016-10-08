import unittest
from context import indexing
import math


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

	def test_calculate_all_scores_memory_one_doc(self):
		stringNormalOneDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""

		index = indexing.Index()
		index.doc_id_list = [1]
		index.inv_index = {"<DOCID>":{1:1.0/11}, "</DOCID>":{1:1.0/11},  "<DOC>":{1:1.0/11}, "</DOC>": {1:1.0/11},"1": {1:1.0/11}, "The": {1:1.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "the":{1:1.0/11}, "new":{1:1.0/11},"Gorbachev":{1:1.0/11}}
		index.calculate_all_scores_memory()
		self.assertEqual(index.inv_index, {"<DOCID>":{1:0}, "</DOCID>":{1:0},  "<DOC>":{1:0}, "</DOC>": {1:0},"1": {1:0}, "The": {1:0}, "onset": {1:0}, "of":{1:0}, "the":{1:0}, "new":{1:0},"Gorbachev":{1:0}})
	

	def test_calculate_all_scores_memory_two_doc(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""

		index = indexing.Index()
		index.doc_id_list = [1,2]
		index.inv_index = { "<DOCID>":{1:1.0/11, 2:1.0/11}, "</DOCID>":{1:1.0/11, 2:1.0/11},  "<DOC>":{1:1.0/11, 2:1.0/11}, "</DOC>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "The": {1:1.0/11}, "the": {2:1.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "the":{1:1.0/11, 2:2.0/11}, "new":{1:1.0/11, 2:1.0/11},"Gorbachev":{1:1.0/11, 2:1.0/11}}
		index.calculate_all_scores_memory()
		self.assertEqual(index.inv_index, { "<DOCID>":{1:0, 2:0}, "</DOCID>":{1:0, 2:0},  "<DOC>":{1:0, 2:0}, "</DOC>": {1:0, 2:0}, "1": {1:1.0/11*math.log10(2)}, "2": {2:1.0/11*math.log10(2)}, "The": {1:1.0/11*math.log10(2)}, "the": {2:0}, "onset": {1:0, 2:0}, "of":{1:0, 2:0}, "the":{1:0, 2:0}, "new":{1:0, 2:0},"Gorbachev":{1:0, 2:0}})
	

	#def tearDown(self):

if __name__=='__main__':
	unittest.main()