# -*- coding: utf-8 -*-

import re



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
     