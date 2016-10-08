import unittest
from context import score

class TokenizationTestCase(unittest.TestCase):
	#def setUp(self):

	#Indexing tests cases
	def test_getTerms_with_stop_words(self):

		query = "The most beautiful thing of all times !"
		self.assertEqual(score.getTerms(query), ["The", "most", "beautiful","thing", "of", "all", "times"])

	def test_getTerms_without_stop_words(self):

		query = "The most beautiful thing of all times !"
		self.assertEqual(score.getTerms(query,True), ["beautiful","thing","times"])
	

	def test_getTerms_case_insensitive(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(score.getTerms(query,False, False), ["the", "most", "beautiful","thing", "of", "all","times"])
	

	def test_getTerms_case_sensitive(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(score.getTerms(query,False, True), ["The", "Most", "BeauTiful","Thing", "oF", "All","Times"])
	
	def test_getTerms_stemming(self):

		query = "The Most BeauTiful Thing oF All Times !"
		self.assertEqual(score.getTerms(query,False, True, True), ["The", "Most", "BeauTi","Thing", "oF", "All","Time"])
	
	#def tearDown(self):

if __name__=='__main__':
	unittest.main()