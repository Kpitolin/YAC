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


Install the stopwords corpus:
In python, execute

    nltk.download()
    d #When prompted what action to take, d is for Download
    Download which package (l=list; x=cancel)?
    Identifier> stopwords 

And it should install.


Then execute ```pip install blist```.
## How do I use it?
At project root, execute python yac/main.py
You can prompt either : 

    > index [-scrt ] <path>
    > load
    > query (-a | -o | -e | -d) <query>...
    > help

To Index, you can add one or a combination of this options:

    -t   Filter tags
    -s   With stemming
    -r   Remove stopword
    -c   Case sensitive

To query you should pick one of this options: 

    -a   Make conjunctive request with naive algorithm
    -o   Make disjunctive request with naive algorithm
    -e  Make conjunctive request with fagin algorithm
    -d  Make disjunctive request with fagin algorithm


If you ever forget, you can always prompt help ! 

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

## How do I test it?

You can run all tests by executing this command at project root: ```python -m unittest discover```
Another way would be running the tests module by module following this format :  ```python -m unittest package.module_name```.

For example, here, we run all tests of the test_indexing module (tests package):

    python -m unittest tests.test_indexing
