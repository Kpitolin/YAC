# coding: utf-8

import sys
import re
import math
import struct
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from blist import sorteddict
porter_stemmer = PorterStemmer()

def getTerms(query, with_stemming = False):
    stop_words=stopwords.words('english')
    query=query.lower()
    query=re.sub(r"[^a-z0-9 ]",' ',query)
    words=[x for x in query.split() if x not in stop_words]
    if with_stemming:
        terms=[porter_stemmer.stem(word) for word in words]
    else:
        terms=words
    return terms


def term_frequency_query(terms):
    term_freq_dict = sorteddict({})
    for term in terms:
        try:
            term_freq_dict[term] += 1
        except KeyError:
            term_freq_dict[term] = 1
    return term_freq_dict


def inverse_document_frequency(nb_docs_containing, nb_docs):
    return math.log10(nb_docs/nb_docs_containing)

def  calculertf_idf(query,f_term,f_index,f_docID ):
    terms = getTerms(query)
    set_terms = set(terms)
    term_freq_query_dict = term_frequency_query(terms)  # Récuperer les fréquences de chaque terme dans la requete
    term_weight_query_dict = {}
    term_freq_query_dict = term_frequency_query(terms)
    count_found_term = 0  # Le nombre de terme dont la postingslist est déjà trouvée
    norm_doc_dict = {}  # La norme du vecteur construit par les fréquences de chaque terme dans chaque doc
    nb_docs = 0
    # Ouvrir le fichier de réindexation des docID et lire ligne par ligne et stocker les valeurs de norme de chaque doc
    with open(f_docID) as f_docID_read:
        for doc_line in f_docID_read:
            nb_docs += 1
            doc_line_arr = doc_line.split(":")
            doc_id = int(doc_line_arr[0])
            norm_doc = float(doc_line_arr[1].split("|")[
                                 3])  # La norme du vecteur construit par les fréquences de chaque terme dans le doc dont l'id est doc_id
            norm_doc_dict[doc_id] = norm_doc  # Stocker la norme dans le dictionnaire dont la clé est le docid

    with open(f_index, "rb") as f_index_read:

        with open(f_term, "r") as f_term_read:

            for term_line in f_term_read:
                term_line_arr = term_line.split("|")
                term = term_line_arr[0]

                if term in set_terms:
                    count_found_term += 1
                    nb_docs_containing_term = int(term_line_arr[1])
                    idf_term = inverse_document_frequency(nb_docs_containing_term, nb_docs)
                    term_weight_query_dict[term] = term_freq_query_dict[term] * idf_term

                if count_found_term == len(set_terms):
                    break
    return term_weight_query_dict



