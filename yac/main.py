"""Main

Usage:
> index [-scrt ] <path> [-m <memory_limit>]
> load
> query [-scr ] (-a | -o | -e | -d) <query>...
> help

Options:
-t   Filter tags
-s   With stemming
-r   Remove stopword
-c   Case sensitive
-a   Make conjunctive request with naive algorithm
-o   Make disjunctive request with naive algorithm
-e  Make conjunctive request with fagin algorithm
-d  Make disjunctive request with fagin algorithm
"""

import time
import re
from indexing import *
from querying import *
import os.path
from sys import argv
from docopt import docopt, DocoptExit

if __name__=='__main__':
    while True : 
        try:
            command = raw_input(">")
            arguments = docopt(__doc__, argv=command)
            memory_limit = 1000000 # 1GB is default
            if arguments['index']:
                filter_tags=False
                remove_stopwords=False
                case_sensitive=False
                with_stemming=False
                if arguments['-t'] == True:
                    filter_tags=True
                if arguments['-r'] == True:
                    remove_stopwords=True
                if arguments['-c'] == True:
                    case_sensitive=True
                if arguments['-s'] == True:
                    with_stemming=True
                if arguments['-m'] == True:
                    try:
                        memory_limit = int(arguments["<memory_limit>"])
                    except ValueError:
                        print "Unexpected memory limit parameter. It should be an int."
                index = Index(memory_limit, filter_tags, remove_stopwords, case_sensitive, with_stemming)    
                start = time.clock()
                index.index_files(arguments["<path>"])
                end = time.clock()
                print "Elapsed Time: {} seconds".format(end - start)
            elif arguments['load']:    
                index = Index(memory_limit, False, False, False, False)
                if index.use_existing_index():
                    print("Index loaded")
                else :
                    print("No Index to be load, create Index!")
            elif arguments['query']:
                query = arguments["<query>"]
                try: 
                    start = time.clock()
                    remove_stopwords=False
                    case_sensitive=False
                    with_stemming=False
                    if arguments['-r'] == True:
                        remove_stopwords=True
                    if arguments['-c'] == True:
                        case_sensitive=True
                    if arguments['-s'] == True:
                        with_stemming=True

                    if arguments['-a'] == True:
                        dic_of_docs = query_with_naive_conj_algo(index, " ".join(query), remove_stopwords, case_sensitive,with_stemming)
                        sort_and_print_dict(dic_of_docs)
                       
                    elif arguments['-e'] == True:
                        top_k = query_with_threshold_algo(index, " ".join(query), 50, False, remove_stopwords, case_sensitive,with_stemming)
                        if top_k:
                            print sort_and_print_pair_list(top_k)
                        else:
                            print "No result for threshold disjunctive."
                    elif arguments['-d'] == True:
                        top_k = query_with_threshold_algo(index, " ".join(query), 50, True,remove_stopwords, case_sensitive,with_stemming)
                        if top_k:
                            print sort_and_print_pair_list(top_k)
                        else:
                            print "No result for threshold disjunctive."
                    else:
                        dic_of_docs = query_with_naive_disj_algo(index, " ".join(query), remove_stopwords, case_sensitive,with_stemming)
                        sort_and_print_dict(dic_of_docs)
                    end = time.clock()
                    print "Elapsed Time: {} seconds".format(end-start)    
                except NameError as e:
                    print "No existing index : {}".format(e)
            elif arguments['help']:
                print("Usage:")
                print("index [-scrt ] <path> [-m <memory_limit>]")
                print("load")
                print("query [-scr ] (-a | -o | -e | -d) <query> ")
                print("help")
                print("Options:")
                print("-t   Filter tags")
                print("-s   With stemming")
                print("-r   Remove stopword")
                print("-c   Case sensitive")
                print("-a   Make conjunctive request with naive algorithm")
                print("-o   Make disjunctive request with naive algorithm")
                print("-e  Make conjunctive request with fagin algorithm")
                print("-d  Make disjunctive request with fagin algorithm)")
        except DocoptExit as e:
            print(e)            
            
            
           
                
              