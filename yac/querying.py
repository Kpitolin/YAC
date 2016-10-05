""" this file define a mock of an inverted file and a simple querying algorithm """

#inverted file
invertedFile = { "and": {"1":1}, "aquarium": {"3":1}, "are":{"3":1, "4":1},
"around": {"1":1}, "as": {"2":1},"both": {"1":1},
"bright": {"3":1},"coloration": {"3":1, 4:1},"derives": {"4":1},
"due": {"3":1},"environements": {"1":1},"fish": {"1":2, "2":3, "3":2, "4":7},
"fishkeepers": {"2":1},"found": {"1":1},"fresh": {"2":1}, "freshwater": {"1":1, "4":1},
"from": {"4":1} }

 #Token recherche
query = "and as both"

def findDocsSortedByScore(invertedFile, query):
	queryList = query.split()
	request = {}
	for word in queryList :
		for doc in invertedFile[word] :
			if(doc in request):
				request[doc] += invertedFile[word][doc]
			else:
				request[doc] = invertedFile[word][doc]

	sortedRequest = sorted(request, key=request.__getitem__, reverse=True)

	for doc in sortedRequest :
		print(doc+ ":" + str(request[doc]))	

findDocsSortedByScore(invertedFile, query) 	