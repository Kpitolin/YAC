"""This file allows you to create an Inverted Index."""

import glob
import re
import tokenization
import score
import time
from blist import sorteddict,sortedlist



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
		self._doc_quantity = 0

		self.dict_file_term = sorteddict()
		self.dict_term_pl = dict()

		self.dictTermsOffset=dict()


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
			for filename in sorted(glob.glob(self.filePathFormat)):
				print(filename)
				lines = open(filename, 'r')
				self.inv_index = self.create_index_merged_based_from_text(lines)
			self.read_terms_in_file()

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
	    		self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(term_plist), len(self._doc_id_list))

	def pair_list_to_text(self,pl):
		""" Transforms a posting list [<docId, Score>] in a text with comas and semi colons : 
			docId, Score;  docId, Score;
		"""
		text = ""
		for (item1, item2) in pl:
			text = text + str(item1)+","+ str(item2)+";"
		return text

	def text_to_pair_list(self, text):
		""" Transforms a text (docId, Score;  docId, Score;) to a posting list [<docId, Score>]
		"""
		lines =[]
		#textfile
		if hasattr(text, 'readlines'):
			lines = text
		#multi-line string
		elif isinstance(text,str):
			lines = text.splitlines(False)
		for line in lines:
			pair_list = text.rstrip().split(";")[:-1]
			for index in range(len(pair_list)):
				pair = pair_list[index].split(",")
				pair_list[index] = (pair[0],pair[1])
		return pair_list

	# Replaces the temporary score by the tf idf in each item of the index dictionnary that's in the query
	def calculate_terms_in_query_scores_memory(self, query):

		for term in score.getTerms(query):
			#print list(self.inv_index.iteritems())
			if term in self.inv_index:
				term_plist = self.inv_index[term]
				for doc_id in term_plist:
					self.inv_index[term][doc_id] *= score.inverse_document_frequency(len(term_plist), len(self._doc_id_list))


	def create_index_merged_based_from_text(self, text):
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
		self.inv_index = {}
		for line in lines:
			
			if nbDoc >= self._doc_limit:
				self.save_index_to_file()
				break
			doc = doc + '\n' + line
			match = re.search(PATTERN_DOC_ID, line)

			if match:
				#extract the docid from the line : the first group in the regex (what's between parenthesis)
				doc_id = int(match.group(1))
				print(doc_id)
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
							if not word in self.inv_index:
								self.inv_index[word] = [(doc_id, score)]
							else:
								lastDocIndex = len(self.inv_index[word]) - 1
								(docIdTemp, scoreTemp) = self.inv_index[word][lastDocIndex]
								if doc_id != docIdTemp:
									self.inv_index[word].append((doc_id, score))
								else:
									self.inv_index[word].pop()
									self.inv_index[word].append((docIdTemp, score + scoreTemp))

					nbDoc+=1
				# flush variables before passing to the next document
				doc = ''
				del doc_id
		return self.inv_index

	def save_index_to_file(self):
		""" Creates a file following this format : 
			term 
			Posting List 
			term 
			Posting List

		 	and adds it to the self._pl_file_list
		"""
		file_name = "fileIndex" + str(time.clock())
		print(file_name)
		with open(file_name,"a+") as f:		
			sortedIndex = sorted(self.inv_index)
			for word in sortedIndex :
				f.write(word+"\n")
				f.write(self.pair_list_to_text(self.inv_index[word]))
				f.write("\n")
		self._pl_file_list.append(file_name)


	def read_terms_from_i_file(self,f,ifilename):
		pattern_term = r"<?/?\w+"
		term = f.readline()
		pl = f.readline().rstrip()
		if len(term) != 0 and not re.match(pattern_term,term):
			return self.read_terms_from_i_file(f,ifilename)
		elif len(term) == 0 :
			return False
		if term not in self.dict_file_term.keys():
			self.dict_file_term[term] =sortedlist([ifilename])
			self.dict_term_pl[term] = [pl]
		else:
			(self.dict_file_term[term]).add(ifilename)
			index_0 = (self.dict_file_term[term]).index(ifilename)
			(self.dict_term_pl[term]).insert(index_0,pl)
		return True


	def read_terms_in_file(self):
		"""It reads the ith term of each file, find the lowest term (alphabetical order)
			and updates a data structure [filename : <term, line>] ordered by term and filename
			Calls save_final_pl_to_file

			dictFile is a data structure {filename: content} that allows us to have the state of everything open file saved (with the cursor at the last line read)
		"""

		term=''
		dictFile = {}
		#fileFinished=list()#
		# Initialization: open all the inverted file and read the first term into the dictionary of terms sorted by key
		for ifilename in  self._pl_file_list :
			dictFile[ifilename] = open(ifilename, "r");
			self.read_terms_from_i_file(dictFile[ifilename],ifilename)
		# Pop the first term of the dictionary and update the dic by reading the following lines of the file
		while bool(self.dict_file_term): 
		#for num in range(10,20):
			element = self.dict_file_term.popitem() # return the pair <term, filename> with the lowest key (sorteddict)
			pl=self.dict_term_pl[element[0]]
			if(self.save_final_pl_to_file(element[0],pl)):
				for ifilename in element[1]:
					if(self.read_terms_from_i_file(dictFile[ifilename],ifilename) == False):
						dictFile[ifilename].close()
						del dictFile[ifilename]
			else:
				return False
		# After readind 100 (configurable) terms in memory ,flush them into the final inverted File
		self.save_extra_file()


	def calculate_all_term_pl_scores(self, PL):
		"""Modify final inverted file to write final score for each doc in eah pl
		"""

		nb_docs = len(self._doc_id_list)
		list_pls = []
		for sring_pls in PL:
			list_pls = list_pls + self.text_to_pair_list(sring_pls)	
		for index in range(len(list_pls)):
				(doc_id,scoreTemp) = map(float,list_pls[index])
				scoreTemp *= score.inverse_document_frequency(len(list_pls), nb_docs)
				list_pls[index] = (doc_id,scoreTemp)
		return list_pls


	def save_final_pl_to_file(self,term,PL):
		"""Creates a single file for the posting lists. format : 
			PL;PL2;PL3 and so on
		   It writes each posting list from offsetMin to offsetMax
		"""
		list_pls = self.calculate_all_term_pl_scores(PL)
		print(list_pls)
		with open('InvertedFile', "a+") as ifile:
			#ifile.write(term+"\n")
			offsetMin=ifile.tell()
			print(self.pair_list_to_text(list_pls))
			ifile.writelines(self.pair_list_to_text(list_pls)+"\n")
			offsetMax=ifile.tell()
			self.dictTermsOffset[term]=(offsetMin,offsetMax)
		return True

	def save_extra_file(self):
		""" Saves the nb of docs to file
		It also writes a dic {term : <offsetMin, offsetMax>} 
		"""
		with open('ExtraFile', "w") as ifile:
			ifile.write("{}\n".format(len(self._doc_id_list))) #todo once
			#ifile.write(self.pair_list_to_text(self.dictTermsOffset))


