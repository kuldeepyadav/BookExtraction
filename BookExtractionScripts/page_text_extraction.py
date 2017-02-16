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
    
    pages = getPageWiseText (bookPath['pdf'])

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
    

def extractpagenumber(pagePath, candidatepagenum):
    
    f= open(pagePath)
    
    allNumbers = []
    for eachline in f:             #scan to get invdividual phone numbers
        if isNumber (eachline.strip()):
            allNumbers.append(int(eachline.strip()))
            
    filteredNumbers = []

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
    
    

def get_page_offset(bookPath):
    
    #pagesDir = bookPath['pagesDir']
    pagesDir = bookPath

    if not os.path.exists(pagesDir):
        print "pages dir not created, create a directory at: ", pagesDir

    path, dirs, files = os.walk(pagesDir).next()
    
    allPageOffset = []
    
    for eachFile in files:
        if not '.txt' in eachFile:
            continue
            
        pagepath = path + eachFile
        candidatepagenum = extractPageNumberFromFile(eachFile)
        actualpagenum = extractpagenumber(pagepath, candidatepagenum)
        
        if actualpagenum is not None:
            page_offset = candidatepagenum - actualpagenum
            print eachFile, candidatepagenum, actualpagenum
            allPageOffset.append(page_offset)  
        
    offsetDict = collections.Counter(allPageOffset)
    print str(offsetDict)
    pageoffset = offsetDict.most_common()[0][0]
    return pageoffset

    
    
