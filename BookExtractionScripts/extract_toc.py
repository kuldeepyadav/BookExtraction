

# -*- coding: utf-8 -*-


import sys
import traceback
import codecs
import json
import os

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams,LTTextBox, LTTextLine, LTFigure, LTImage, LTChar
from pdfminer.converter import PDFPageAggregator
from pdfminer.psparser import PSKeyword, PSLiteral, LIT
import layout_scanner
from pdfminer.pdftypes import PDFStream, PDFObjRef, resolve1, stream_value
from collections import OrderedDict


# Open a PDF file.

def getTOC(filePath):

    fp = open(filePath)
    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Supply the password for initialization.
    document = PDFDocument(parser, password="")
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
        # Create a PDF resource manager object that stores shared resources.
    
    pages = dict( (page.pageid, pageno) for (pageno,page)
                  in enumerate(PDFPage.create_pages(document)) )
    
    def resolve_dest(dest):
        if isinstance(dest, str):
            dest = resolve1(document.get_dest(dest))
            #print "updated dest [str] : ",dest
        elif isinstance(dest, PSLiteral):
            dest = resolve1(document.get_dest(dest.name))
            #print "updated dest [PSLiteral]: ", dest
        elif isinstance(dest, PDFObjRef):
            dest = resolve1(dest)
            #print "updated dest [PDFObjRef]: ", dest
        if isinstance(dest, dict):
            dest = dest['D']
            #print "updated dest [dict]: ", dest
        
        return dest        
        
        
    try:
        outlines = document.get_outlines()    
    except PDFNoOutlines:
        print "could not extract TOC ", filePath
        print "Error is :", sys.exc_info()[0]
        outlines = None

    toc =[]
    if outlines is not None:
        for (level,title,dest,a,se) in outlines:
            pageno = None
            #print level, title
            
            if dest:
                try:
                    dest = resolve_dest(dest)
                    pageno = pages[dest[0].objid]
                except:
                    desired_trace = traceback.format_exc(sys.exc_info())
                    print "Exception caught", desired_trace
                    break                    
            elif a:
                #print str(a) 
                #action = a.resolve()
                try:
                    #action = a
                    if not isinstance(a, dict):
                        action = a.resolve()
                    else:
                        action = a
                    if isinstance(action, dict):
                        subtype = action.get('S')
                        if subtype and repr(subtype) == '/GoTo' and action.get('D'):
                            dest = resolve_dest(action['D'])
                            pageno = pages[dest[0].objid]
                except:
                    desired_trace = traceback.format_exc(sys.exc_info())
                    print "Exception caught", desired_trace
                    break
            
            toc.append((level, title, pageno))
            
    return toc
    
def getTOCFromLayoutScanner(filePath):
    
    toc = layout_scanner.get_toc(filePath)
    return toc
   
def extractTOC(bookPath, logger):
    
    tocfile = bookPath['metadataDir'] + 'toc.txt'
    tocJSONFile = bookPath['metadataDir'] + 'toc.txt'
    
    if os.path.exists(tocfile) or os.path.exists(tocJSONFile):        
        tocResult, tocdict = readTOCFromFile(bookPath, logger)
        logger.writeLine ("TOC already exits : " + str(tocResult) + " " + str(tocdict))
        return tocResult, tocdict
    
    toc = getTOC (bookPath['pdf'])     
    
    if toc == []:
        return False, []
    
    allconcepts =[]
    tocdict = OrderedDict()
    
    for eachline in toc:
        item = ""
        for eachitem in eachline:
            if isinstance(eachitem, unicode):
                item = item +  eachitem.encode('utf-8', 'strict') + " "
            else:
                item = item + str(eachitem) + " "
                
        allconcepts.append(item)
        
    if len(allconcepts) == 0:
        return False
        
    for eachline in toc:
        toctitle = eachline[1].encode('utf-8', 'strict').replace('\x00', '')
        toclevel = eachline[0]
        tocpageno = eachline[2]

        tocdict[toctitle] = (toclevel, tocpageno)
        
    print "Length of all concepts is : ", len(allconcepts)

    with open(bookPath['metadataDir'] + 'toc.txt', 'w') as fp:
        for item in tocdict.items():
            fp.write (str(item) + "\n")  
            logger.writeLine(str(item))
            
    tocJSONPath = bookPath['metadataDir'] + 'toc.json'
            
    json.dump(tocdict, open(tocJSONPath,'w'))
    
    logger.writeLine("TOC dumped to : " + tocJSONPath + " " +  str(len(tocdict.items())))
            
    return True, tocdict


def readTOCFromFile(bookPath, logger):
    
    tocJSONFilePath = bookPath['metadataDir'] + 'toc.json'
    
    try:
        tocdict = json.load(open(tocJSONFilePath), object_pairs_hook=OrderedDict)
    except:
         desired_trace = traceback.format_exc(sys.exc_info())
         print "Exception caught", desired_trace
         logger.writeLine("exception caught while reading toc.json " + desired_trace)
         return False, {}
         
    return True, tocdict
      
    
        
    
