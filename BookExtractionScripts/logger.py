# -*- coding: utf-8 -*-

import codecs

class Logger:
   
   def __init__(self, logfilePath, toAppend = True):
      self.logfilePath = logfilePath
      self.toAppend = toAppend
      
      if toAppend == True:
          self.fp = codecs.open(self.logfilePath, 'a')
          #self.fp = open(self.logfilePath, 'a')
      else:
          self.fp = open(self.logfilePath, 'w')
      
      print "Logger file opened successfully : ", self.logfilePath
   
   def writeLine(self, line):
       self.fp.write (line + '\n')
     

   def closeLogger(self):
       self.fp.close()
       print "Logger file closed successfully : ", self.logfilePath