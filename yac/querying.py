""" this file define a mock of an inverted file and a simple querying algorithm """
import time
import re
import linecache
import indexing
import tokenization
import os.path
from sys import argv
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()

def get_terms(query, remove_stopwords=False, case_sensitive=False, with_stemming=False):
    """ X """

    stop_words = stopwords.words('english')

    if not case_sensitive:
        query = query.lower()
    query = re.sub(r"[^a-zA-Z0-9 ]",' ',query)
    words = [x for x in query.split() if not remove_stopwords or x.lower() not in stop_words]
    terms = []
    if with_stemming:
        terms = [porter_stemmer.stem(word) for word in words]
    else:
        terms = words
    return terms

########## THRESHOLD ALGORITHM ##########

def text_to_pl(text):
    """ Transforms a string "doc1,score_doc1;doc2, score_doc2;" to a posting list {doc1:score_doc1, doc2:score_doc2} """

    pl = {}
    pair_list = text.rstrip().split(";")[:-1]
    for index in range(len(pair_list)):
        pair = pair_list[index].split(",")
        pl[pair[0]] = float(pair[1])
    return pl

def query_with_threshold_algo(index, query, k):
    """ Prepares sorted_by_docs and sorted_by_scores for threshold_algo() and calls it """

    if index.indexed:
        sorted_by_docs = {} # Extrait de l'inverted index ne contenant que les termes de la requete
        sorted_by_scores = {} # Dictionnaire qui associe aux termes de la requete la liste des documents dans laquelle ils apparaissent triee par score decroissant
        terms = [] # Termes de la requete presents dans l'inverted file
        query_terms = get_terms(query)
        # Construction des deux indexs : tries par document et par score
        if index.in_memory:
            for term in query_terms:
                if term in index.inv_index:
                    terms.append(term)
                    sorted_by_docs[term] = index.inv_index[term]
                    sorted_by_scores[term] = sorted(sorted_by_docs[term], key=sorted_by_docs[term].__getitem__, reverse=True)
        else:
            for term in query_terms:
                if term in index.dict_terms_offset:
                    terms.append(term)
                    text = linecache.getline('InvertedFile', index.dict_terms_offset[term])
                    sorted_by_docs[term] = text_to_pl(text)
                    sorted_by_scores[term] = sorted(sorted_by_docs[term], key=sorted_by_docs[term].__getitem__, reverse=True)
        if len(terms) > 0:
            return threshold_algo(terms, sorted_by_docs, sorted_by_scores, k)
        else:
            print "None of the query terms has been found."
    else:
        print "No index in memory nor loaded from file."
    return False

def threshold_algo(terms, sorted_by_docs, sorted_by_scores, k):
    """ Runs threshold algorithm """

    t = 1
    smallest_score = 0 # Plus petit score parmis les documents du top-k
    top_k = []
    docs_met = set()
    remaining_terms = set(terms)
    while (t > smallest_score or len(top_k) < k) and len(remaining_terms) > 0: # Iteration sur les documents tries par score
        t = 0 # Seuil : score maximal atteignable par les documents pas encore etudies
        terms = list(remaining_terms)
        for term in terms:
            if len(sorted_by_scores[term]): # Is this test really usefull ?
                doc = sorted_by_scores[term].pop(0) # Document avec le meilleur score pour ce terme
                if len(sorted_by_scores[term]):
                    t += sorted_by_docs[term][sorted_by_scores[term][0]] # Mise a jour du seuil
                else:
                    remaining_terms.remove(term)
                if doc not in docs_met: # Si c'est la premiere fois qu'on le rencontre
                    docs_met.add(doc)
                    score = 0
                    # Calcul du score du document
                    for a_term in terms:
                        if doc in sorted_by_docs[a_term]:
                            score += sorted_by_docs[a_term][doc]
                    # Modification eventuelle des top-k documents
                    # print "Doc " + str(doc) + " has a score of " + str(score)
                    if len(top_k) < k:
                        top_k.append((doc, score))
                        top_k.sort(key=lambda x: x[1])
                    else:
                        if score > top_k[0][1]:
                            top_k.pop(0)
                            top_k.append((doc, score))
                            top_k.sort(key=lambda x: x[1])
                            # print "New top-k :"
                            # print top_k
                    smallest_score = top_k[0][1]
        # print "t = " + str(t) + " > smallest score = " + str(smallest_score) + " ? " + str(t > smallest_score)
    return top_k

########## NAIVE ALGORITHM ##########

def naive_disj_query(index, query):
    """ X """

    if index.indexed:
        if index.in_memory:
            return find_docs_disj_memory(index.inv_index, query)
        else:
            return find_docs_disj_merge_based(index, query)
    else:
        print "No index in memory nor loaded from file."
    return False


#Token recherche disjonctive ("OU")
def find_docs_disj_merge_based(index, query):
    """ Returns a dict {doc id: score} where score is the sum of scores for each term of the query present in the document """

    terms = get_terms(query)
    results = {}
    for term in terms:
        if term in index.dict_terms_offset:
            offset = index.dict_terms_offset[term]
            line = linecache.getline("InvertedFile", offset)
            pl = index.text_to_pair_list(line)
            for doc, score in pl:
                if(doc in results):
                    results[doc] += score
                else:
                    results[doc] = score
    return results

#Token recherche disjonctive ("OU")
def find_docs_disj_memory(inverted_index, query):
    """ Returns a dict {doc id: score} where score is the sum of scores for each term of the query present in the document """

    terms = get_terms(query)
    results = {}
    for term in terms:
        if term in inverted_index:
                for doc in inverted_index[term]:
                    if(doc in results):
                        results[doc] += inverted_index[term][doc]
                    else:
                        results[doc] = inverted_index[term][doc]
    return results

#Token recherche conjonctive ("ET")
# def find_docs_conj_memory(index,query):
#     """ Returns a dict {doc id: score} where score is the sum of scores for each term. Every term of the query must be in the document """

#     terms = get_terms(query)
#     postingLists = []
#     #On recupere les PL de chaque terme
#     for term in terms:
#         if term in index.dict_terms_offset:
#             offset = index.dict_terms_offset[term]
#             line = linecache.getline("InvertedFile", offset)
#             pl = index.text_to_pair_list(line)
#             postingLists += pl
#     results = {}
#     last = []
#     if len(postingLists)>0:
#         last = postingLists.pop()
#     for doc0, score0 in last : #Boucle sur les clefs dans results
#         for doc,score in postingLists :
#             if doc == doc :
#                 doc_score += PL[doc]
#             else :
#                 doc_score = 0
#                 break
#         if doc_score != 0 :
#             results[doc0] = doc_score
#     return results

# def popSmallestDict(dictList):
#     """ X """
#
#     smallest = min(dictList)
#     dictList.remove(smallest)
#     return smallest



# def findDocsSortedByScoreDisj(inverted_index,query):
#     """ X """
#
#     nonSortedDict = findDocsDisj(inverted_index,query)
#     sortedDict = sortDict(nonSortedDict)
#     return (sortedDict, nonSortedDict)


# def findDocsSortedByScoreConj(inverted_index,query):
#     """ X """
#
#     nonSortedDict = findDocsConj(inverted_index,query)
#     sortedDict = sortDict(nonSortedDict)
#     return (sortedDict, nonSortedDict)


########## PRINTING FUNCTIONS ##########

def sort_and_print_dict(dict_score):
    """ Orders by score (DESC) and prints a list of pairs {doc_id: score} """

    sorted_list = sorted(dict_score, key=dict_score.__getitem__, reverse=True)
    print_docs_ordered_by_scores(dict_score, sorted_list)

def print_docs_ordered_by_scores(dict_score, sorted_list):
    """ Prints a list of pairs {doc id: score} already sorted by score (DESC) """

    if len(sorted_list) == 0:
        print("Terms of query not found in document(s)")
    for doc in sorted_list :
        print("{0} : {1}".format(doc, str(dict_score[doc])))
# =======
# #Returns a dict {doc id: score} where score is the sum of scores for each term. Every term of the query must be in the document
# def findDocsConj(index,query):
#
# 	queryList = getTerms(query)
# 	postingLists = []
# 	#On recupere les PL de chaque terme
# 	for word in queryList:
# 		if word in index.dictTermsOffset:
# 			offset = index.dictTermsOffset[word]
# 			line = linecache.getline("InvertedFile1", offset)
# 			pl = index.text_to_pair_list(line)
# 			postingLists += pl
#
# 	request = {}
# 	last = []
# 	if len(postingLists)>0:
# 		last = postingLists.pop()
#
# 	for doc0, score0 in last : #Boucle sur les clefs dans results
# 		for doc,score in postingLists :
# 			if doc == doc :
# 				doc_score += PL[doc]
# 			else :
# 				doc_score = 0
# 				break
# 		if doc_score != 0 :
# 			request[doc0] = doc_score
# 	return response
#
# def findDocsSortedByScoreDisj(invertedFile,query):
# 	nonSortedDict = findDocsDisj(invertedFile,query)
# 	sortedDict = sortDict(nonSortedDict)
# 	return (sortedDict, nonSortedDict)
#
#
# def findDocsSortedByScoreConj(invertedFile,query):
# 	nonSortedDict = findDocsConj(invertedFile,query)
# 	sortedDict = sortDict(nonSortedDict)
# 	return (sortedDict, nonSortedDict)
#
# if __name__=='__main__':
#
# 	#Prompt for query terms
# 	#Here specify the location of the textfiles to search upon
#     if os.path.isfile("ExtraFile") == True and os.path.isfile("InvertedFile") == True:
#         index = indexing.Index()
#         index.extra_file_handler()
#     else:
#         start = time.clock()
#         index = indexing.Index("../../../latimes/la010189")
#         index.create_index_from_file_format_merged_based()
#         end = time.clock()
#         print "Elapsed Time: {} seconds".format(end - start)
#     query = raw_input("Entrez votre recherche : ")
#     while(query != "exit"):
#         print "Resutat recherche disjonctive:"
#         print "requetage naif"
#
#         dicOfDocs = findDocsDisjMergedBased(index, query)
#         sortAndPrintDict(dicOfDocs)
#
#         print "requetage faggins"
#
#         threshold_algo(index, query,10)
#
#         query = raw_input("Entrez votre recherche : ")
#
# >>>>>>> master


if __name__=='__main__':

    index = indexing.Index(memory_limit = 1000000)
    if not index.use_existing_index():
        start = time.clock()
        index.index("../../latimes/la010189")
        end = time.clock()
        print "Elapsed Time: {} seconds".format(end - start)

    query = raw_input("Entrez votre recherche : ")
    while(query != "exit"):
        # print "Resutat recherche disjonctive:"
        print "Requetage naif :"
        dic_of_docs = naive_disj_query(index, query)
        sort_and_print_dict(dic_of_docs)
        print "Requetage threshold algo :"
        top_k = query_with_threshold_algo(index, query, 5)
        if top_k:
            print top_k
        else:
            print "No result :/"
        query = raw_input("Entrez votre recherche : ")



    #Token recherche conjonctive ("ET")
    #query = raw_input("Entrez votre recherche disjonctive: ")
    #findDocsSortedByScoreConj(inverted_index,query)
