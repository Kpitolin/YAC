import unittest
from context import querying


class QueryingTestCase(unittest.TestCase):
	#def setUp(self):
	def test_findDocsDisj_empty(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		query = "Carrefour, tudududu!"
		dicOfDocs = querying.findDocsDisj(invertedFile, query)
		self.assertEqual(dicOfDocs,{})

	def test_findDocsDisj_normal(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		query = "and as both"
		dicOfDocs = querying.findDocsDisj(invertedFile, query)
		self.assertEqual(dicOfDocs,{1:2,2:1})

	def test_findDocsConj_empty(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		query = "Carrefour, tudududu!"
		dicOfDocs = querying.findDocsConj(invertedFile, query)
		self.assertEqual(dicOfDocs,{})

	def test_findDocsConj_result_not_enought_matches(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}

		query = "and as both"
		dicOfDocs = querying.findDocsConj(invertedFile, query)
		self.assertEqual(dicOfDocs, {})

	def test_findDocsConj_normal(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}

		query = "and around both"
		dicOfDocs = querying.findDocsConj(invertedFile, query)
		self.assertEqual(dicOfDocs, {1:3})

	def test_sortDict_normal(self):
		dicOfDocs = {1:1, 3:2, 9:9}
		sortedList = querying.sort(dicOfDocs)
		self.assertEqual(sortedList, [9,3,1])
	#def tearDown(self):

if __name__=='__main__':
	unittest.main()