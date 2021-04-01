# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 20:16:46 2021

@author: arman
"""
from scripts import *
from flask import Blueprint, render_template, redirect, url_for, request, flash
#%timeit
import warnings
warnings.filterwarnings("ignore")

app = create_app()
if __name__ == "__main__":
    app.run(debug=False,port=3000) 

# if __name__ == "__main__":
#     from sklearn.linear_model import LogisticRegression
#     from collections import Counter
#     from datetime import datetime
    
#     a = Analyse()
#     print("pass")
#     z = a.scatter_ca_produit()
    

    


    
    



    
    
    
        