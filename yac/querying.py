"""This file define a mock of an inverted file and a simple querying algorithm """
import time
import re
import indexing, tokenization
from sys import argv
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
porter_stemmer = PorterStemmer()

#inverted file
inverted_file = { "and": {1:1}, "aquarium": {3:1}, "are":{3:1, 4:1},
"around": {1:1}, "as": {2:1},"both": {1:1},
"bright": {3:1},"coloration": {3:1, 4:1},"derives": {4:1},
"due": {3:1},"environements": {1:1},"fish": {1:2, 2:3, 3:2, 4:7},
"fishkeepers": {2:1},"found": {1:1},"fresh": {2:1}, "freshwater": {1:1, 4:1},
"from": {4:1} }

def threshold_algo(inv_index, query_terms, k):
    sorted_by_docs = {} # Extrait de l'inverted index ne contenant que les termes de la requete
    sorted_by_scores = {} # Dictionnaire qui associe aux termes de la requete la liste des documents dans laquelle ils apparaissent triee par score decroissant
    terms = [] # Termes de la requete presents dans l'inverted file
    for term in query_terms: # Construction des deux index : tries par document et par score
        if term in inv_index:
            terms.append(term)
            sorted_by_docs[term] = inv_index[term]
            sorted_by_scores[term] = sorted(sorted_by_docs[term], key=inv_index[term].__getitem__, reverse=True)
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
        query = query.lower()
    query = re.sub(r"[^a-zA-Z0-9 ]",' ',query)
    words = [x for x in query.split() if not remove_stopwords or x.lower() not in stop_words]
    terms = []
    if with_stemming:
        terms = [porter_stemmer.stem(word) for word in words]
    else:
        terms = words
    return terms

def sort(dict_score):
    """Returns a list of the doc ids sorted by score"""

    sorted_list = sorted(dict_score, key=dict_score.__getitem__, reverse=True)
    return sorted_list

def print_doc_ordered_by_scores(dict_score, sorted_list):
    """Prints a list of pairs {doc id: score} already sorted by score (DESC)"""

    if len(sorted_list) == 0:
        print("Terms of query not found in document(s)")
    for doc in sorted_list :
        print("{0} : {1}".format(doc,str(dict_score[doc])))

def sort_and_print_dict(dict_score):
    """Orders by score (DESC) and prints a list of pairs {doc id: score}"""

    sorted_list = sort(dict_score)
    print_doc_ordered_by_scores(dict_score, sorted_list)


# Token recherche disjonctive ("OU")
def find_docs_disj(inverted_file, query):
    """Returns a dict {doc id: score} where score is the sum of scores for each term of the query present in the document"""
    query_list = get_terms(query)
    request = {}
    for word in query_list:
        if word in inverted_file:
                for doc in inverted_file[word]:
                    if(doc in request):
                        request[doc] += inverted_file[word][doc]
                    else:
                        request[doc] = inverted_file[word][doc]
    return request

def pop_smallest_dict(dict_list):
    smallest = min(dict_list)
    dict_list.remove(smallest)
    return smallest

# Token recherche conjonctive ("ET")
def find_docs_conj(inverted_file, query):
    """Returns a dict {doc id: score} where score is the sum of scores for each term. Every term of the query must be in the document"""
    query_list = get_terms(query)
    posting_lists = []
    # On recupere les PL de chaque terme
    for word in query_list :
        if word in inverted_file:
            posting_lists += [inverted_file[word]]

    request = {}
    last = []
    if len(posting_lists) > 0:
        last = posting_lists.pop()

    for doc in last : # Boucle sur les clefs dans results
        doc_score = last[doc]
        for PL in posting_lists :
            if PL.has_key(doc) :
                doc_score += PL[doc]
            else :
                doc_score = 0
                break
        if doc_score != 0 :
            request[doc] = doc_score
    return request

def find_docs_sorted_by_score_disj(inverted_file, query):
    non_sorted_dict = find_docs_disj(inverted_file, query)
    sorted_dict = sort_dict(non_sorted_dict)
    return (sorted_dict, non_sorted_dict)


def find_docs_sorted_by_score_conj(inverted_file, query):
    non_sorted_dict = find_docs_conj(inverted_file, query)
    sorted_dict = sort_dict(non_sorted_dict)
    return (sorted_dict, non_sorted_dict)

if __name__=='__main__':
    # Prompt for query terms
    # Here specify the location of the textfiles to search upon
    start = time.clock()

    index = indexing.Index("../../../../Downloads/latimes/la010189")
    index.create_index_from_file_format()
    index.calculate_all_scores_memory()
    query = raw_input("Entrez votre recherche disjonctive: ")
    print "Resutat recherche disjonctive:"
    dic_of_docs = find_docs_disj(index.inv_index, query)
    sort_and_print_dict(dic_of_docs)
    end = time.clock()

    print "Elapsed Time: {} seconds".format(end - start)


    # Token recherche conjonctive ("ET")
    # query = raw_input("Entrez votre recherche disjonctive: ")
    # find_docs_sorted_by_score_conj(inverted_file,query)
