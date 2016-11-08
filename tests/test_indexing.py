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
		pattern_file_title =  r"(partialIndex*|InvertedFile|Offsets)"
		files = [join(folderpath, f) for f in listdir(folderpath) if isfile(join(folderpath, f)) and re.match(pattern_file_title, f)]
		for filename in files:
			self.delete_file(filename)
		self._index = None

	#Indexing tests cases
	def test_indexing_string_memory_one_doc(self):

		stringNormalOneDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""

		resultedIndex = {"<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11},"1": {1:1.0/11}, "the": {1:2.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:1.0/11},"gorbachev":{1:1.0/11}}
		self._index.index_documents(stringNormalOneDoc)
		self.assertEqual(self._index._partial_files_names, [])
		self.assertEqual(self._index.inv_index, resultedIndex)
		

	def test_indexing_string_memory_two_docs(self):

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
		self._index.index_documents(stringNormalDoc)
		self.assertEqual(self._index._partial_files_names, [])
		self.assertEqual(self._index.inv_index, resultedIndex)


	def test_indexing_string_memory_two_docs_special_characters(self):

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
		self._index.index_documents(stringNormalDoc)
		self.assertEqual(self._index.inv_index, resultedIndex)

	def test_update_scores_with_idf_one_doc(self):
		stringNormalOneDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of the new Gorbachev
		</DOC>"""
		initialIndex =  { "<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11}, "1": {1:1.0/11}, "the":{1:2.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:1.0/11},"gorbachev":{1:1.0/11}}

		resultedIndex = {"<docid>":{1:0}, "</docid>":{1:0},  "<doc>":{1:0}, "</doc>": {1:0},"1": {1:0}, "onset": {1:0}, "of":{1:0}, "the":{1:0}, "new":{1:0},"gorbachev":{1:0}}

		#index = indexing.Index()
		self._index._doc_id_list = [1]
		self._index.inv_index = initialIndex
		self._index.update_scores_with_idf()
		self.assertEqual(self._index.inv_index, resultedIndex)

	def test_update_scores_with_idf_two_doc(self):
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
		#index = indexing.Index()
		self._index._doc_id_list = [1,2]
		self._index.inv_index = {"<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:1.0/11, 2:1.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "the":{1:1.0/11, 2:2.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}}
		self._index.update_scores_with_idf()
		self.assertEqual(self._index.inv_index, resultedIndex)


	def test_create_index_merged_based_empty(self):
	 	emptystring = ""
		resultedIndex = {}
		final_index = self._index.index_documents(emptystring)
		self.assertEqual(final_index , resultedIndex)


	def test_create_index_merged_based_limit_two_docs(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""
	 	resultedIndex = { "<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:2.0/11, 2:2.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}}
		self._index.index_text(stringNormalDoc, False)
		self.assertNotEqual(self._index._partial_files_names, [])
		self.assertEqual(self._index.inv_index , resultedIndex)


	def test_create_index_merged_based_all_docs_with_save(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>"""

		index = indexing.Index()
		self.memory_limit = 1
		partial_index = index.index_text(stringNormalDoc, False)
		self.assertNotEqual(index._partial_files_names, [])
		resultingTextFile = "1\n1,0.0909090909091;\n</doc>\n1,0.0909090909091;\n</docid>\n1,0.0909090909091;\n<doc>\n1,0.0909090909091;\n<docid>\n1,0.0909090909091;\ngorbachev\n1,0.0909090909091;\nnew\n1,0.0909090909091;\nof\n1,0.0909090909091;\nonset\n1,0.0909090909091;\nthe\n1,0.181818181818;\n"
		self.assertEqual(self.read_file(index._partial_files_names[0]), resultingTextFile)


	def test_write_partial_index_zero_doc(self):
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
		self._index.write_partial_index()
		self.assertEqual(self._index._partial_files_names, [])

	def test_write_partial_index_one_doc(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>"""

		resultedIndex = { "<docid>":{1:1.0/11}, "</docid>":{1:1.0/11},  "<doc>":{1:1.0/11}, "</doc>": {1:1.0/11}, "1": {1:1.0/11}, "the": {1:2.0/11}, "onset": {1:1.0/11}, "of":{1:1.0/11}, "new":{1:1.0/11},"gorbachev":{1:1.0/11}}
		self._index.inv_index = resultedIndex
		self._index.write_partial_index()
		resultingTextFile = "1\n1,0.0909090909091;\n</doc>\n1,0.0909090909091;\n</docid>\n1,0.0909090909091;\n<doc>\n1,0.0909090909091;\n<docid>\n1,0.0909090909091;\ngorbachev\n1,0.0909090909091;\nnew\n1,0.0909090909091;\nof\n1,0.0909090909091;\nonset\n1,0.0909090909091;\nthe\n1,0.181818181818;\n"
		self.assertEqual(self.read_file(self._index._partial_files_names[0]), resultingTextFile)

	def test_write_partial_index_two_doc(self):
		stringNormalDoc = """
		<DOC>
		<DOCID> 1 </DOCID>
		The onset of "the new Gorbachev".
		</DOC>
		<DOC>
		<DOCID> 2 </DOCID>
		the onset of "the new Gorbachev"!
		</DOC>"""

		resultedIndex = { "<docid>":{1:1.0/11, 2:1.0/11}, "</docid>":{1:1.0/11, 2:1.0/11},  "<doc>":{1:1.0/11, 2:1.0/11}, "</doc>": {1:1.0/11, 2:1.0/11}, "1": {1:1.0/11}, "2": {2:1.0/11}, "the": {1:2.0/11, 2:2.0/11}, "onset": {1:1.0/11, 2:1.0/11}, "of":{1:1.0/11, 2:1.0/11}, "new":{1:1.0/11, 2:1.0/11},"gorbachev":{1:1.0/11, 2:1.0/11}}
		self._index.inv_index = resultedIndex
		self._index.write_partial_index()
		resultingTextFile = "1\n1,0.0909090909091;\n2\n2,0.0909090909091;\n</doc>\n1,0.0909090909091;2,0.0909090909091;\n</docid>\n1,0.0909090909091;2,0.0909090909091;\n<doc>\n1,0.0909090909091;2,0.0909090909091;\n<docid>\n1,0.0909090909091;2,0.0909090909091;\ngorbachev\n1,0.0909090909091;2,0.0909090909091;\nnew\n1,0.0909090909091;2,0.0909090909091;\nof\n1,0.0909090909091;2,0.0909090909091;\nonset\n1,0.0909090909091;2,0.0909090909091;\nthe\n1,0.181818181818;2,0.181818181818;\n"
		self.assertEqual(self.read_file(self._index._partial_files_names[0]), resultingTextFile)

	def test_read_terms_from_i_file_empty(self):
		with open('partialIndex1', "w") as ifile:
			ifile.write("  ")
		with open('partialIndex1', "r") as ifile:
			self.assertFalse(self._index.read_terms_from_i_file(ifile, "partialIndex1"))

	def test_read_terms_from_i_file_one_term(self):
		with open('partialIndex2', "w") as ifile:
			ifile.write("</doc>")
		with open('partialIndex2', "r") as ifile:
			self.assertTrue(self._index.read_terms_from_i_file(ifile, "partialIndex2"))

	def test_read_terms_from_i_file_one_term_one_pl(self):
		with open('partialIndex3', "w") as ifile:
			ifile.write("term" + "\n")
			ifile.write("posting List" + "\n")
		with open('partialIndex3', "r") as ifile:
			self.assertTrue(self._index.read_terms_from_i_file(ifile, "partialIndex3"))


	def test_read_terms_from_i_file_one_term_reached_end(self):
		with open('partialIndex4', "w") as ifile:
			ifile.write("term" + "\n")
			ifile.write("posting List" + "\n")
		with open('partialIndex4', "r") as ifile:
			self._index.read_terms_from_i_file(ifile, "partialIndex4")
			self.assertFalse(self._index.read_terms_from_i_file(ifile, "partialIndex4"))


	def test_remove_line_from_file_start_2_lines(self):
		stringNormalDoc = """<DOC>
<DOCID> 1 </DOCID>
The onset of "the new Gorbachev".
</DOC>
<DOC>
<DOCID> 2 </DOCID>
the onset of "the new Gorbachev"!
</DOC>"""
		stringNormalDocCut = """The onset of "the new Gorbachev".
</DOC>
<DOC>
<DOCID> 2 </DOCID>
the onset of "the new Gorbachev"!
</DOC>"""
		with open('partialIndex5', "w") as ifile:
			ifile.write(stringNormalDoc)

		with open('partialIndex5', "r+") as ifile:
			self._index.remove_lines_from_file_start(ifile,2)
		self.assertEqual(open('partialIndex5', "r").read(),stringNormalDocCut)


	def test_remove_line_from_file_start_rm_nothing(self):
		stringNormalDoc = """<DOC>
<DOCID> 1 </DOCID>
The onset of "the new Gorbachev".
</DOC>
<DOC>
<DOCID> 2 </DOCID>
the onset of "the new Gorbachev"!
</DOC>"""

		with open('partialIndex6', "w") as ifile:
			ifile.write(stringNormalDoc)

		with open('partialIndex6', "r+") as ifile:
			self._index.remove_lines_from_file_start(ifile,0)
		self.assertEqual(open('partialIndex6', "r").read(),stringNormalDoc)


	def test_remove_line_from_file_start_everything(self):
		stringNormalDoc = """<DOC>
<DOCID> 1 </DOCID>
The onset of "the new Gorbachev".
</DOC>
<DOC>
<DOCID> 2 </DOCID>
the onset of "the new Gorbachev"!
</DOC>"""

		with open('partialIndex7', "w") as ifile:
			ifile.write(stringNormalDoc)

		with open('partialIndex7', "r+") as ifile:
			self._index.remove_lines_from_file_start(ifile,8)
		self.assertEqual(open('partialIndex7', "r").read(),"")

if __name__=='__main__':
	unittest.main()
