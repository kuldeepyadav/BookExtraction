# -*- coding: utf-8 -*-



def associateTopicsWithKeywords(tocdict, indexdict, pageoffset, logger):
    
    for eachtopic in tocdict.items():
        logger.writeLine("Each topic is " +  str(eachtopic))
        
    logger.writeLine ("length of dicts " +  str(len(tocdict)) + " " + str(len(indexdict)))
    logger.writeLine ("page offset is : " + str(pageoffset))    



def getTopicKeywords():
    
    return None