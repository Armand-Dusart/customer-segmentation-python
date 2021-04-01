# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 13:29:19 2021

@author: arman
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from pandas import read_csv, unique, read_sql, DataFrame
from os import getcwd
from .sql import *
from .analyse import *
from time import sleep
from os import getcwd
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template("index.html")

@main.route('/menu')
def menu():
    sql = SQL()
    email = request.cookies.get('email')
    if email == None: 
        flash("Session expired")
        return render_template("menu.html",user=[])
    with sql.connect() as engine :
        req = "select * from auth where email='"+email+"'"
        user = read_sql(req,engine)
    return render_template("menu.html",user=user)

@main.route('/achat')
def achat():
    path = getcwd()
    #Exemple de produits
    produits = read_csv(path+'\data\some_products.csv',sep=";", encoding="utf-8")
    produits['Catégorie']= ['Objets_artistiques',
                                "Objets_artistiques",
                                "Objets_de_creation",
                                "Contenants",
                                "Cadeaux_pour_evenements",
                                "Objets_artistiques",
                                "Contenants",
                                "Contenants",
                                "Contenants",
                                "Objets_de_creation"]
    cat = unique(produits['Catégorie'])
    return render_template("achat.html",product=produits,cat=cat)


@main.route('/payer', methods=["POST"])
def payer():
    #check si la session existe encore
    email = request.cookies.get('email')
    if email == None: 
        flash(email)
        return render_template("payer.html")
    #récuperation de l'utilisateur
    sql = SQL()
    with sql.connect() as engine :
        req = "select * from auth where email='"+email+"'"
        user = read_sql(req,engine)
    #récupération du panier
    req = request.form
    k = [i for i in req.keys()]
    produits = [req.get(i) for i in k]
    #création de la facture
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    #récupération du dernier invoiceNo
    with sql.connect() as engine :
        req = "select max(invoiceNo) from invoices where invoiceNo NOT LIKE '%C%'"
        df = read_sql(req,engine)
    last_value = int(df.values[0][0]) + 1
    #pour chaque produit
    for i in range(int(len(produits)/4)):
        bill = {}
        #récupération détail produit
        produit = produits[i*4:(i+1)*4]
        with sql.connect() as engine :
            req = "select * from invoices where StockCode='"+produit[3]+"'"
            val = read_sql(req,engine)
        if len(val) == 0 :
            pass
        elif len(val) > 1 :
            val = val.loc[0]
        #construction de la facture
        bill['CustomerID'] = int(user['id'][0])
        bill['InvoiceNo'] = last_value 
        bill['StockCode'] = produit[3]
        bill['Description'] = val['Description']
        bill['Quantity'] = produit[1]
        bill['InvoiceDate'] = current_time
        bill['UnitPrice'] = val['UnitPrice']
        bill['Country'] = user['country'][0]
        bill['CA'] = produit[2]
        bill['Catégorie'] = val['Catégorie']
        #ajout de la facture dans la db
        with sql.connect() as engine:
            cur = engine.cursor()
            cur.execute('INSERT INTO invoices (CustomerID, InvoiceNo, StockCode, Description, Quantity, InvoiceDate,  UnitPrice, Country, CA, Catégorie) VALUES (:CustomerID, :InvoiceNo, :StockCode, :Description, :Quantity, :InvoiceDate,  :UnitPrice, :Country, :CA, :Catégorie);', bill)
    
    return render_template("payer.html")

@main.route('/profil')
def profil():
    sql = SQL()
    email = request.cookies.get('email')
    if email == None: 
        flash("Session expired")
        return redirect(url_for('main.menu'))
    with sql.connect() as engine :
        req = "select * from auth where email='"+email+"'"
        user = read_sql(req,engine)
    if user['role'][0] == "customer":
        id = user['id'][0]
        with sql.connect() as engine :
            req = "select * from invoices where CustomerID="+str(id)
            df = pd.read_sql(req,engine)
        return render_template("profil.html",user=user,df=df,len=len(df))
    else:
        return render_template("profil.html",user=user,df=DataFrame(),len=0)



