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


	@property
	def current_doc_index(self):
		return self._current_doc_index
	@current_doc_index.setter
	def current_doc_index(self, value):
		self._current_doc_index = value

	@property
	def doc_limit(self):
		return self._doc_limit

	@doc_limit.setter
	def doc_limit(self, value):
		self._doc_limit = value

	@property
	def memory_limit(self):
		return self._memory_limit
	@memory_limit.setter
	def memory_limit(self, value):
		self._memory_limit = value


	def __init__(self, filePathFormat = "", filterTags = False, remove_stopwords = False, case_sensitive = False, with_stemming = False):
		self.filePathFormat = filePathFormat
		self.filterTags = filterTags
		self.inv_index = {}
		self.remove_stopwords = remove_stopwords
		self.case_sensitive = case_sensitive
		self.with_stemming = with_stemming

		self._doc_id_list = []
		self._pl_file_list = []
		self._current_doc_index = 0
		self._doc_limit = 10
		self._memory_limit = 10


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
				self.inv_index = self.createIndexFromText(lines)

		return self.inv_index

	# We had a pb in inv_index => if you execute the function two times in a row with default parameters, inv_index has a value the second time
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
				self._doc_id_list.append(doc_id)
			elif re.search(PATTERN_DOC_END, line) and doc != '' and doc_id != '':
				#if we reached the end of the document, insert tokens in hashmap and flush variables

				words = tokenization.TextFile.tokenizeStringSplit(doc, self.filterTags, self.remove_stopwords, self.case_sensitive, self.with_stemming)

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


	# Replaces the temporary score by the tf idf in each item of the index dictionnary
	def calculate_all_scores_memory(self):

	    for term,term_plist in self.inv_index.iteritems():
	    	for doc_id in self.inv_index[term]:
	    		self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(term_plist), len(self.doc_id_list))


	# Replaces the temporary score by the tf idf in each item of the index dictionnary that's in the query
	def calculate_terms_in_query_scores_memory(self, query):

		for term in score.getTerms(query):
			#print list(self.inv_index.iteritems())
			if term in self.inv_index:
				term_plist = self.inv_index[term]
				for doc_id in term_plist:
					self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(term_plist), len(self.doc_id_list))


	def createIndexMergedBasedFromText(self, text):
		""" Creates a merged based index 
			We read text from the stream doc by doc until we reach docLimit or memoryLimit
			Everytime, we update a map {term :[<docId, Score>]} the posting list [<docId, Score>] must be ordered by docId
			Hypothesis : we run througth the documents in order so the posting lists are naturally ordered by score
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

		nbDoc = 0
		inv_index = {}
		for line in lines:
			
			if nbDoc >= self._doc_limit:
				break
			doc = doc + '\n' + line
			match = re.search(PATTERN_DOC_ID, line)

			if match:
				#extract the docid from the line : the first group in the regex (what's between parenthesis)
				doc_id = int(match.group(1))
				if doc_id >= self._current_doc_index:

					self._doc_id_list.append(doc_id)
					self._current_doc_index = doc_id
					
			elif re.search(PATTERN_DOC_END, line) and doc != '':

				if len(self._doc_id_list)-nbDoc > 0: 
					#if we reached the end of the document, insert tokens in hashmap and flush variables
					words = tokenization.TextFile.tokenizeStringSplit(doc, self.filterTags, self.remove_stopwords, self.case_sensitive, self.with_stemming)
					# for the time being, we just calculate the frequency of each term and put it as the score
					# avoid ZeroDivisionError
					if len(words) > 0:
						score = 1.0/len(words)
						for word in words:
							if not word in inv_index:
								inv_index[word] = [(doc_id, score)]
							else:
								lastDocIndex = len(inv_index[word]) - 1
								(docIdTemp, scoreTemp) = inv_index[word][lastDocIndex]
								if doc_id != docIdTemp:
									inv_index[word].append((doc_id, score))
								else:
									inv_index[word].pop()
									inv_index[word].append((docIdTemp, score + scoreTemp))

					nbDoc+=1
				# flush variables before passing to the next document
				doc = ''
				del doc_id
		return inv_index

	def saveIndexToFile(self):
		""" Creates a file following this format : 
			term 
			Posting List 
			term 
			Posting List

		 	and adds it to the plFileList
		"""
		file_name = "IndexFiles/fileIndex" + str(len(self.plFileList))
		with open(file_name,"a+") as f:		
			sortedIndex = sorted(self.inv_index)
			for word in sortedIndex :
				f.write(word+"\n")
				for pl in self.inv_index[word] :
					f.write(str(pl)+","+ str(self.inv_index[word][pl])+";")
				f.write("\n")
				self.plFileList.append(file_name)


	def readTermsInFile(self):
		"""It reads the ith term of each file, find the lowest term (alphabetical order)
			and updates a data structure [filename : <term, line>] ordered by term and filename
			Calls saveFinalPLToFile
		"""


	def saveFinalPLToFile(self):
		"""Creates a single file for the posting list.
		   It writes each posting list from offsetMin to offsetMax
		   It also writes a dic {term : <offsetMin, offsetMax>} 
		"""
