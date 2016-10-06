"""This file allows you to create an Inverted Index."""

import tokenization

pattern_doc_id = r"<DOCID>\s(\d+)\s</DOCID>"
pattern_doc_end = r"</DOC>"

#creation of the Inverted Index
ii = {}

#filling of the Inverted Index
for filename in glob.glob("../../latimes/la010189"):
  lines = open(filename, 'r')
  
	doc_id = ''
	doc = ''

	for line in lines:
		match = re.search(pattern_doc_id, line)
		if match:
			#extract the docid from the line : the first group in the regex (what's between parenthesis)
			doc_id = int(match.group(1))

		elif re.search(pattern_doc_end, line) and doc_word_list != [] and doc_id != '':
			#if we reached the end of the document, insert tokens in hashmap and flush variables
			words = tokenize(doc)
			
		  score = 1.0/len(words)
			for word in words:
				if not word in ii:
					ii[word] = {}
				if not filename in ii[word]:
					ii[word][filename] = score
				else:
					ii[word][filename] += score
			doc = ''
			del doc_id

