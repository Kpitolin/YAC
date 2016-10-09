#YAC : Yet another Crawler

## What is YAC?
Yac is a textfile crawler. It allows you to query a file or a set of file formatted in the folling way and returning the document entities sorted by relevance  : 

```
<DOC>
<DOCID> {AN_ID} </DOCID>
{Here content organized in HTML tags} 
</DOC>
```

## How do I install it?
Install [**Python 2.7**](https://www.python.org/download/releases/2.7/)

You must install the following packages to get going : 

- nltk
- blist

Follow the instructions [here](http://www.nltk.org/install.html) for nltk.

Install ~~~Every?~~~ corpus.
 
Then execute ```pip install blist```.
## How do I use it?
### From the command line
For now,

1. modify the path of the file in `querying.py` line 62 to a file (or file format) in your path you want to query against. **Remember : it's the relative path from the directory you're in in the command line.**
2. Once at project root, execute `python yac/querying.py`. It will prompt you to ask the terms of your query and print for all the documents `{doc id} : {score}` sorted by aggregation  of scores of terms in query

###Programmatically
The steps :

1. Tokenize the text in file (we have two methods but for now, we use split and remove the punctuation)
- Create inverted index
- Compute final scores of each term
- Search in inverted index most relevant docs from terms in query
- Sort them and print the result

Example of inverted index : ```{ "term 1": {1:1}, "term 2": {3:1}, "term 3":{2:1, 4:1}}```.
The inner dictionnary is structured that way : ```{doc_id:score}``` both are int for now
    
    index = indexing.Index("pathToFileORfilepathFormat") # Object initialization
    index.createIndexFromFileFormat() # 1 + 2
    index.calculate_all_scores_memory() # 3
    query = raw_input("Entrez votre recherche disjonctive: ")
    print "Resutat recherche disjonctive:"
    dicOfDocs = querying.findDocsDisj(index.inv_index, query) # 4
    querying.sortAndPrintDict(dicOfDocs) # 5
