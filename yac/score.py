import sys
import re
import math
import struct
from nltk.corpus import stopwords

#Récupérer les termes dans la requete (faire le stemming et enlever les mots vides)
def getTerms(query):
    stop_words=stopwords.words('english')
    query=query.lower()
    query=re.sub(r"[^a-z0-9 ]",' ',query) #remplacer les caractères non-alphabetiques par espace
    words=[x for x in query.split() if x not in stop_words]  #eliminer les mots vides
    terms=[porter_stemmer.stem(word) for word in words]
    return terms

# Retourne un dictionnaire dont la clé est le terme et la valeur est la fréquence de chaque terme dans la requete
def term_frequency_query(terms):
    term_freq_dict = sorteddict({})
    for term in terms:
        try:
            term_freq_dict[term] += 1
        except KeyError:
            term_freq_dict[term] = 1
    return term_freq_dict


#Calculer idf du terme
def inverse_document_frequency(nb_docs_containing, nb_docs):
    return math.log10(nb_docs/nb_docs_containing)

def  calculertf_idf(query,f_term,f_docID ):
    term_weight_query_dict = {}  # Le tf-idf de chaque terme dans la requete
    term_freq_query_dict = term_frequency_query(terms) # Récuperer les fréquences de chaque terme dans la requete
    # Ouvrir le fichier index binaire en mode lecture en binaire
    with open(f_index, "rb") as f_index_read:
        # Ouvrir le fichier de vocabulaires
        with open(f_term, "r") as f_term_read:
            # Lire le fichier de vocabulaires ligne par ligne (autrement dit terme par terme)
            for term_line in f_term_read:
                term_line_arr = term_line.split("|")
                term = term_line_arr[0]
                # Si on trouve un terme, récupérer sa postingslist et calculer les valeurs
                if term in set_terms:
                    count_found_term += 1
                    nb_docs_containing_term = int(term_line_arr[1])  # Le nombre de docs contient le terme
                    idf_term = inverse_document_frequency(nb_docs_containing_term, nb_docs)  # Calculer idf du terme
                    term_weight_query_dict[term] = term_freq_query_dict[term] * idf_term  # Calculer tf-idf du terme dans la requete

                if count_found_term == len(set_terms):
                    break  # Si on trouve déjà toutes la postingslist de chaque terme, arrête la lecture

    return term_weight_query_dict



