# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 13:29:57 2021

@author: arman
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
import re 
from .sql import *
from pandas import read_sql
from flask import make_response
auth = Blueprint('auth', __name__)

def check(email): 
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):  
        return True    
    else:  
        return False
    
    
@auth.route('/login')
def login():
    if request.cookies.get('email'):
        return redirect(url_for('main.menu'))
    return render_template("login.html")


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    #remember = True if request.form.get('remember') else False
    sql = SQL()
    with sql.connect() as engine:
        req = "select * from auth where email='"+email+"'"
        user = read_sql(req,engine)
    if len(user['email']) == 0 :
        flash('Mauvaise email')
        return redirect(url_for('auth.login'))
    elif user['password'][0] != str(password) :
        flash('Mauvais mot de passe')
        return redirect(url_for('auth.login'))
    resp = make_response(redirect(url_for('main.menu')))

    resp.set_cookie('username', str(user['prenom'][0]),max_age=3600)
    resp.set_cookie('email', str(user['email'][0]),max_age=3600)

    return resp
    

@auth.route('/signup')
def signup():
    country = ["United Kingdom",
                "France",
                "Australia",
                "Netherlands",
                "Germany",
                "Norway",
                "EIRE",
                "Switzerland",
                "Spain",
                "Poland",
                "Portugal",
                "Italy",
                "Belgium",
                "Lithuania",
                "Japan",
                "Iceland",
                "Channel Islands",
                "Denmark",
                "Cyprus",
                "Austria",
                "Finland",
                "Sweden",
                "Greece",
                "Singapore",
                "Lebanon",
                "United Arab Emirates",
                "Israel",
                "Saudi Arabia",
                "Czech Republic",
                "Canada",
                "Unspecified",
                "Brazil",
                "USA",
                "European Community",
                "Bahrain",
                "Malta",
                "RSA"]
    country = sorted(country)
    return render_template("signup.html", country=country)

@auth.route('/signup', methods=['POST'])
def signup_post():
    sql = SQL()
    email = request.form.get('email')
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    country = request.form.get('country')
    pw_1 = request.form.get('pw')
    pw_2 = request.form.get('pw_c')
    with sql.connect() as engine:
        req = "select * from auth where email='"+str(email)+"'"
        user = read_sql(req,engine)
    if pw_1 != pw_2 :
        flash('Les mots de passe ne correspondent pas')
        return redirect(url_for('auth.signup'))
    elif check(email) == False :
        flash('Mauvaise adresse email')
        return redirect(url_for('auth.signup'))
    elif len(user['email']) != 0 :
        flash('Email déja utilisée')
        return redirect(url_for('auth.signup'))
    user = {'email':email,'password':pw_1,'nom': nom,'prenom':prenom,'country':country,'role':'customer'}
    with sql.connect() as engine:
        cur = engine.cursor()
        cur.execute('INSERT INTO auth (email, password, nom, prenom, country,role) VALUES (:email, :password, :nom, :prenom, :country, :role);', user)
    
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    resp = make_response(redirect(url_for('main.index')))
    resp.delete_cookie('username')
    resp.delete_cookie('email')
    return resp