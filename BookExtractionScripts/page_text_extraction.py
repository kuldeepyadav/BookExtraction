# -*- coding: utf-8 -*-



from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams,LTTextBox, LTTextLine, LTFigure, LTImage, LTChar
from pdfminer.converter import PDFPageAggregator
import layout_scanner
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
import os
from utilities import *
import collections

# Open a PDF file.

def getAllPageText(filePath):

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

    outlines = document.get_outlines()    
        
    rsrcmgr = PDFResourceManager()

    # Set parameters for analysis.
    laparams = LAParams()
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    textContent = []

    for i, page in enumerate(PDFPage.create_pages(document)):
        interpreter.process_page(page)
        # receive the LTPage object for the page.
        layout = device.get_result()
        page_wise_content = parse_lt_objs(layout, i+1, '/home/kuldeep/bookextraction/images/')
        textContent.append(page_wise_content)     
    
    
    """
    for lt_obj in layout:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            # text, so arrange is logically based on its column width
            print "Text is : ", i, lt_obj.get_text()
            #page_text = update_page_text_hash(page_text, lt_obj)
            #print page_text
    """
    
    #print layout.get_text() 
    
    return textContent, outlines
    
def getPageWiseText(bookPath):
    
    pages=layout_scanner.get_pages(bookPath)
    return pages
    
def convertPDFToHTMLPage(bookPath):
    
    rsrcmgr = PDFResourceManager()
    codec = 'utf-8'
    scale = 1
    rotation = 0
    
    outfile = bookPath.replace ('.pdf', '.html')
    outfp = file(outfile, 'w')
    
    laparams = LAParams()
    
    layoutmode = 'normal'
    
    device = HTMLConverter(rsrcmgr, outfp, codec=codec, scale=scale,
                               layoutmode=layoutmode, laparams=laparams)

    
    fp = file(bookPath, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(fp, password="",check_extractable=True):
        page.rotate = (page.rotate+rotation) % 360
        interpreter.process_page(page)
    
    fp.close()
    device.close()
    outfp.close()
    
    print "HTML output written to : ", outfile
    
    
def convertPDFToTextPages(bookPath):
    #allText,outlines = getAllPageText(bookPath)
 
    #to check if no extraction of pages is required 
    samplefile = bookPath['pagesDir'] + 'page_0.txt'
    if os.path.exists(samplefile):
        return True
    
    pages = getPageWiseText (bookPath['pdf'])

    if len(pages) ==0:
        return False        
    
    for i,eachpage in enumerate(pages):
        pageName = 'page_' + str(i) + ".txt"
        pagePath = bookPath['pagesDir'] + pageName
        
        f= open(pagePath,'w')
        f.write (eachpage)
        f.close()        
    
    return True
    
    
def getMetadataInformation(bookPath):
    
    fp = open(bookPath['pdf'], 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    
    try:
        if doc.info == []:
            return [], ''
            
        title = doc.info[0]['Title']
        if title.contains ('PDFObjRef'):
            title = ''
    except Exception, e:
        title = ''     

    return doc.info[0], title  # The "Info" metadata
    

def getMetadataInfoUsingPDF(bookPathPDF):
    
    fp = open(bookPathPDF, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    return doc.info  # The "Info" metadata
 
def isPageStringWithNumber(pagestring):
     regx = re.compile(r'Page|page\s\d+$')
     
     return bool(regx.match(pagestring)) 
     
def parsePageStringWithNumber(pagestring):
    pagestring = pagestring.lower().replace('page', '').strip()
    
    if isNumber(pagestring):
        return int(pagestring)
    else:
        return None


def extractpagenumber(pagePath, candidatepagenum):
    
    f= open(pagePath)
    
    allNumbers = []
    for eachline in f:             #scan to get invdividual phone numbers
        eachline = eachline.strip()
        if isNumber (eachline):
            allNumbers.append(int(eachline))
        elif isPageStringWithNumber(eachline):
            pagenum = parsePageStringWithNumber(eachline)
            allNumbers.append(pagenum)
        else:
             continue
        
            
    filteredNumbers = []
    print "all numbers are : ", len(allNumbers),allNumbers

    for eachnum in allNumbers:
        if eachnum == 0 or eachnum > candidatepagenum:
            continue
        else:
            filteredNumbers.append(eachnum)
    
    if len(filteredNumbers) > 0:
        return filteredNumbers[0]
    else:
        return None        
   
        
def extractPageNumberFromFile(fileName):
    
    #page_8.txt
    
    pagenum= int(fileName.split('.')[0].split('_')[1])
    return pagenum
    
    

def get_page_offset(bookPath, logger):
    
    pagesDir = bookPath['pagesDir']
    #pagesDir = bookPath

    if not os.path.exists(pagesDir):
        print "pages dir not created, create a directory at: ", pagesDir

    path, dirs, files = os.walk(pagesDir).next()
    
    allPageOffset = []
    
    totalpages = len(files)
    print "number of files to be scanned : ", totalpages
    logger.writeLine("number of files to be scanned : " +  str(len(files)))
    
    if totalpages == 0:
        return None
        
        
    filelist, pagefiledict = sortFilesByName(files)
    
    for eachFile in filelist:
        if not '.txt' in eachFile:
            continue
            
        pagepath = path + eachFile
        candidatepagenum = extractPageNumberFromFile(eachFile)
        actualpagenum = extractpagenumber(pagepath, candidatepagenum)
        
        if actualpagenum is not None:
            page_offset = candidatepagenum - actualpagenum
            print eachFile, candidatepagenum, actualpagenum
            logger.writeLine(eachFile + " " + str(candidatepagenum) + " " + str(actualpagenum))
            allPageOffset.append(page_offset)  
    
    print "length of allPageOffset is : ",len(allPageOffset)
    logger.writeLine("length of allPageOffset is : " + str(len(allPageOffset)))
    
    if len(allPageOffset) == 0:
        return 0
    
    offsetDict = collections.Counter(allPageOffset)
    print str(offsetDict)
    logger.writeLine("Offset dict is : " + str(offsetDict))
    pageoffset = offsetDict.most_common()[0][0]
    pageoffset_support = offsetDict.most_common()[0][1]

    support = float(pageoffset_support)/totalpages

    if support < 0.2:
        pageoffset = 0
        logger.writeLine ("support is less than 0.2, page offset is : " + str(support) + " " + str(pageoffset))
        
    offsetlimit = totalpages * 0.1
    if pageoffset > offsetlimit:
        pageoffset = 0   
        logger.writeLine ("offset is more than limit : " + str(pageoffset))


    bookInfo, bookTitle = getMetadataInformation(bookPath)
    print "bookinfo result : ", bookInfo, bookTitle
    logger.writeLine ("book info result : " + str(bookInfo))

    with open(bookPath['metadataDir'] + 'info.txt','w') as f:
        f.write (str(bookInfo) + "\n")
        f.write (str(pageoffset) + "\n")
        f.write (str(totalpages))       
        
    return pageoffset, totalpages
    

def sortFilesByName(files):   #returns  a dict
    
    pagefiledict = {}
    for eachfile in files:
        pagenum = extractPageNumberFromFile(eachfile)
        pagefiledict[eachfile] = int(pagenum)
    
    return sorted(pagefiledict, key=pagefiledict.__getitem__), pagefiledict
    
    
def extractCleanBookText(bookPath, pageoffset, totalpages, logger):

    pagesDir = bookPath['pagesDir']
    #pagesDir = bookPath

    if not os.path.exists(pagesDir):
        print "pages dir not created, create a directory at: ", pagesDir

    path, dirs, files = os.walk(pagesDir).next()
    
    totalpages = len(files)
    print "number of files to be read : ", totalpages
    logger.writeLine("number of files to be read : " +  str(len(files)))
    
    startingpage = pageoffset + 1
    endingpage = totalpages - 10      #ignore last few pages
    
    logger.writeLine("Starting and ending page number " +  str(startingpage)  + " " +  str(endingpage))
    
    filelist, pagefiledict = sortFilesByName(files)
    
    logger.writeLine("file list is : " + str(filelist))
    
    completeBookTextPath = bookPath['metadataDir'] + 'completeBookText.txt'
    bookTextFile = open(completeBookTextPath,'w')
    
    logger.writeLine("complete booktext path : " + completeBookTextPath)
    
    #logger.writeLine("sorted files are : " + str(len(files)))    
    
    for eachFile in filelist:
        if not '.txt' in eachFile:
            logger.writeLine("file is not text : " + eachFile)
            continue
        
        pagenum= pagefiledict[eachFile]
        #pagenum = extractPageNumberFromFile(eachFile)
        
        if pagenum not in range(startingpage, endingpage):
            logger.writeLine ("page not in range : " + str(pagenum))
            continue
        
        pagepath = path + eachFile
        logger.writeLine("reading and write contents for the file: " + pagepath)
        f = open(pagepath)
        for line in f:
            if len(line) < 50:
                continue
            
            bookTextFile.write (line)
            
    bookTextFile.close()
    
