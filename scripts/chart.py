# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 01:01:29 2021

@author: arman
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from pandas import read_csv, unique, read_sql
from os import getcwd
from .sql import *
from .analyse import *
from time import sleep
from datetime import datetime

chart = Blueprint('chart', __name__)

@chart.route('/analyse')
def analyse():
    global ays
    ays = Analyse()
    email = request.cookies.get('email')
    if email == None: 
        flash("Session expired")
        return render_template("analyse.html")
    return render_template("analyse.html")

@chart.route('/analyse/ensemble')
def ensemble():
    global ays 
    email = request.cookies.get('email')
    if email == None: 
        flash("Session expired")
        return redirect(url_for('main.menu'))
    graph = ays.indicateur_ca()
    countries = ays.scatter_ca()
    map = ays.map_ca()
    cr_sp = ays.croissance_speed()
    fid_ind = ays.indicateur_fid()
    graph_years, years, years_ca = ays.scatter_ca_year()
    years_ca = zip(years,years_ca)
    return render_template("ensemble.html",bar=graph,
                           map=map,
                           countries=countries,
                           cr_sp=cr_sp,
                           fid_ind=fid_ind,
                           years=years,
                           years_ca=years_ca,
                           graph_years=graph_years
                           )

@chart.route('/analyse/client')
def client():
    global ays
    email = request.cookies.get('email')
    if email == None: 
        flash("Session expired")
        return redirect(url_for('main.menu'))
    scatter_cat = ays.scatter_ca_seg()
    bar_seg ,seg, dict= ays.bar_country_seg()
    values = ays.table_seg()
    scatter_client,df_c, achat = ays.scatter_ca_client()
    conso_seg = ays.conso_seg()
    return render_template("client.html",
                           scatter_cat=scatter_cat,
                           seg=seg,
                           bar_seg=bar_seg,
                           dict=dict,
                           values=values,
                           scatter_client=scatter_client,
                           conso_seg=conso_seg,
                           df_c=df_c,
                           achat=achat)

@chart.route('/analyse/categorie')
def categorie():
    global ays
    email = request.cookies.get('email')
    if email == None: 
        flash("Session expired")
        return redirect(url_for('main.menu'))
    scatter_cat = ays.scatter_ca_categorie()
    archiv_cat = ays.cat_pref_year()
    scatter_produit = ays.scatter_ca_produit()
    return render_template("categorie.html",
                           scatter_cat=scatter_cat,
                           archiv_cat=archiv_cat,
                           scatter_produit=scatter_produit)
