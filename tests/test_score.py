import unittest
from context import score

class ScoreTestCase(unittest.TestCase):
	#def setUp(self):

	#Indexing tests cases
	def test_get_terms_with_stop_words(self):

		query = "The most beautiful thing of all times !"
		self.assertEqual(score.get_terms(query), ["the", "most", "beautiful","thing", "of", "all", "times"])

	def test_get_terms_without_stop_words(self):

		query = "The most beautiful thing of all times !"
		self.assertEqual(score.get_terms(query,True), ["beautiful","thing","times"])
	

	def test_get_terms_case_insensitive(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(score.get_terms(query,False, False), ["the", "most", "beautiful","thing", "of", "all","times"])
	

	def test_get_terms_case_sensitive(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(score.get_terms(query,False, True), ["The", "Most", "BeauTiful","Thing", "oF", "All","Times"])
	
	def test_get_terms_stemming(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(score.get_terms(query,False, True, True), ["The", "Most", "BeauTi","Thing", "oF", "All","Time"])
	
	#def tearDown(self):

if __name__=='__main__':
	unittest.main()