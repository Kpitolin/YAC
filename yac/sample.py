import time
import tokenization
import indexing
import querying

# This script just tokenizes a file (relative path from the directory you're in in the command line)
# If you are at ./YAC and the file is in the folder above, pathToFile = ../la010189 for example
start = time.clock()

#index = indexing.Index("../../latimes/la01*89") # Object initialization
#index.create_index_from_file_format() # 1 + 2
#index.calculate_all_scores_memory() # 3

querying.threshold_algo(querying.get_terms("soviet moscow"), 3)

#query = raw_input("Entrez votre recherche disjonctive: ")
#print "Resutat recherche disjonctive:"
#dic_of_docs = querying.find_docs_disj(index.inv_index, query)
#querying.sort_and_print_dict(dic_of_docs)


end = time.clock()

print "Elapsed Time: {} seconds".format(end - start)
