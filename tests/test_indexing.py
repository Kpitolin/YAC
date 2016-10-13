import unittest
from context import indexing
import math


class IndexingTestCase(unittest.TestCase):
	#def setUp(self):

	#Indexing tests cases
	def test_indexing_string_split_one_doc(self):

		string_normal_one_doc = """
		<DOC>
		<DOCID> 1 </DOCID>
		the onset of the new gorbachev
		</DOC>"""
		self.assertEqual(indexing.Index().create_index_from_text(string_normal_one_doc), {"<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11},"1": {1:1.0/11}, "the": {1:2.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:1.0/11},"gorbachev":{1:1.0/11}})
	

	def test_indexing_string_split_two_docs(self):

		string_normal_doc = """
		<DOC>
		<DOCID> 1 </DOCID>
		the onset of the new gorbachev
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of the new gorbachev
		</DOC>"""
		self.assertEqual(indexing.Index().create_index_from_text(string_normal_doc), { "<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:2.0/11,2:2.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}})


	def test_indexing_string_split_two_docs_special_characters(self):

		string_normal_doc = """
		<DOC>
		<DOCID> 1 </DOCID>
		the onset of "the new gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new gorbachev"!
		</DOC>"""
		self.assertEqual(indexing.Index().create_index_from_text(string_normal_doc), { "<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:2.0/11,2:2.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}})

	def test_calculate_all_scores_memory_one_doc(self):
		string_normal_one_doc = """
		<DOC>
		<DOCID> 1 </DOCID>
		the onset of the new gorbachev
		</DOC>"""

		index = indexing.Index()
		index.doc_id_list = [1]
		index.inv_index = {"<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11},"1": {1:1.0/11}, "the": {1:2.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:1.0/11},"gorbachev":{1:1.0/11}}
		index.calculate_all_scores_memory()
		self.assertEqual(index.inv_index, {"<docid>":{1:0}, "</docid>":{1:0},  "<doc>":{1:0}, "</doc>": {1:0},"1": {1:0}, "the": {1:0}, "onset": {1:0}, "of":{1:0}, "new":{1:0},"gorbachev":{1:0}})
	

	def test_calculate_terms_in_query_scores_memory_one_doc(self):
		string_normal_one_doc = """
		<DOC>
		<DOCID> 1 </DOCID>
		the onset of the new gorbachev
		</DOC>"""

		query = "the new Gorbachev"

		index = indexing.Index()
		index.doc_id_list = [1]
		index.inv_index = {"<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11},"1": {1:1.0/11}, "the": {1:2.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:1.0/11},"gorbachev":{1:1.0/11}}
		index.calculate_terms_in_query_scores_memory(query)
		self.assertEqual(index.inv_index, {"<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11},"1": {1:1.0/11}, "the": {1:0}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:0},"gorbachev":{1:0}})
	

	def test_calculate_all_scores_memory_two_doc(self):
		string_normal_doc = """
		<DOC>
		<DOCID> 1 </DOCID>
		the onset of "the new gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new gorbachev"!
		</DOC>"""

		index = indexing.Index()
		index.doc_id_list = [1,2]
		index.inv_index = {"<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:2.0/11, 2:2.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}}
		index.calculate_all_scores_memory()
		self.assertEqual(index.inv_index, { "<docid>":{1:0, 2:0}, "</docid>":{1:0, 2:0},  "<doc>":{1:0, 2:0}, "</doc>": {1:0, 2:0}, "1": {1:1.0/11*math.log10(2)}, "2": {2:1.0/11*math.log10(2)}, "the": {1:0, 2:0}, "onset": {1:0, 2:0}, "of":{1:0, 2:0}, "new":{1:0, 2:0},"gorbachev":{1:0, 2:0}})
	

	#def tearDown(self):

if __name__=='__main__':
	unittest.main()