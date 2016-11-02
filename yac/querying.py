""" this file define a mock of an inverted file and a simple querying algorithm """
import time
import re
import linecache
import indexing, tokenization
from sys import argv
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()


def text_to_pl(text):
    """ Transforms a text "doc1,score_doc1;doc2, score_doc2;" to a posting list {doc1:score_doc1, doc2:score_doc2} """
    pl = {}
    pair_list = text.rstrip().split(";")[:-1]
    for index in range(len(pair_list)):
        pair = pair_list[index].split(",")
        pl[pair[0]] = float(pair[1])
    return pl

def threshold_algo(index, query, k): # index a passer en parametre
    # offsets remplacer
    #offsets = {"soviet":1, "moscow":2}

    sorted_by_docs = {} # Extrait de l'inverted index ne contenant que les termes de la requete
    sorted_by_scores = {} # Dictionnaire qui associe aux termes de la requete la liste des documents dans laquelle ils apparaissent triee par score decroissant
    terms = [] # Termes de la requete presents dans l'inverted file
    query_terms  = get_terms(query)
    for term in query_terms: # Construction des deux index : tries par document et par score
        if term in index.dictTermsOffset:
            print index.dictTermsOffset[term]
            print term
            terms.append(term)
            text = linecache.getline('InvertedFile', index.dictTermsOffset[term])
            sorted_by_docs[term] = text_to_pl(text)
            sorted_by_scores[term] = sorted(sorted_by_docs[term], key=sorted_by_docs[term].__getitem__, reverse=True)
    t = 1
    smallest_score = 0 # Plus petit score parmis les documents du top-k
    top_k = []
    docs_met = set()
    # TODO :  check if k < nb docs
    while t > smallest_score or len(top_k)<k: # Iteration sur les documents tries par score
        t = 0 # Seuil : score maximal atteignable par les documents pas encore etudies
        for term in terms:
            if len(sorted_by_scores[term]) > 0:
                doc = sorted_by_scores[term].pop(0) # Document avec le meilleur score pour ce terme
                if len(sorted_by_scores[term]) > 0:
                    t += sorted_by_docs[term][sorted_by_scores[term][0]] # Mise a jour du seuil
                if not doc in docs_met: # Si c'est la premiere fois qu'on le rencontre
                    docs_met.add(doc)
                    score = 0
                    # Calcul du score du document
                    for a_term in terms:
                        if doc in sorted_by_docs[a_term]:
                            score += sorted_by_docs[a_term][doc]
                    # Modification eventuelle des top-k documents
                    #print "Doc " + str(doc) + " has a score of " + str(score)
                    if len(top_k) < k:
                        top_k.append((doc, score))
                        top_k.sort(key=lambda x: x[1])
                    else:
                        if score > top_k[0][1]:
                            top_k.pop(0)
                            top_k.append((doc, score))
                            top_k.sort(key=lambda x: x[1])
                            #print "New top-k :"
                            #print top_k
        smallest_score = top_k[0][1]
        #print "t = " + str(t) + " > smallest score = " + str(smallest_score) + " ? " + str(t > smallest_score)
    print top_k


def get_terms(query, remove_stopwords=False, case_sensitive=False, with_stemming=False):
    stop_words = stopwords.words('english')

    if not case_sensitive:
        query=query.lower()
    query=re.sub(r"[^a-zA-Z0-9 ]",' ',query)
    words=[x for x in query.split() if not remove_stopwords or x.lower() not in stop_words]
    terms=[]
    if with_stemming:
        terms=[porter_stemmer.stem(word) for word in words]
    else:
        terms=words
    return terms


#Return a list of the doc ids sorted by score
def sort(dict_score):
	sortedList = sorted(dict_score, key=dict_score.__getitem__, reverse=True)
	return sortedList

#Prints a list of pairs {doc id: score} already sorted by score (DESC)
def printDocOrderedByScores(dict_score,sortedList):
	if len(sortedList)==0:
		print("Terms of query not found in document(s)")
	for doc in sortedList :
		print("{0} : {1}".format(doc,str(dict_score[doc])))

#Orders by score (DESC) and prints a list of pairs {doc id: score}
def sortAndPrintDict(dict_score):
	sortedList = sort(dict_score)
	printDocOrderedByScores(dict_score, sortedList)


#Token recherche disjonctive ("OU")

#Returns a dict {doc id: score} where score is the sum of scores for each term of the query present in the document 
def findDocsDisjMergedBased(index, query):

	queryList = get_terms(query)
	response = {}
	for word in queryList:
		if word in index.dictTermsOffset:
			print index.dictTermsOffset[word]
			offset = index.dictTermsOffset[word]
			line = linecache.getline("InvertedFile", offset)
			pl = index.text_to_pair_list(line)
			for doc,score in pl:
				if(doc in response):
					response[doc] += score
				else:
					response[doc] = score
	return response


#Token recherche disjonctive ("OU")
#Returns a dict {doc id: score} where score is the sum of scores for each term of the query present in the document
def findDocsDisjMemory(invertedFile, query):
    queryList = get_terms(query)
    request = {}
    for word in queryList:
        if word in invertedFile:
                for doc in invertedFile[word]:
                    if(doc in request):
                        request[doc] += invertedFile[word][doc]
                    else:
                        request[doc] = invertedFile[word][doc]
    return request


def popSmallestDict(dictList):
	smallest = min(dictList)
	dictList.remove(smallest)
	return smallest

#Token recherche conjonctive ("ET")
#Returns a dict {doc id: score} where score is the sum of scores for each term. Every term of the query must be in the document
def findDocsConj(index,query):

	queryList = getTerms(query)
	postingLists = []
	#On recupere les PL de chaque terme
	for word in queryList:
		if word in index.dictTermsOffset:
			offset = index.dictTermsOffset[word]
			line = linecache.getline("InvertedFile", offset)
			pl = index.text_to_pair_list(line)
			postingLists += pl
	
	request = {}
	last = []
	if len(postingLists)>0:
		last = postingLists.pop()

	print(last)
	for doc0, score0 in last : #Boucle sur les clefs dans results
		for doc,score in postingLists :
			if doc == doc :
				doc_score += PL[doc]
			else :
				doc_score = 0
				break
		if doc_score != 0 :
			request[doc0] = doc_score
	return response

def findDocsSortedByScoreDisj(invertedFile,query):
	nonSortedDict = findDocsDisj(invertedFile,query)
	sortedDict = sortDict(nonSortedDict)
	return (sortedDict, nonSortedDict)


def findDocsSortedByScoreConj(invertedFile,query):
	nonSortedDict = findDocsConj(invertedFile,query)
	sortedDict = sortDict(nonSortedDict)
	return (sortedDict, nonSortedDict)

if __name__=='__main__':

	#Prompt for query terms
	#Here specify the location of the textfiles to search upon
	start = time.clock()
	index = indexing.Index("../../../latimes/la010189")
	#inv_index = index.create_index_from_file_format_memory()
	index.create_index_from_file_format_merged_based()
	query = raw_input("Entrez votre recherche disjonctive: ")
	print index.dictTermsOffset[query]

	print "Resutat recherche disjonctive:"
	print "requetage naif"

	dicOfDocs = findDocsDisjMergedBased(index, query)
	sortAndPrintDict(dicOfDocs)

	print "requetage faggins"

	threshold_algo(index, query,10)
	#dicOfDocs = findDocsDisjMemory(inv_index, query)
	end = time.clock()

	print "Elapsed Time: {} seconds".format(end - start)


	#Token recherche conjonctive ("ET")
	#query = raw_input("Entrez votre recherche disjonctive: ")
	#findDocsSortedByScoreConj(invertedFile,query)
