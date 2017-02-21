# -*- coding: utf-8 -*-

import codecs

class Topic:
    
    keywordlist = None
    
    def __init__(self, topicname, level, startpage, endpage):
        self.topicname = topicname
        self.startpage = startpage
        self.endpage = endpage
        self.level = level
        
    def updateEndPage(self, endpage):
        if self.startpage == endpage:
            self.endpage = endpage
        else:
            self.endpage = endpage - 1
        
    def updateKeywordList(self, keywordlist):
        self.keywordlist = keywordlist
        
    

        
def changeIndexDictWithPageoffset(indexdict, pageoffset, logger):
    
    newIndexDict = {}
    for eachitem in indexdict.items():
        logger.writeLine ("adjusting offset for : " + str(eachitem))
        indexname = eachitem[0]
        """
        pagenumStr = eachitem[1].split(',')
        
        pagenums = []
        for numStr in pagenumStr:
            if len(numStr) > 0:
                pagenums.append(int(numStr))
        """
        updatedpagenums = []
        for eachpagenum in eachitem[1]:
            updatednum = int(eachpagenum) + pageoffset
            updatedpagenums.append(updatednum)
            
        newIndexDict[indexname] = updatedpagenums

    return newIndexDict


def associateTopicsWithKeywords(bookPath, tocdict, indexdict, pageoffset, totalpages, logger):
    
    logger.writeLine ("length of dicts " +  str(len(tocdict)) + " " + str(len(indexdict)))
    logger.writeLine ("page offset is : " + str(pageoffset) + " " + str(totalpages))    
    
    allTopicObjects = getTopicClassObjs (tocdict, totalpages, logger)
    newIndexDict = changeIndexDictWithPageoffset(indexdict, pageoffset, logger)
    
    for eachobj in allTopicObjects:
         keywordlist = getTopicKeywords(eachobj.startpage,eachobj.endpage, newIndexDict)
         eachobj.updateKeywordList(keywordlist)
         logger.writeLine (str(eachobj.startpage) + " " + str(eachobj.endpage) + " " + str(keywordlist))
    
    topicsWithKeywordsFilePath = bookPath['metadataDir'] + 'topicswithkeywords.txt'
    with open(topicsWithKeywordsFilePath, 'w') as f:
         for eachobj in allTopicObjects:
             f.write(eachobj.topicname.encode('utf8') + " " + str(eachobj.startpage) + " " + str(eachobj.endpage) + "\n")
             f.write(str(eachobj.keywordlist) + "\n")
             f.write("\n")
    

def getTopicClassObjs(tocdict, totalpages, logger=None):
    
    prevLevel = -1
    
    allTopicObjects = []
    stackedTopicObjects = []
    
    for eachtoc in tocdict.items():
        
        topicname = eachtoc[0]
        topiclevel = eachtoc[1][0]
        startpage = eachtoc[1][1]
        endpage = None
        
        logger.writeLine ("handling : " + str(eachtoc) + "\n")
        
        if prevLevel == topiclevel:
            #length = len(stackedTopicObjects)
            lastobject = stackedTopicObjects.pop()
            lastobject.updateEndPage(startpage)
            allTopicObjects.append(lastobject)
            logger.writeLine ("level is same : " + str(len(allTopicObjects)) + " " + str(len(stackedTopicObjects)))
            #logger.write ("\n")     
        elif prevLevel > topiclevel:
            logger.writeLine ("level is higher : " + str(len(allTopicObjects)) + " " + str(len(stackedTopicObjects)))
              
            while (len(stackedTopicObjects) >= 1):
                lastobject = stackedTopicObjects.pop()
                if lastobject.level >= topiclevel:
                    lastobject.updateEndPage(startpage)
                    allTopicObjects.append(lastobject)
                else:
                    stackedTopicObjects.append(lastobject)
                    break
                
            logger.writeLine ("after popping : " + str(len(allTopicObjects)) + " " + str(len(stackedTopicObjects)))
            
                
        newTopic = Topic(topicname, topiclevel, startpage, endpage)
        stackedTopicObjects.append(newTopic)      
        logger.writeLine ("after insertion : " + str(len(allTopicObjects)) + " " + str(len(stackedTopicObjects)))
        prevLevel = topiclevel                    
        #f.write (str(topiclevel) + "    " + str(startpage) + "\n")
        #print topiclevel, startpage
    while (len(stackedTopicObjects) >= 1):
        lastobject = stackedTopicObjects.pop()
        lastobject.updateEndPage(totalpages)
        allTopicObjects.append(lastobject)
        
    print "length of all topic objs is : ", len(allTopicObjects)
    
    topicdict = {}  #with start and endpage
    
    for obj in allTopicObjects:
        topicdict[obj.topicname] = (obj.startpage, obj.endpage)
    
    print "length of topicdict is : ", len(topicdict), str(topicdict)
        
    sortedTopicObjects = []

    for eachtoc in tocdict.items():        
        topicname = eachtoc[0]
        topiclevel = eachtoc[1][0]
        startpage, endpage = topicdict[topicname]
        newTopic = Topic(topicname, topiclevel, startpage, endpage)
        sortedTopicObjects.append(newTopic)
        
    print "length of all sorted topic objs is : ", len(sortedTopicObjects)
    writeTopicObjs(sortedTopicObjects)
    return sortedTopicObjects
    

def  writeTopicObjs(allTopicObjects):
    
    with open('/home/kuldeep/temp.txt', 'w') as f:
        for obj in allTopicObjects:
            f.write(obj.topicname.encode('utf8') + " " + str(obj.level) + " " + str(obj.startpage) + " " + str(obj.endpage) + "\n")
            
            #topicname, level, startpage, endpage
        

def getTopicKeywords(startpage,endpage, indexdict):
    
    
    allKeywords = []
    for eachindex in indexdict.items():
        indexname = eachindex[0]
        
        isExist = False
        for pagenum in eachindex[1]:
            if pagenum in range(startpage, endpage):
                isExist = True
                break
            elif pagenum == startpage or pagenum == endpage:
                isExist = True
                break
                
        if isExist:
            allKeywords.append(indexname)
    
    return allKeywords