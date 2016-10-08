"""This file allows you to create an Inverted Index."""

import glob
import re
import tokenization
import score

PATTERN_DOC_ID = r"<DOCID>\s(\d+)\s</DOCID>"
PATTERN_DOC_END = r"</DOC>"


class Index:
	""" Example of inv_index : 
	 { "term 1": {1:1}, "term 2": {3:1}, "term 3":{2:1, 4:1}}
	 The inner dictionnary is structured that way : {doc_id:score} both are int for now
	"""
	doc_id_list = []

	def __init__(self, filePathFormat = ""):
		self.filePathFormat = filePathFormat
		self.inv_index = {}
	
	def createIndexFromFileFormat(self):
		"""Creates the Inverted Index for a file or multiple file of the same format
		For now, the score is just the frequency of the term in the document


		Usage for every file starting with la (outside of this module):
		inv_index = indexing.Index("../../../../Downloads/latimes/la*").createIndexFromFileFormat()

		Usage for a file
		inv_index = indexing.Index("../../../../Downloads/latimes/la010189").createIndexFromFileFormat()

		"""

		if self.filePathFormat != "":
			#filling of the Inverted Index
			for filename in glob.glob(self.filePathFormat):
				lines = open(filename, 'r')
				inv_index = self.createIndexFromText(lines)
					
		return inv_index

	#We had a pb in inv_index => if you execute the function two times in a row with default parameters, inv_index has a value the second time
	def createIndexFromText(self, text):
		"""Creates the Inverted Index for a text

		Usage 
		a = indexing.Index().createIndexFromText(textMultiline)
		"""

		doc_id = ''
		doc = ''
		lines = []

		#textfile
		if hasattr(text, 'readlines'):
			lines = text
		#multi-line string 
		elif isinstance(text,str):
			lines = text.splitlines(False)

		for line in lines:
			doc += line
			match = re.search(PATTERN_DOC_ID, line)
			if match:
				#extract the docid from the line : the first group in the regex (what's between parenthesis)
				doc_id = int(match.group(1))
				self.doc_id_list.append(doc_id)
			elif re.search(PATTERN_DOC_END, line) and doc != '' and doc_id != '':
				#if we reached the end of the document, insert tokens in hashmap and flush variables
				
				words = tokenization.TextFile.tokenizeStringSplit(doc)
				# for the time being, we just calculate the frequency of each term and put it as the score
				# avoid ZeroDivisionError
				if len(words) > 0:
					score = 1.0/len(words)
					for word in words:
						if not word in self.inv_index:
							self.inv_index[word] = {}
						if not doc_id in self.inv_index[word]:
							self.inv_index[word][doc_id] = score
						else:
							self.inv_index[word][doc_id] += score
					# flush variables before passing to the next document
					doc = ''
					del doc_id

		return self.inv_index


	#Replaces the temporary score by the tf idf in each item of the index dictionnary
	def  calculate_all_scores_memory(self):

	    for term,term_plist in self.inv_index.iteritems():
	    	for doc_id in self.inv_index[term]:
	    		self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(term_plist), len(self.doc_id_list))
	

