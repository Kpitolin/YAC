""" this file define a mock of an inverted file and a simple querying algorithm """

from sys import argv

#inverted file
invertedFile = { "and": {"1":1}, "aquarium": {"3":1}, "are":{"3":1, "4":1},
"around": {"1":1}, "as": {"2":1},"both": {"1":1},
"bright": {"3":1},"coloration": {"3":1, 4:1},"derives": {"4":1},
"due": {"3":1},"environements": {"1":1},"fish": {"1":2, "2":3, "3":2, "4":7},
"fishkeepers": {"2":1},"found": {"1":1},"fresh": {"2":1}, "freshwater": {"1":1, "4":1},
"from": {"4":1} }


 #Prompt for query terms
query = raw_input("Entrez votre recherche disjonctive: ")


 #Token recherche disjonctive ("OU")

def sortAndPrintDict(dict):
    sortedDict = sorted(dict, key=dict.__getitem__, reverse=True)
    for doc in sortedDict :
		print(doc+ ":" + str(dict[doc]))

def findDocsSortedByScore(invertedFile, query):
	queryList = query.split()
	request = {}
	for word in queryList :
		for doc in invertedFile[word] :
			if(doc in request):
				request[doc] += invertedFile[word][doc]
			else:
				request[doc] = invertedFile[word][doc]
	sortAndPrintDict(request)

print "Resutat recherche disjonctive:"
findDocsSortedByScore(invertedFile, query)

#Token recherche conjonctive ("ET")
query = raw_input("Entrez votre recherche disjonctive: ")

def popSmallestDict(dictList):
    smallest = min(dictList)
    dictList.remove(smallest)
    return smallest

def findDocsSortedByScoreConj(invertedFile,query):
    queryList = query.split()
    postingLists = []
    #On recupere les PL de chaque terme
    for word in queryList :
        postingLists += [invertedFile[word]]
    last = postingLists.pop()
    request = {}

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

    sortAndPrintDict(request)

findDocsSortedByScoreConj(invertedFile,query)
