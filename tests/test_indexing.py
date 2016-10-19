import unittest
from context import indexing
import math


class IndexingTestCase(unittest.TestCase):
	#def setUp(self):

	#Indexing tests cases
	def test_indexing_string_split_one_doc(self):

		stringNormalOneDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""

		resultedIndex = {"<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11},"1": {1:1.0/11}, "the": {1:2.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:1.0/11},"gorbachev":{1:1.0/11}}
	
		self.assertEqual(indexing.Index().createIndexFromText(stringNormalOneDoc), resultedIndex)
	

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

		resultedIndex = { "<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:2.0/11, 2:2.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}}

		self.assertEqual(indexing.Index().createIndexFromText(stringNormalDoc), resultedIndex)


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

		resultedIndex =  { "<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the":{1:2.0/11, 2:2.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}}
		self.assertEqual(indexing.Index().createIndexFromText(stringNormalDoc), resultedIndex)

	def test_calculate_all_scores_memory_one_doc(self):
		stringNormalOneDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		initialIndex =  { "<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11}, "1": {1:1.0/11}, "the":{1:2.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:1.0/11},"gorbachev":{1:1.0/11}}

		resultedIndex = {"<docid>":{1:0}, "</docid>":{1:0},  "<doc>":{1:0}, "</doc>": {1:0},"1": {1:0}, "onset": {1:0}, "of":{1:0}, "the":{1:0}, "new":{1:0},"gorbachev":{1:0}}

		index = indexing.Index()
		index.doc_id_list = [1]
		index.inv_index = initialIndex
		index.calculate_all_scores_memory()
		self.assertEqual(index.inv_index, resultedIndex)
		del index
	
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

		resultedIndex = { "<docid>":{1:0, 2:0}, "</docid>":{1:0, 2:0},  "<doc>":{1:0, 2:0}, "</doc>": {1:0, 2:0}, "1": {1:1.0/11*math.log10(2)}, "2": {2:1.0/11*math.log10(2)}, "onset": {1:0, 2:0}, "of":{1:0, 2:0}, "the":{1:0, 2:0}, "new":{1:0, 2:0},"gorbachev":{1:0, 2:0}}

		index = indexing.Index()
		index.doc_id_list = [1,2]
		index.inv_index = {"<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:1.0/11, 2:1.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "the":{1:1.0/11, 2:2.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}}
		index.calculate_all_scores_memory()
		self.assertEqual(index.inv_index, resultedIndex)
		del index


	def test_create_index_merged_based_all_docs(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""

		resultedIndex = { "<docid>":[(1,1.0/11), (2,1.0/11)], "</docid>":[(1,1.0/11), (2,1.0/11)],  "<doc>":[(1,1.0/11), (2,1.0/11)], "</doc>": [(1,1.0/11), (2,1.0/11)], "1": [(1,1.0/11)], "2": [(2,1.0/11)], "the": [(1,2.0/11), (2,2.0/11)], "onset": [(1,1.0/11), (2,1.0/11)], "of":[(1,1.0/11), (2,1.0/11)], "new":[(1,1.0/11), (2,1.0/11)],"gorbachev":[(1,1.0/11), (2,1.0/11)]}

		index = indexing.Index() 
		index._doc_limit = 2
		self.assertEqual( index.createIndexMergedBasedFromText(stringNormalDoc) , resultedIndex)
		del index


	def test_create_index_merged_based_limit_one_doc(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""

		resultedIndex = { "<docid>":[(1,1.0/11)], "</docid>":[(1,1.0/11)],  "<doc>":[(1,1.0/11)], "</doc>": [(1,1.0/11)], "1": [(1,1.0/11)], "the": [(1,2.0/11)], "onset": [(1,1.0/11)], "of":[(1,1.0/11)], "new":[(1,1.0/11)],"gorbachev":[(1,1.0/11)]}

		index = indexing.Index() 
		index._doc_limit = 1
		self.assertEqual( index.createIndexMergedBasedFromText(stringNormalDoc) , resultedIndex)
		del index


	def test_create_index_merged_based_limit_one_doc_from_second_doc(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""

		resultedIndex = { "<docid>":[(2,1.0/11)], "</docid>":[(2,1.0/11)],  "<doc>":[(2,1.0/11)], "</doc>": [(2,1.0/11)], "2": [(2,1.0/11)], "the": [(2,2.0/11)], "onset": [(2,1.0/11)], "of":[(2,1.0/11)], "new":[(2,1.0/11)],"gorbachev":[(2,1.0/11)]}

		index = indexing.Index() 
		index._current_doc_index = 2
		index._doc_limit = 1
		partialIndex = index.createIndexMergedBasedFromText(stringNormalDoc) 
		self.assertEqual(partialIndex, resultedIndex)
		del index


	def test_create_index_merged_based_limit_zero_doc(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""

		resultedIndex = {}

		index = indexing.Index() 
		index._doc_limit = 0
		self.assertEqual( index.createIndexMergedBasedFromText(stringNormalDoc) , resultedIndex)
		del index


	#def tearDown(self):

if __name__=='__main__':
	unittest.main()