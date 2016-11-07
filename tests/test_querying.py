import unittest
from context import querying, indexing


class QueryingTestCase(unittest.TestCase):

	@property
	def index(self):
		return self._index

	@index.setter
	def index(self, value):
		self._index = value

	def setUp(self):
		self._index = indexing.Index()

	def test_get_terms_with_stop_words(self):

		query = "The most beautiful thing of all times !"
		self.assertEqual(querying.get_terms(query), ["the", "most", "beautiful","thing", "of", "all", "times"])

	def test_get_terms_without_stop_words(self):

		query = "The most beautiful thing of all times !"
		self.assertEqual(querying.get_terms(query,True), ["beautiful","thing","times"])
	

	def test_get_terms_case_insensitive(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(querying.get_terms(query,False, False), ["the", "most", "beautiful","thing", "of", "all","times"])
	

	def test_get_terms_case_sensitive(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(querying.get_terms(query,False, True), ["The", "Most", "BeauTiful","Thing", "oF", "All","Times"])
	
	def test_get_terms_stemming(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(querying.get_terms(query,False, True, True), ["The", "Most", "BeauTi","Thing", "oF", "All","Time"])

	def test_find_docs_disj_empty(self):
		query = "Carrefour, tudududu!"
		self._index._inv_index = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		dicOfDocs = querying.naive_disj_algo(self._index._inv_index, query)
		self.assertEqual(dicOfDocs,{})

	def test_find_docs_disj_normal(self):
		self._index._inv_index = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		query = "and as both"
		dicOfDocs = querying.naive_disj_algo(self._index._inv_index, query)
		self.assertEqual(dicOfDocs,{1:2,2:1})

	def test_find_docs_conj_empty(self):
		self._index._inv_index = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}
		query = "Carrefour, tudududu!"
		dicOfDocs = querying.naive_conj_algo(self._index._inv_index, query)
		self.assertEqual(dicOfDocs,{})

	def test_find_docs_conj_result_not_enought_matches(self):
		self._index._inv_index = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}

		query = "and as both"
		dicOfDocs = querying.naive_conj_algo(self._index._inv_index, query)
		self.assertEqual(dicOfDocs, {})

	def test_find_docs_conj_normal(self):
		self._index._inv_index = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
		"around": {1:1}, "as": {2:1},"both": {1:1},
		"bright": {3:1}}

		query = "and around both"
		dicOfDocs = querying.naive_conj_algo(self._index._inv_index, query)
		self.assertEqual(dicOfDocs, {1:3})


	def tearDown(self):
		self._index = None

if __name__=='__main__':
	unittest.main()