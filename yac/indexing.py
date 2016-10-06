"""This file allows you to create an Inverted Index."""

import glob
import re
import tokenization

pattern_doc_id = r"<DOCID>\s(\d+)\s</DOCID>"
pattern_doc_end = r"</DOC>"

def createIndex(filePathFormat):
	#creation of the Inverted Index
	ii = {}

	#filling of the Inverted Index
	for filename in glob.glob(filePathFormat):
		lines = open(filename, 'r')
		doc_id = ''
		doc = ''
		for line in lines:
			match = re.search(pattern_doc_id, line)
			if match:
				#extract the docid from the line : the first group in the regex (what's between parenthesis)
				doc_id = int(match.group(1))
			elif re.search(pattern_doc_end, line) and doc != '' and doc_id != '':
				#if we reached the end of the document, insert tokens in hashmap and flush variables
				words = tokenization.TextFile.tokenizeStringSplit(doc)
				score = 1.0/len(words)
				for word in words:
					if not word in ii:
						ii[word] = {}
					if not doc_id in ii[word]:
						ii[word][doc_id] = score
					else:
						ii[word][doc_id] += score
				doc = ''
				del doc_id
	return ii
	

