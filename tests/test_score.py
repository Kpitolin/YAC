import unittest
from context import score

class TokenizationTestCase(unittest.TestCase):
	#def setUp(self):

	#Indexing tests cases
	def test_getTerms(self):

		query = "The most beautiful thing of all times !"
		self.assertEqual(score.getTerms(query), ["beautiful","thing","times"])
	
	#def tearDown(self):


if __name__=='__main__':
	unittest.main()