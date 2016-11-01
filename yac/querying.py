""" this file define a mock of an inverted file and a simple querying algorithm """
import time
import re
import indexing, tokenization
from sys import argv
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()


def getTerms(query, remove_stopwords = False , case_sensitive = False , with_stemming = False):
    stop_words=stopwords.words('english')

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
def findDocsDisj(invertedFile, query):
	queryList = getTerms(query)
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
def findDocsConj(invertedFile,query):
    queryList = getTerms(query)
    postingLists = []
    #On recupere les PL de chaque terme
    for word in queryList :
    	if word in invertedFile:
        	postingLists += [invertedFile[word]]
    
	request = {}
	last = []
    if len(postingLists)>0:
    	last = postingLists.pop()

    for doc in last : #Boucle sur les clefs dans results
        doc_score = last[doc]
        for PL in postingLists :
            if PL.has_key(doc) :
                doc_score += PL[doc]
            else :
                doc_score = 0
                break
        if doc_score != 0 :
            request[doc] = doc_score
    return request

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


    index = indexing.Index("../latimes/la*")
    index.createIndexFromFileFormat()
    #index.calculate_all_scores_merged_based()
    query = raw_input("Entrez votre recherche disjonctive: ")
    print "Resutat recherche disjonctive:"
    dicOfDocs = findDocsDisj(index.inv_index, query)
    sortAndPrintDict(dicOfDocs)
    end = time.clock()

    print "Elapsed Time: {} seconds".format(end - start)


    #Token recherche conjonctive ("ET")
    #query = raw_input("Entrez votre recherche disjonctive: ")
    #findDocsSortedByScoreConj(invertedFile,query)
