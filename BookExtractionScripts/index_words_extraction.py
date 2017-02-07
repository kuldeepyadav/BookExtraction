# -*- coding: utf-8 -*-


import re
import os
import codecs

#“ex” for exercises, “ﬁg” for
#ﬁgures, “n” for footnotes, “sum” for summaries.

blackListedStrings = ['ex.', 'pr.', 'fig.', 'n.', 'ex', 'fig', 'n', 'sum']

def isIndexLine(linecontent):
    
    regx = re.compile(r'[\w{1,}\s\-\d\W\,\/\+\(\)\.\:]*\s[\d+\–\-\s\,\.]*$')
    
    return bool(regx.match(linecontent))
    

def isIndexLineWithCleaning(linecontent):
    
    cleanedline = cleanIncomingString (linecontent)
    
    regx = re.compile(r'[\w{1,}\s\-\d\W\,\/\+\(\)\.\:]*\s[\d+\–\-\s\,\.]*$')
    
    if not isinstance(cleanedline, str):
        print "error : not a string instance "        
    
    return bool(regx.match(cleanedline))
    
    
def cleanIncomingString (string):
    
    regex = re.compile(r'([0-9.,]+(\s{0,})(pr|ex|sum|fig|ff|n|f|t))(\.{0,})')
    
    print "String to clean : ", string
    
    if string.strip().lower() == 'index' or string.strip().lower() == 'subject index':
        return ''           #return blank string     
    
    if len(string) > 50:
        return ''        
        
    seeIndex = string.lower().find('see')
    
    if seeIndex > 0:
        newstring = string[:seeIndex]   #ignore everything after see
    else:    
        newstring = string

    if newstring.strip() == 0:
        return ''
    
    string = newstring.strip()
    
    print "string is  : ", string
    
    while regex.search(string) is not None:
        matchedString = regex.search(string).group()
        print "matched string is ",matchedString
        pagenumber = [int(s) for s in re.findall(r'\d+', matchedString)]
        print "page number is ", str(pagenumber)
        if len(pagenumber) > 0:
            newstring = string.replace(matchedString, str(pagenumber[0]))
        else:
            newstring = string.replace(matchedString, '')
        string = newstring
        
    
    # allmatches = re.findall(regex, string)
    
    print "cleaned string  ", string
    return string

def isIndexPage(pagePath):
    
    f= open(pagePath)
    
    totalcount = 0
    indexcount = 0
    for eachline in f:
        if isIndexLine(eachline.strip()) and len(eachline.strip())>0 and len(eachline.strip())<50:
            indexcount = indexcount + 1
            #print "each line is : ", eachline
        
        totalcount = totalcount + 1
        
    if totalcount == 0:
        return False
        
    ratio = float(indexcount)/totalcount

    if ratio > 0.4: 
        return True
    else:
        return False

        
def parseIndexPage(pagepath, logger, indexdict =  {}):
    
    print "page path is : ", pagepath
    filestream = codecs.open(pagepath, 'r')
    #pagetext = open(pagepath, 'r', encoding='utf-8')
    
    #f= open('/home/kuldeep/bookextraction/Books/book_parser_log.txt','a')
    
    previousKeyPhrase = None
    page_range = None 
    
    for line in filestream:
        #print "current line is : ", line       
        
        try:
            cleanedline = cleanIncomingString (line.strip())
            strippedline = cleanedline.strip()
            strippedline= unicode(strippedline, "utf8")
            #strippedline=strippedline.decode('utf-8','ignore').encode("utf-8")
        except:
            print "Error in cleaning string : ", line, pagepath
            logger.writeLine ("Error in cleaning string : " + line + "," + pagepath)
            continue
        
        
        logger.writeLine ("Cleaned string " + strippedline)
        
        if len(strippedline.strip()) <= 1:  #ignore blank line and single characters
            continue      
       
        if isIndexLine(strippedline):
            logger.writeLine("Index line detected : " + strippedline)
            keyphrase, pagenumbers = parseIndexLine(strippedline)
            
            logger.writeLine("parsed keyphrase and pagenumbers : " + str(keyphrase) +  " " +  str(pagenumbers))
            
            if previousKeyPhrase is not None:
                keyphrase = previousKeyPhrase + ' ' + keyphrase
                previousKeyPhrase = None
            
            logger.writeLine ("Index word detected : " + keyphrase + " " + str(pagenumbers))
            #keyphrase = keyphrase.encode('utf-8', 'strict')
            
            indexdict[keyphrase] = pagenumbers

        elif isAlphaNumericString(strippedline):
            if previousKeyPhrase is not None:
                previousKeyPhrase = previousKeyPhrase + ' ' + strippedline
            else:
                previousKeyPhrase = strippedline
                
            logger.writeLine ("Alpha numeric string : " + strippedline + " " + previousKeyPhrase)
                
        elif isPageNumbers(strippedline):
            page_range = splitPageNumbers (strippedline)
            logger.writeLine("parsed page numbers are:  " + str(page_range))
            
            if previousKeyPhrase != None:
                #previousKeyPhrase = previousKeyPhrase.encode('utf-8', 'strict')
                indexdict[previousKeyPhrase] = page_range
                logger.writeLine ("Index word detected : " + previousKeyPhrase + " " + str(page_range))
                previousKeyPhrase = None                 
        else:
            print "Could not parse line : ", strippedline
            logger.writeLine ("Could not parse line : " +  strippedline)

  
    #print "Length of indexdict ", len(indexdict.items())
    return indexdict
    

def isAlphaNumericString(string):
    
     #regx = re.compile(r'[[a-z][A-Z]{1,}\s\-\d\,\/\+\(\)\.]*')
     
     if any(c.isalpha() for c in string):
         return True
     else: 
         regx = re.compile(r'\d+\.\d+')
         return bool(regx.match(string))
     
     
def isPageNumbers(string):
    
     regx = re.compile(r'[\d+\-\–\,\.]')
     
     return bool(regx.match(string))
     
def isNumber (string):
    
     if len(string) == 0:
         return False
     
     return all(c.isdigit() for c in string)
     
def isNumberWithADot(string):
     
     regx = re.compile(r'\d+\.$')
     
     return bool(regx.match(string))
    
     
     
def splitPageNumbers (string):
    
    newstring = string.replace ('-', ' ').replace('–', ' ').replace('--',' ')
    
    stringparts = newstring.split (' ')
    
    allnumbers = []

    for eachpart in stringparts:
        if len(eachpart.strip()) > 0:
            if isNumber(eachpart.strip()):
                allnumbers.append(int(eachpart))
            elif isNumberWithADot(eachpart.strip()):
                onlynumber= eachpart.strip().replace('.', '')
                allnumbers.append(int(onlynumber))
            else:
                print "Non number : ", eachpart
                
    
    if len(allnumbers) != 2:
        print "number of page numbers are greater than 2, can not be parsed", string
        return []
        
        
    diff = allnumbers[1] - allnumbers[0]
    num_digit = len(str(allnumbers[1]))
    start_page = allnumbers[0]
    if diff < 0:
        if num_digit == 1:
            modulo = allnumbers[0] / 10
            to_be_sum = 10 * modulo 
            end_page = to_be_sum + allnumbers[1]
        elif num_digit == 2:
            modulo = allnumbers[0] / 100
            to_be_sum = 100 * modulo 
            end_page = to_be_sum + allnumbers[1]
        elif num_digit == 3:
            modulo = allnumbers[0] / 1000
            to_be_sum = 1000 * modulo 
            end_page = to_be_sum + allnumbers[1]
        else:
            print "number of digits are very large : ", num_digit
            end_page = start_page
    else:
        start_page = allnumbers[0]
        end_page = allnumbers[1]
    
    page_range = range(start_page, end_page)   
    page_range.append(end_page)
     
    return page_range
    
    

def parseIndexLine(indexline):
    
   cleanindexline=  indexline.replace(',',' ').replace(';',' ')  
   
   indexparts = cleanindexline.split (' ')   
   
   #print "index parts are : ", indexparts
   
   keyphrases =  []
   pagenumbers = []
   for part in indexparts:
       
       eachpart = part.strip()
       
       if len(eachpart) ==0:
           continue
       
       if isAlphaNumericString(eachpart):
           print "Found keyphrase : ", eachpart
           keyphrases.append(eachpart)
       elif isPageNumbers(eachpart):
           #print "Found page numbers : ", eachpart           
           if isNumber(eachpart):    # for single page numbers           
               pagenumbers.append(int(eachpart))      
               print "single page number : ",int(eachpart)
           else: # for mulitple page numbers separated by - or --
               page_range = splitPageNumbers(eachpart)
               print "page_range : ", page_range
               pagenumbers.extend(page_range)
               
       else:
           print "No match to the string: ", eachpart
           
   combinedphrase = ' '.join(phrase for phrase in keyphrases)
           
   return combinedphrase, pagenumbers


def getBookIndex(bookPath, logger):

    pagesDir = bookPath['pagesDir']

    if not os.path.exists(pagesDir):
        print "pages dir not created, create a directory at: ", pagesDir

    path, dirs, files = os.walk(pagesDir).next()
    
    indexDict = {}
    
    for eachFile in files:
        if not '.txt' in eachFile:
            continue
            
        pagepath = path + eachFile
        result = isIndexPage(pagepath)
        
        logger.writeLine(pagepath + "," + str(result))
        
        if result == True:
            indexDict = parseIndexPage(pagepath, logger, indexDict)
            logger.writeLine (str(pagepath) + "\t" + str(indexDict.values))
    
    print "total length of index dict is : ", len(indexDict)
    
    indexDict = cleanIndexDict(indexDict)  
    
    if len(indexDict) == 0:
        return False, indexDict
    
    indexFilePath = bookPath['metadataDir'] + 'index.txt'

    with open(indexFilePath, 'w') as f:
        for key, value in indexDict.items():
            f.write (str(key) + "\t" + str(value) + "\n")
        
    
    return True, indexDict
    
def getBookIndexFromFile (bookPath, logger):
    
    indexFilePath = bookPath['metadataDir'] + 'index.txt'
    
    filestream = codecs.open(indexFilePath, 'r', encoding= 'utf8')
    indexdict = {}
    
    for line in filestream:
        line = line.strip()
        
        if len(line) == 0:
            continue
            
        b1 = line.index('[')
        b2 = line.index(']')
        
        print line, b1, b2
        
        keyphrase = line[0:b1].strip()
        
        pagenumberstr = line[b1+1:b2]
        pagenumberlist = pagenumberstr.split(',')
        pagenumbers = []
        for eachpagenum in pagenumberlist:
            if isNumber(eachpagenum) > 0:
                pagenumbers.append(int(eachpagenum))
                
        #keyphrase = keyphrase.decode('unicode_escape').encode('ascii','ignore')
        try:
            keyphrase = keyphrase.encode('utf-8', 'ignore')
            keyphrase = keyphrase.replace('\x00', ' ')
        except UnicodeEncodeError:
            logger.writeLine("Unicode error in: " + keyphrase)
            print "Unicode error in: ", keyphrase
            continue           
        
        print keyphrase, pagenumberstr

        isunicode = False
        if isinstance(keyphrase, unicode):
            isunicode = True
            
            
        if len(keyphrase) > 0:
            indexdict[keyphrase] = pagenumberstr  

        print "is unicode : ", isunicode
        #logger.writeLine(keyphrase.encode("utf-8"))
            
        #logger.writeLine("Index line : " + str(isunicode) + " " + keyphrase.encode("utf-8") + " " + str(pagenumbers))
        
           
        
    return True, indexdict
        
    
    
    
def dumpIndexDict (indexDict, filePath):
    
     with open(filePath, 'w') as f:
        for key, value in indexDict.items():
            f.write (str(key) + "\t" + str(value) + "\n")
            
            
def cleanIndexDict(indexDict):
    
    newIndexDict ={}

    for eachkey, eachvalue in indexDict.items():
        newkey = ''.join(eachkey.split('\x00'))   #getting rid of null characters
        newIndexDict[newkey]= eachvalue 
    
    return newIndexDict
    

        
            
    
