import unittest, os
from os import listdir
from os.path import isfile, join
from context import indexing
import math
import re


class IndexingTestCase(unittest.TestCase):

	@property
	def index(self):
		return self._index
	@index.setter
	def index(self, value):
		self._index = value


	def read_file(self,filename):
		with open(filename, "r") as f:
			return f.read()

	def delete_file(self,filepath):
		if isfile(filepath):
			try:
				os.remove(filepath)
			except OSError:
				print("An error occured deleting file {}".format(filepath))


	def setUp(self):
		self._index = indexing.Index()


	def tearDown(self):
		folderpath= "."
		pattern_file_title =  r"fileIndex*"
		files = [join(folderpath, f) for f in listdir(folderpath) if isfile(join(folderpath, f)) and re.match(pattern_file_title, f)]
		for filename in files:
			self.delete_file(filename)
		self._index = None

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
		index._doc_id_list = [1]
		index.inv_index = initialIndex
		index.calculate_all_scores_memory()
		self.assertEqual(index.inv_index, resultedIndex)
	
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
		index._doc_id_list = [1,2]
		index.inv_index = {"<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:1.0/11, 2:1.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "the":{1:1.0/11, 2:2.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}}
		index.calculate_all_scores_memory()
		self.assertEqual(index.inv_index, resultedIndex)


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
		self.assertEqual( index.create_index_merged_based_from_text(stringNormalDoc) , resultedIndex)


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
		self.assertEqual( index.create_index_merged_based_from_text(stringNormalDoc) , resultedIndex)


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
		partialIndex = index.create_index_merged_based_from_text(stringNormalDoc) 
		self.assertEqual(partialIndex, resultedIndex)


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
		self._index._doc_limit = 0
		self.assertEqual(self._index.create_index_merged_based_from_text(stringNormalDoc), resultedIndex)


	def test_create_index_merged_based_all_docs_with_save(self):
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

		index._doc_limit = 1
		partial_index = index.create_index_merged_based_from_text(stringNormalDoc)
		self.assertNotEqual(index._pl_file_list, [])
		resultingTextFile = "1\n1,0.0909090909091;\n</doc>\n1,0.0909090909091;\n</docid>\n1,0.0909090909091;\n<doc>\n1,0.0909090909091;\n<docid>\n1,0.0909090909091;\ngorbachev\n1,0.0909090909091;\nnew\n1,0.0909090909091;\nof\n1,0.0909090909091;\nonset\n1,0.0909090909091;\nthe\n1,0.181818181818;\n"
		self.assertEqual(self.read_file(index._pl_file_list[0]), resultingTextFile)


	def test_save_index_to_file_zero_doc(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""

		self._index.inv_index = {}
		self._index.save_index_to_file()
		self.assertEqual(self._index._pl_file_list, [])

	def test_save_index_to_file_one_doc(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>"""

		resultedIndex = { "<docid>":[(1,1.0/11)], "</docid>":[(1,1.0/11)],  "<doc>":[(1,1.0/11)], "</doc>": [(1,1.0/11)], "1": [(1,1.0/11)], "the": [(1,2.0/11)], "onset": [(1,1.0/11)], "of":[(1,1.0/11)], "new":[(1,1.0/11)],"gorbachev":[(1,1.0/11)]}
		self._index.inv_index = resultedIndex		
		self._index.save_index_to_file()
		resultingTextFile = "1\n1,0.0909090909091;\n</doc>\n1,0.0909090909091;\n</docid>\n1,0.0909090909091;\n<doc>\n1,0.0909090909091;\n<docid>\n1,0.0909090909091;\ngorbachev\n1,0.0909090909091;\nnew\n1,0.0909090909091;\nof\n1,0.0909090909091;\nonset\n1,0.0909090909091;\nthe\n1,0.181818181818;\n"
		self.assertEqual(self.read_file(self._index._pl_file_list[0]), resultingTextFile)
		
	def test_save_index_to_file_two_doc(self):
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
		self._index.inv_index = resultedIndex		
		self._index.save_index_to_file()
		resultingTextFile = "1\n1,0.0909090909091;\n2\n2,0.0909090909091;\n</doc>\n1,0.0909090909091;2,0.0909090909091;\n</docid>\n1,0.0909090909091;2,0.0909090909091;\n<doc>\n1,0.0909090909091;2,0.0909090909091;\n<docid>\n1,0.0909090909091;2,0.0909090909091;\ngorbachev\n1,0.0909090909091;2,0.0909090909091;\nnew\n1,0.0909090909091;2,0.0909090909091;\nof\n1,0.0909090909091;2,0.0909090909091;\nonset\n1,0.0909090909091;2,0.0909090909091;\nthe\n1,0.181818181818;2,0.181818181818;\n"
		self.assertEqual(self.read_file(self._index._pl_file_list[0]), resultingTextFile)

	def test_read_terms_from_i_file_empty(self):
		with open('fileIndexTest1', "w") as ifile:
			ifile.write("  ")
		with open('fileIndexTest1', "r") as ifile:
			self.assertFalse(self._index.read_terms_from_i_file(ifile, "fileIndexTest1"))

	def test_read_terms_from_i_file_one_term(self):
		with open('fileIndexTest2', "w") as ifile:
			ifile.write("</doc>")
		with open('fileIndexTest2', "r") as ifile:
			self.assertTrue(self._index.read_terms_from_i_file(ifile, "fileIndexTest2"))

	def test_read_terms_from_i_file_one_term_one_pl(self):
		with open('fileIndexTest3', "w") as ifile:
			ifile.write("term" + "\n")
			ifile.write("posting List" + "\n")
		with open('fileIndexTest3', "r") as ifile:
			self.assertTrue(self._index.read_terms_from_i_file(ifile, "fileIndexTest3"))


	def test_read_terms_from_i_file_one_term_reached_end(self):
		with open('fileIndexTest4', "w") as ifile:
			ifile.write("term" + "\n")
			ifile.write("posting List" + "\n")
		with open('fileIndexTest4', "r") as ifile:
			self._index.read_terms_from_i_file(ifile, "fileIndexTest4")
			self.assertFalse(self._index.read_terms_from_i_file(ifile, "fileIndexTest4"))



if __name__=='__main__':
	unittest.main()