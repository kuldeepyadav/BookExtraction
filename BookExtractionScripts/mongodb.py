# -*- coding: utf-8 -*-


from pymongo import MongoClient
from collections import OrderedDict

class MongoDB:
    
   db = None
   
   def __init__(self, database = 'books'):       
       
       try:
           client = MongoClient()  #from collections import OrderedDict
           self.db = client[database]           
       except Exception, e:
           print "Exception is : ", str(e)
           return
       
       #allcollections = db.collection_names(include_system_collections=False)
       print "Mongo client initialized with collections"
       
   def insertABook(self, collectionName, bookDict):
       try:
           insertresult = self.db[collectionName].insert(bookDict, check_keys=False)
           
           print "Result is : ", insertresult
           if insertresult is not None:
               print "Book inserted in the database"
               return True, insertresult
           else:
               return  False, -1
       except Exception, e:
           print str(e)
           return False, str(e)
           
           
           
   def checkIfBookExist(self, collectionName, bookName):
        print "Checking not implemented yet"
        
   def getBookByName(self, bookName):
        print "Retrieving not implemented yet"
        
        

        
    
           
       
       
       