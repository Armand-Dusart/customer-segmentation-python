# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 21:09:54 2021

@author: arman
"""

from os import getcwd
import sqlite3 as sq
import pandas as pd
from contextlib import contextmanager 

class SQL(object):
    def __init__(self):
        self.path = getcwd() + "/data/magasin.db"
        
    @contextmanager
    def connect(self):
        try :
            engine = sq.connect(self.path)
            yield engine
        except PermissionError:
            print("can't access to DB")
        except :
            print("Error Connexion to "+self.path)
            print("Or bad syntax in with statement")
        finally: 
            engine.commit()
            engine.close()   

        


 
        
  
      
        
    
 
    
    
    
    