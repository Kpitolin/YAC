import unittest
from context import score
import math
class ScoreTestCase(unittest.TestCase):
	#def setUp(self):

	#Score tests cases
	def test_inverse_document_frequency_zero_containing(self):
		nb_docs_containing = 0
		nb_docs = 1
		self.assertTrue(math.isnan(score.inverse_document_frequency(nb_docs_containing,nb_docs)))

	def test_inverse_document_frequency_zero_docs(self):
		nb_docs_containing = 0
		nb_docs = 0
		self.assertTrue(math.isnan(score.inverse_document_frequency(nb_docs_containing,nb_docs)))

	def test_inverse_document_frequency_one(self):
		nb_docs_containing = 1 
		nb_docs = 1
		self.assertEqual(score.inverse_document_frequency(nb_docs_containing,nb_docs),0)

	def test_inverse_document_frequency_normal(self):
		nb_docs_containing = 10
		nb_docs = 100
		self.assertEqual(score.inverse_document_frequency(nb_docs_containing,nb_docs),1.0)

	def test_inverse_document_frequency_negative(self):
		nb_docs_containing = -1 
		nb_docs = 1
		self.assertTrue(math.isnan(score.inverse_document_frequency(nb_docs_containing,nb_docs)))


	#def tearDown(self):

if __name__=='__main__':
	unittest.main()