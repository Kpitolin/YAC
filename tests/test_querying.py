import unittest
from context import querying


class QueryingTestCase(unittest.TestCase):
	#def setUp(self):
	def test_find_docs_disj_empty(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		query = "Carrefour, tudududu!"
		dicOfDocs = querying.findDocsSortedByScoreDisj(invertedFile, query)
		self.assertEqual(dicOfDocs,([],{}))

	def test_find_docs_disj_normal(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		query = "and as both"
		dicOfDocs = querying.findDocsSortedByScoreDisj(invertedFile, query)
		self.assertEqual(dicOfDocs,([1,2],{1:2,2:1}))

	def test_find_docs_conj_empty(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		query = "Carrefour, tudududu!"
		dicOfDocs = querying.findDocsSortedByScoreConj(invertedFile, query)
		self.assertEqual(dicOfDocs,([],{}))

	def test_find_docs_conj_result_not_enought_matches(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}

		query = "and as both"
		dicOfDocs = querying.findDocsSortedByScoreConj(invertedFile, query)
		self.assertEqual(dicOfDocs, ([],{}))

	def test_find_docs_conj_normal(self):
		invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}

		query = "and around both"
		dicOfDocs = querying.findDocsSortedByScoreConj(invertedFile, query)
		self.assertEqual(dicOfDocs, ([1],{1:3}))

	def test_sortDict_normal(self):
		dicOfDocs = {1:1, 3:2, 9:9}
		sortedList = querying.sort(dicOfDocs)
		self.assertEqual(sortedList, [9,3,1])
	#def tearDown(self):

if __name__=='__main__':
	unittest.main()