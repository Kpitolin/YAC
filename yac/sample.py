import time
import tokenization
import indexing
import querying

# this script just tokenizes a file (relative path from the directory you're in in the command line)
# if you are at ./YAC and the file is in the folder above, pathToFile = ../la010189 for example
start = time.clock()
index = indexing.Index("../latimes/la010189") # Object initialization
index.createIndexFromFileFormat() # 1 + 2
index.saveIndexToFile()
index.calculate_all_scores_memory() # 3
query = raw_input("Entrez votre recherche disjonctive: ")
print "Resutat recherche disjonctive:"
dicOfDocs = querying.findDocsDisj(index.inv_index, query)
querying.sortAndPrintDict(dicOfDocs)


end = time.clock()

print "Elapsed Time: {} seconds".format(end - start)
