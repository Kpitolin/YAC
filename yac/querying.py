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
    for item in pair_list:
        doc_id, score = item.split(",")
        pl[doc_id] = float(score)
    return pl

def query_with_threshold_algo(index, query, k, disj=True):
    """ Prepares sorted_by_docs and sorted_by_scores for threshold_algo() and calls it """

    if index.indexed:
        sorted_by_docs = {} # Extrait de l'inverted index ne contenant que les termes de la requete
        sorted_by_scores = {} # Dictionnaire qui associe aux termes de la requete la liste des documents dans laquelle ils apparaissent triee par score decroissant
        terms = [] # Termes de la requete presents dans l'inverted index
        query_terms = set(get_terms(query))
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
            return threshold_algo(terms, sorted_by_docs, sorted_by_scores, k, disj)
        else:
            print "None of the query terms has been found."
    else:
        print "No index in memory nor loaded from file."
    return False


def threshold_algo(terms, sorted_by_docs, sorted_by_scores, k, disj):
    """ Runs threshold algorithm """

    t = 1
    smallest_score = 0 # Plus petit score parmis les documents du top-k
    top_k = []
    docs_met = set()
    remaining_terms = terms #
    while (t > smallest_score or len(top_k) < k) and len(remaining_terms): # Iteration sur les documents tries par score
        t = 0 # Seuil : score maximal atteignable par les documents pas encore etudies
        terms = list(remaining_terms)
        for term in terms:
            if len(sorted_by_scores[term]): # Is this test really usefull ?
                doc = sorted_by_scores[term].pop(0) # Document avec le meilleur score pour ce terme
                if len(sorted_by_scores[term]):
                    t += sorted_by_docs[term][sorted_by_scores[term][0]] # Mise a jour du seuil
                else:
                    if disj:
                        remaining_terms.remove(term)
                    else:
                        remaining_terms = list() # In conj queries
                if doc not in docs_met: # Si c'est la premiere fois qu'on le rencontre
                    docs_met.add(doc)
                    score = 0
                    # Calcul du score du document
                    doc_has_all_terms = True # Used in conj queries
                    for a_term in terms:
                        if doc in sorted_by_docs[a_term]:
                            score += sorted_by_docs[a_term][doc]
                        else:
                            doc_has_all_terms = False
                    # Modification eventuelle des top-k documents
                    if doc_has_all_terms or disj:
                        if len(top_k) < k:
                            top_k.append((doc, score))
                            top_k.sort(key=lambda x: x[1])
                        else:
                            if score > top_k[0][1]:
                                top_k.pop(0)
                                top_k.append((doc, score))
                                top_k.sort(key=lambda x: x[1])
                    if len(top_k):
                        smallest_score = top_k[0][1]
                    else:
                        smallest_score = 0
    return top_k

########## NAIVE ALGORITHM DISJUNCTIVE ##########

def query_with_naive_disj_algo(index, query):
    """ X """

    terms = set(get_terms(query))
    if index.indexed:
        if index.in_memory:
            return naive_disj_algo(index.inv_index, terms)
        else:
            # Reconstruction of an in-memory inverted index from the file InvertedFile, containing the terms of the query
            inv_index_reconstructed = {}
            for term in terms:
                if term in index.dict_terms_offset:
                    offset = index.dict_terms_offset[term]
                    line = linecache.getline("InvertedFile", offset)
                    inv_index_reconstructed[term] = text_to_pl(line)
            return naive_disj_algo(inv_index_reconstructed, terms)
    else:
        print "No index in memory nor loaded from file."
    return False

#Token recherche disjonctive ("OU")
def naive_disj_algo(inverted_index, terms):
    """ Returns a dict {doc id: score} where score is the sum of scores for each term of the query present in the document """

    results = {}
    for term in terms:
        if term in inverted_index:
                for doc in inverted_index[term]:
                    if(doc in results):
                        results[doc] += inverted_index[term][doc]
                    else:
                        results[doc] = inverted_index[term][doc]
    return results


########## NAIVE ALGORITHM CONJUNCTIVE ##########

def query_with_naive_conj_algo(index, query):
    """ X """

    terms = set(get_terms(query))
    if index.indexed:
        if index.in_memory:
            return naive_conj_algo(index.inv_index, terms)
        else:
            # Reconstruction of an in-memory inverted index from the file InvertedFile, containing the terms of the query
            inv_index_reconstructed = {}
            for term in terms:
                if term in index.dict_terms_offset:
                    offset = index.dict_terms_offset[term]
                    line = linecache.getline("InvertedFile", offset)
                    inv_index_reconstructed[term] = text_to_pl(line)
            return naive_conj_algo(inv_index_reconstructed, terms)
    else:
        print "No index in memory nor loaded from file."
    return False

#Token recherche conjonctive ("ET")
def naive_conj_algo(inverted_index, terms):
    """ Returns a dict {doc id: score} where score is the sum of scores for each term. Every term of the query must be in the document """

    terms = list(terms)
    if terms[0] not in inverted_index:
        print "Term '" + terms[0] + "' not found."
        return {}
    remaining_docs = set(inverted_index[terms[0]].keys())
    scores = {}
    # Initialisation of scores
    for doc in remaining_docs:
        scores[doc] = 0.
    #
    for term in terms:
        if term in inverted_index:
                docs = list(remaining_docs)
                for doc in docs:
                    if doc in inverted_index[term]:
                        scores[doc] += inverted_index[term][doc]
                    else:
                        remaining_docs.remove(doc)
        else:
            print "Term '" + term + "' not found."
            return {}
    # Get the score of remaining documents
    results = {}
    for doc in remaining_docs:
        results[doc] = scores[doc]
    return results


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

# TODO : We may need to get a set of query terms, if not we can have some problems executing the algos

if __name__=='__main__':

    index = indexing.Index(memory_limit = 1000000)
    if not index.use_existing_index():
        start = time.clock()
        index.index_files("../../latimes/la010189")
        end = time.clock()
        print "Elapsed Time: {} seconds".format(end - start)

    query = raw_input("Entrez votre recherche : ")
    while(query != "exit"):
        # print "Resutat recherche disjonctive:"
        start = time.clock()
        print "Requetage naif disjonctif :"
        dic_of_docs = query_with_naive_disj_algo(index, query)
        sort_and_print_dict(dic_of_docs)
        end = time.clock()
        print "Elapsed Time: {} seconds".format(end-start)
        print "Requetage threshold disjonctif :"
        start = time.clock()
        top_k = query_with_threshold_algo(index, query, 10)
        if top_k:
            print top_k
        else:
            print "No result for threshold disjunctive."
        end = time.clock()
        print "Elapsed Time: {} seconds".format(end-start)
        print "Requetage naif conjonctif :"
        start = time.clock()
        dic_of_docs = query_with_naive_conj_algo(index, query)
        sort_and_print_dict(dic_of_docs)
        end = time.clock()
        print "Elapsed Time: {} seconds".format(end-start)
        print "Requetage threshold conjonctif :"
        start = time.clock()
        top_k = query_with_threshold_algo(index, query, 10, disj=False)
        if top_k:
            print top_k
        else:
            print "No result for threshold disjunctive."
        end = time.clock()
        print "Elapsed Time: {} seconds".format(end-start)
        query = raw_input("Entrez votre recherche : ")
