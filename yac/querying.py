""" this file define a mock of an inverted file and a simple querying algorithm """
import time
import re
import linecache
import indexing, tokenization
from sys import argv
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()

#inverted file
invertedFile = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
"around": {1:1}, "as": {2:1},"both": {1:1},
"bright": {3:1},"coloration": {3:1, 4:1},"derives": {4:1},
"due": {3:1},"environements": {1:1},"fish": {1:2, 2:3, 3:2, 4:7},
"fishkeepers": {2:1},"found": {1:1},"fresh": {2:1}, "freshwater": {1:1, 4:1},
"from": {4:1} }

def text_to_pl(text):
    """ Transforms a text "doc1,score_doc1;doc2, score_doc2;" to a posting list {doc1:score_doc1, doc2:score_doc2} """
    pl = {}
    pair_list = text.rstrip().split(";")[:-1]
    for index in range(len(pair_list)):
        pair = pair_list[index].split(",")
        pl[pair[0]] = float(pair[1])
    return pl

def threshold_algo(query_terms, k): # index a passer en parametre
    # offsets remplacer
    offsets = {"soviet":1, "moscow":2}

    sorted_by_docs = {} # Extrait de l'inverted index ne contenant que les termes de la requete
    sorted_by_scores = {} # Dictionnaire qui associe aux termes de la requete la liste des documents dans laquelle ils apparaissent triee par score decroissant
    terms = [] # Termes de la requete presents dans l'inverted file
    for term in query_terms: # Construction des deux index : tries par document et par score
        if term in offsets:
            terms.append(term)
            text = linecache.getline('InvertedFile_test', offsets[term])
            sorted_by_docs[term] = text_to_pl(text)
            sorted_by_scores[term] = sorted(sorted_by_docs[term], key=sorted_by_docs[term].__getitem__, reverse=True)
    t = 1
    smallest_score = 0 # Plus petit score parmis les documents du top-k
    top_k = []
    docs_met = set()
    while t > smallest_score: # Iteration sur les documents tries par score
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
def findDocsDisj(invertedFile, query):
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
def findDocsConj(invertedFile,query):
    queryList = get_terms(query)
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


    index = indexing.Index("../latimes/la021*")
    index.createIndexFromFileFormat()
    index.calculate_all_scores_memory()
    query = raw_input("Entrez votre recherche disjonctive: ")
    print "Resutat recherche disjonctive:"
    dicOfDocs = findDocsDisj(index.inv_index, query)
    sortAndPrintDict(dicOfDocs)
    end = time.clock()

    print "Elapsed Time: {} seconds".format(end - start)


    #Token recherche conjonctive ("ET")
    #query = raw_input("Entrez votre recherche disjonctive: ")
    #findDocsSortedByScoreConj(invertedFile,query)
