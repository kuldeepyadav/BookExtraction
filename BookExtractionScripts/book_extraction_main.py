# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-


from os import walk
import os
import sys
import pickle
from page_text_extraction import convertPDFToTextPages, getMetadataInformation
from index_words_extraction import getBookIndex
import layout_scanner
from extract_toc import extractTOC
from logger import Logger
from mongodb import MongoDB


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
    
    


if __name__ == "__main__":
    
    #allowedFileNames = ['Mar201.pdf', 'Inbound_Marketing_For_Dummies.pdf', 'SecOfTheMarMasWhaTheBesMarDoAndWhyItWor.pdf', 'Writing.pdf']
    #blockedFileNames = []
    
    defaultPath = '/home/kuldeep/bookextraction/Books/computernetworks/'
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
        #    continue
        
        print "Processing : ", eachbookPath['name']
        
        try:
            createDirectories(eachbookPath)
            bookInfo, bookTitle = getMetadataInformation(eachbookPath)
            print "bookinfo result : ", bookInfo, bookTitle
        
            if bookInfo == {}:
                print "Skipping this book : ", eachbookPath['name']
                continue
        
            toc = []
            indexdict = []

            pageResult = convertPDFToTextPages(eachbookPath)
            tocResult, toc  = extractTOC(eachbookPath)
            print "toc result : ", tocResult
            indexResult, indexdict = getBookIndex(eachbookPath, log)
            print "index result : ", indexResult, len(indexdict)
            
            log.writeLine ("Processed : " + eachbookPath['pdf'] + " " + str(pageResult) + " " + str(tocResult) + " " + str(indexResult))
        
        
        except:
            log.writeLine ('Error in processing book: ' + eachbookPath['pdf'])
            e = sys.exc_info()[0]
            print "Error is : ", e
            log.writeLine ('Error in processing book: ' + str(e))
        
    
    log.closeLogger()
    
    
#allPDFfiles = readDatasetDirectory()

