import time, tokenization

# this script just tokenizes a file (relative path from the directory you're in in the command line)
# if you are at ./YAC and the file is in the folder above, pathToFile = ../la010189 for example
start = time.clock()
#t = tokenization.TextFile("pathToFile") # '../../../../Downloads/latimes/la010189'
#hashmap = t.tokenizeTextFileByDocSplit() #True : without tags (<DOC> for example), False or nothing : tags are included. 
#print(hashmap)
testFileList = tokenization.TextFileList.fileListFromPath("folderPath") # '../../../../Downloads/latimes'
print(len(testFileList.tokenizeTextFilesByDocSplit()))
end = time.clock()
print(end - start)