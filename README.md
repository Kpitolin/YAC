#YAC : Yet another Crawler

## What is YAC?
Yac is a textfile crawler. It allows you to query a file or a set of file formatted in the folling way and returning the document entities sorted by relevance  : 

```
<DOC>
<DOCID> {AN_ID} </DOCID>
{Here content organized in HTML tags} 
</DOC>
```
## How does it work ?

The general steps of YAC are as follows:

1. Tokenizes the text in file (we have two methods but for now, we use split and remove the punctuation)
- Creates and inverted index
- Computes final scores of each term
- Searches in inverted index most relevant docs from terms in query
- Sorts them and prints the result

We use different methods for both tokenization, indexing and querying. Those details will be discussed in a document named Implementation Details. 

## How do I install it?
Install [**Python 2.7**](https://www.python.org/download/releases/2.7/)

You must install the following packages to get going : 

- nltk
- blist
- docopt

Follow the instructions [here](http://www.nltk.org/install.html) for nltk.


Install the stopwords corpus:
In python, execute

    nltk.download()
    d #When prompted what action to take, d is for Download
    Download which package (l=list; x=cancel)?
    Identifier> stopwords 

And it should install.

Then execute ```pip install blist``` and ```pip install docopt```.

## How do I use it?
At project root, execute python yac/main.py
You can prompt either : 

    > index [-scrt ] <path> [-m <memory_limit>]
    > load
    > query [-scr ] (-a | -o | -e | -d) <query>...
    > help

Basic usage being : you index then you query. If you just started the program, have an index file (InvertedFile) and an offset file (Offsets) you can load them into memory to then query. You must specify the same tokenization option in the index and the query command for the result to be relevant.

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

## How do I test it?

**Before running the tests, beware of something important. As tests generates a large number of files, all partial index files, offsets or inverted index will be removed from the directory from which the test are executed.**

You can run all tests by executing this command at project root: ```python -m unittest discover```
Another way would be running the tests module by module following this format :  ```python -m unittest package.module_name```.

For example, here, we run all tests of the test_indexing module (tests package):

    python -m unittest tests.test_indexing
