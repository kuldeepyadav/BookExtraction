
# -*- coding: utf-8 -*-


from os import walk
import os
import sys
import pickle
from page_text_extraction import convertPDFToTextPages, getMetadataInformation
from index_words_extraction import getBookIndex, getBookIndexFromFile
import layout_scanner
from extract_toc import extractTOC
from logger import Logger
from mongodb import MongoDB
import GLOBAL_CONSTANTS


def readDatasetDirectory(rootFolder):
    #bookList = ['AI1', 'IP2', 'OS1', 'OS4', 'CN4', 'IP3', 'OS2']
    #allBookPaths = []
    allDirs = []
    allPDFfiles=[]
    for (dirpath, dirnames, filenames) in walk(rootFolder):
        print dirpath,dirnames,filenames
        for dirname in dirnames:
            subDirPath = os.path.join(dirpath, dirname)
            allDirs.append(subDirPath)
            dirFiles = os.listdir(subDirPath)   
            bookPath = {}
	    
            for eachFile in dirFiles:
                if '.pdf' in eachFile:
                    bookPath['pdf'] = os.path.join(subDirPath, eachFile)
                    bookPath['dir'] = os.path.join(subDirPath,'')
                    bookPath['name'] = eachFile
                    allPDFfiles.append(bookPath)
                    #print "processing : ",bookPath
                    #try:
                        #except:
                    #    e = sys.exc_info()[0]
                    #    print "Error is : ", e
                    #    print "Exception caught in: ", bookPath
        for filename in filenames:
            print "filename is : ", filename
            bookPath= {}
            if '.pdf' in filename:
                bookPath['pdf'] = os.path.join(dirpath, filename)
                bookPath['dir'] = os.path.join(dirpath,'')
                bookPath['name'] = filename
                print "book path is: ", bookPath
                allPDFfiles.append(bookPath)
                
            
                
    #print allDirs, len(allDirs)
    #print allBookPaths, len(allBookPaths)
    return allPDFfiles   
    
def createDirectories(bookPath):
    
    bookDir = bookPath['dir'] + bookPath['name'].replace('.pdf', '') + "/"
    
    if not os.path.exists(bookDir):
        os.makedirs(bookDir)
        
    pagesDir = bookDir + 'pages/'
    
    if not os.path.exists(pagesDir):
        os.makedirs(pagesDir)
        
    metadataDir = bookDir + 'metadata/'
    
    if not os.path.exists(metadataDir):
        os.makedirs(metadataDir)
        
    bookPath['pagesDir'] = pagesDir
    bookPath['metadataDir'] = metadataDir

    print "Directories succssfully created"

    return bookPath
    
 
def insertBookIntoDB(bookPath, bookInfo, bookTitle, toc, indexdict, logger):
    
    bookdict = {}

    #item['author'] = item['author'].encode('utf-8', 'strict')

    bookdict['title'] = bookTitle.encode('utf-8', 'ignore')
    bookdict['path'] = bookPath['pdf']
    bookdict['name']= bookPath['name']
    bookdict['toc'] = toc
    bookdict['indexkeywords'] = indexdict
    #bookdict['bookinfo'] = bookInfo

    dbInstance = MongoDB()
    result, id = dbInstance.insertABook(GLOBAL_CONSTANTS.CollectionName, bookdict)
    
    print "Insert book status : ", result, GLOBAL_CONSTANTS.CollectionName

    logger.writeLine("Book inserted into the database : " + str(result) + " " + bookdict['name'] + " " + GLOBAL_CONSTANTS.CollectionName)
    
    return

        
if __name__ == "__main__":
    
    allowedFileNames = []
    blockedFileNames = []
    
    defaultPath = '/home/kuldeep/bookextraction/Books/test/'
    print "number of arguments are : ", len(sys.argv)  
    
    if len(sys.argv) > 2:
        bookPath = sys.argv[1]
    else:
        print "Error: at least two parameters needed"
        bookPath = defaultPath
        print "setting to deafult path ", bookPath
        #exit
        
    log = Logger(bookPath + 'bookProcessingLog.txt', True)
        
    allPDFFiles = readDatasetDirectory(bookPath)
    print "total pdf files : ", len(allPDFFiles)    
    
    
    for eachbookPath in allPDFFiles:
        
        #if eachbookPath['name'] not in allowedFileNames:
        #    print "file is blocked : ", eachbookPath['name']
        #   continue
        
        #if eachbookPath['name'] in blockedFileNames:
        #    log.writeLine("File is blocked : " + eachbookPath['name'])
        #    print "file is blocked : ", eachbookPath['name']
        #    continue
        
        print "Processing : ", eachbookPath['name']     
        toc = []
        indexdict = []
        createDirectories(eachbookPath)  
        bookInfo, bookTitle = getMetadataInformation(eachbookPath)
        print "bookinfo result : ", bookInfo, bookTitle
        log.writeLine ("book info result : " + str(bookInfo))    
        
        #tocResult, toc  = extractTOC(eachbookPath)
        
        
        #try:
            
        pageResult = convertPDFToTextPages(eachbookPath)
        print "Page result extraction : ", pageResult
            
        tocResult, toc  = extractTOC(eachbookPath)
        print "toc result : ", tocResult
        log.writeLine ('toc processing result for ' + eachbookPath['pdf'] + ' ' + str(tocResult))
            
        indexResult, indexdict = getBookIndex(eachbookPath, log)
        print "index result : ", indexResult, len(indexdict)
            
        #indexResult, indexdict = getBookIndexFromFile(eachbookPath, log)    
        #insertBookIntoDB(eachbookPath, bookInfo, bookTitle, toc, indexdict, log)

        log.writeLine ("Processed : " + eachbookPath['pdf'] + " " + str(pageResult) + " " + str(tocResult) + " " + str(indexResult))
            
        """
        except:
            log.writeLine ('Error in processing book: ' + eachbookPath['pdf'])
            e = sys.exc_info()[0]
            print "Error is : ", e
            log.writeLine ('Error in processing book: ' + str(e))
        """
        
    log.closeLogger()
    
    
#allPDFfiles = readDatasetDirectory()

