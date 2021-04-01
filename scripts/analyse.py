# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 15:33:14 2021

@author: arman
"""

from .sql import *
import pandas as pd
import numpy as np
from random import randrange
from collections import Counter
import json
import plotly
import plotly.graph_objs as go
import plotly.express as px
from random import randrange
from datetime import datetime
import pycountry
from utils.tools import *
from pickle import load
from os import getcwd

"""
input model
['value','frequence','avg_basket','cat_1','cat_2','cat_3','cat_4','france','germany','other','uk']
"""

class Analyse:
    def __init__(self):
        
        path = getcwd()
        with open(path+'/model/model_final.pkl', 'rb') as file:
            self.lr = load(file)
        sql = SQL()
        with sql.connect() as engine:
            req = "select * from invoices"
            self.df = pd.read_sql(req,engine)
            req  ="select * from customers"
            self.df_parquet = pd.read_sql(req,engine)
        cat = pd.unique(self.df['Catégorie'])
        dict = {k:i for i,k in enumerate(cat)}
        self.df['Catégorie_format_num'] = self.df['Catégorie'].apply(lambda x : dict[x])
        self.init_client()
        with sql.connect() as engine:
            req  ="select * from customers"
            self.df_customer = pd.read_sql(req,engine)
        # self.df_customer = pd.concat([df_groupby.drop('Country',axis=1) ,pd.get_dummies(df_groupby['Country'])], axis=1)
        self.df_produit =self.df.groupby(by=['Catégorie']).sum()
        self.df = self.df.set_index('CustomerID').join(self.df_customer.set_index('CustomerID')['label']).reset_index()

    
    """
    Vue D'ensemble
    """
        
    #Indicateur de l'évolution du CA
    def indicateur_ca(self):
        df = self.df
        df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
        df = df.sort_values(by=['date'], ascending=False)
        df_gr = df.groupby(by=['date']).CA.sum().apply(lambda x : round(x,2))
        date = df_gr.index[-12:]
        ca = df_gr.values[-12:]
        now = datetime.now()
        current_time = now.strftime("%Y/%m")
        act = ca[-1] if current_time != date[-1] else ca[-2]
        before = ca[-2] if current_time != date[-1] else ca[-3]
        fig = go.Figure(go.Indicator(mode = "number+delta",
        value = act,
        delta = {"reference": before, "valueformat": ".0f"},
        title = {"text": "Chiffre d'affaires"}))
        fig.add_trace(go.Scatter(
            y = ca, x=[d for d in date], name="Chiffre d'affaires"))
        fig.update_layout(hovermode="x",title={
        'text': "Evolution du CA par mois",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
        graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph
        
    def map_ca(self):
        df = self.df.groupby(by=["Country"]).sum()
        for country in df.index :
            try :
                df.loc[country,'iso'] = pycountry.countries.get(name=country).alpha_3
            except :
                df.loc[country,'iso'] = None 
        df = df.drop(['European Community','Unspecified'])
        df.loc[['Channel Islands','Czech Republic','EIRE','RSA','USA'],'iso'] = ['CXR','CZE','IRL','ZAF','USA']
        df = df.drop("United Kingdom")
        df = df.dropna().reset_index()
        fig = px.choropleth(df,
                            locations="iso",
                            color="CA",
                            hover_name="Country",
                            color_continuous_scale=px.colors.sequential.Plasma
                            )
        fig.update_layout(hovermode="x",title={
        'text': "Répartition du chiffre d'affaires (CA) par pays",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
        graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph
    
    def scatter_ca(self):
        graph={}
        df = self.df.set_index('Country')
        countries = pd.unique(df.index)
        for country in countries:
            df_c = df.loc[country]
            df_c['date'] = df_c['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
            df_c = df_c.sort_values(by=['date'], ascending=False)
            df_gr = df_c.groupby(by=['date']).CA.sum().apply(lambda x : round(x,2))
            date = df_gr.index[-12:]
            ca = df_gr.values[-12:]
            data = [
                go.Scatter(
                    x=date, # assign x as the dataframe column 'x'
                    y=ca,
                    mode='lines',
                    marker_color='rgb('+str(randrange(0,255))+', '+str(randrange(0,255))+', '+str(randrange(0,255))+')',                
                    name= country
                )
            ]
            graph[country] = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return graph
    
    #indicateur de croissance
    def croissance_speed(self):
        df = self.df
        df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
        df = df.sort_values(by=['date'], ascending=False)
        df = df.groupby(by=['date']).sum().apply(lambda x : round(x,2))
        CA = [int(d) for d in df['CA']][::-1]
        value = [CA[i]-CA[i+1] for i in range(len(CA)) if i != len(CA)-1]
        fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = int(value[0]),
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Croissance du Chiffre d'affaires", 'font': {'size': 24}},
        delta = {'reference': int(value[1])},
        gauge = {
            'axis': {'range': [min(value), max(value)], 'tickwidth': 1, 'tickcolor': "rgb(15, 68, 146)"},
            'bar': {'color': "rgb(15, 68, 146)"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "black",
            'steps': [
                {'range': [min(value), int(value[1])], 'color': 'rgb(255, 239, 10)'}],
            'threshold': {
                'line': {'color': "green", 'width': 4},
                'thickness': 0.75,
                'value': int(np.mean(value))}}))
        graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph
    
    #indicateur fidélité
    def indicateur_fid(self):
        df = self.df
        df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
        df = df.sort_values(by=['date'], ascending=False)
        date = pd.unique(df['date'])[:12][::-1]
        nb_v = [i*0.001 for i in df.groupby(by=['date']).InvoiceNo.count()][-12:]
        df_c = df.groupby(by=['date','CustomerID'], as_index=False).sum()
        nb_c = [i*0.01 for i in df_c.groupby(by=['date']).CustomerID.count()][-12:]
        fig = go.Figure(go.Bar(
                    x=date, # assign x as the dataframe column 'x'
                    y=nb_v,
                    name="Nombre de transaction par mois (en millier)"
                ))
        fig.add_trace(go.Scatter(
            y = nb_c, x=date, name="Nombre de client ayant acheté (en centaine)"))
        fig.update_layout(hovermode="x",title={
        'text': "Evolution de la consommation client",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
        graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph
    
    #archive
    def scatter_ca_year(self):
        df = self.df
        df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
        df['year'] = df['InvoiceDate'].apply(lambda x : str(x).split("-")[0])
        year = [i for i in df.groupby(by=['year']).sum().index]
        year_ca = [int(i) for i in df.groupby(by=['year']).CA.sum()]
        graph={}
        for i in year :
            df_c = df[df['year'] == i]
            df_gr = df_c.groupby(by=['date']).CA.sum().apply(lambda x : round(x,2))
            date = df_gr.index
            ca = df_gr.values
            data = [
                        go.Scatter(
                            x=date, # assign x as the dataframe column 'x'
                            y=ca,
                            mode='lines',
                            marker_color='rgb('+str(randrange(0,255))+', '+str(randrange(0,255))+', '+str(randrange(0,255))+')',                
                            name= i
                        )
                    ]
            graph[i] = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return graph, year, year_ca
    
    """
    produit
    """
    #par catégorie
    def scatter_ca_categorie(self):
        df = self.df
        df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
        categories = self.df_produit.drop('autres').index
        graph={}
        fig = go.Figure()
        for i in categories :
            df_c = df[df['Catégorie'] == i]
            df_gr = df_c.groupby(by=['date']).CA.sum().apply(lambda x : round(x,2))
            date = df_gr.index[-12:]
            ca = df_gr.values[-12:]
            fig.add_trace(
                        go.Scatter(
                            x=date, # assign x as the dataframe column 'x'
                            y=ca,
                            mode='lines',
                            marker_color='rgb('+str(randrange(0,255))+', '+str(randrange(0,255))+', '+str(randrange(0,255))+')',                
                            name= i
                        )
                    )
        fig.update_layout(hovermode="x",title={
        'text': "Evolution du chiffre d'affaires par catégorie de produit",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
        graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph  

    def cat_pref_year(self):
        df = self.df
        df['year'] = df['InvoiceDate'].apply(lambda x : str(x).split("-")[0])
        year = pd.unique(df['year'])
        cat = pd.unique([i for i in df['Catégorie'] if i != "autres"])
        df_c = pd.DataFrame(index=cat,columns=year)
        df = df.groupby(by=['year','Catégorie'], as_index=False).count().set_index('Catégorie').drop('autres')
        for y in year:
            for c in cat:
                df_c.loc[c,y] = df[df['year'] == y].loc[c,'CA']
        return df_c
    
    def scatter_ca_produit(self,limit=100):
        df = self.df
        produits  = pd.unique(df['StockCode'])[:limit]
        df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
        graph={}
        for c in produits :
            df_c = df[df['StockCode'] == c]
            df_gr = df_c.groupby(by=['date']).CA.sum().apply(lambda x : round(x,2))
            date = df_gr.index
            ca = df_gr.values
            data = [
                        go.Scatter(
                            x=date, # assign x as the dataframe column 'x'
                            y=ca,
                            mode='lines',
                            marker_color='rgb('+str(randrange(0,255))+', '+str(randrange(0,255))+', '+str(randrange(0,255))+')',                
                            name= str(c)
                        )
                    ]
            graph[c] = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        return graph
        
    """
    Client
    """
    def init_client(self):
        cat = pd.unique(self.df['Catégorie'])
        dict = {k:i for i,k in enumerate(cat)}
        df_groupby = self.df[['CustomerID','CA','Quantity']]
        df_customer = df_groupby.groupby(by=['CustomerID']).sum()
        frequence =  self.df.groupby('CustomerID').CustomerID.count()
        df_customer['frequence'] = frequence
        panier_moy = self.df.groupby(by = ['CustomerID']).CA.mean()
        df_customer['panier_moyen'] = panier_moy
        df_customer['panier_moyen'] =  df_customer['panier_moyen'].apply(lambda x : round(x,2))
        cat_fav = []
        country = []
        last_purchase = []
        for client in df_customer.index:
            df_c = self.df[self.df['CustomerID'] == client]
            cat_fav.append(Counter([c for c in df_c['Catégorie']]).most_common()[0][0])
            country.append(df_c['Country'].values[0])
            last_purchase.append(max(df_c['InvoiceDate']))
        df_customer['Catégorie_fav'] = cat_fav
        df_customer['Country'] = country
        df_customer['Last_purchase'] = last_purchase
        df_customer['Catégorie_fav_num'] = df_customer['Catégorie_fav'].apply(lambda x : dict[x])
        input_col = ['CA','frequence','panier_moyen',0,1,2,3,'France','Germany','autre','United Kingdom']
        pays = ['France','Germany','United Kingdom']
        df_customer['Country'] = df_customer['Country'].apply(lambda x : x if x in pays else 'autre')
        
        #comparaison avec les données 'static'
        df_customer = df_customer.join(self.df_parquet.set_index('CustomerID')['label']).reset_index()
        df_customer['Last_purchase'] = df_customer['Last_purchase'].apply(lambda x : datetime.strptime(x.split(" ")[0],"%Y-%m-%d"))
        df_customer = df_customer.drop_duplicates()
        now = datetime.now()
        country = pd.get_dummies(df_customer['Country'])
        catégories = pd.get_dummies(df_customer['Catégorie_fav_num']).drop(4,axis=1)
        df_customer_input = pd.concat([df_customer,country,catégories], axis=1)
        
        #ajout de la récence
        df_customer_input['Recency'] = df_customer_input['Last_purchase'].apply(lambda x : int(str(now-x).split(' ')[0]))
        if True in [b for b in df_customer_input['Recency'] < 7]:
            df_customer_input = df_customer_input[df_customer_input['Recency'] < 7]
            X = df_customer_input[input_col]
            
            #prediction de la segmentation ds clients les plus récents
            new_seg = self.lr.predict(X)
            customerID = df_customer_input['CustomerID']
            zip_pred = zip([i for i  in customerID], [c for c in new_seg])
            df_customer = df_customer.set_index('CustomerID')
            for c,l in zip_pred:
                df_customer.loc[c,'label'] = l
            df_customer = df_customer.reset_index() 
            sql=SQL()
            with sql.connect() as engine:
                c = engine.cursor()
                req = "DROP TABLE customers"
                c.execute(req)
                df_customer.to_sql('customers',engine,index=False)
                    
    #CA par segment client                
    def scatter_ca_seg(self):
        df = self.df
        seg = sorted(pd.unique(df['label']))
        df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
        df_dummies = pd.concat([df,pd.get_dummies(df['date']).applymap(lambda x : None if x == 0 else x)],axis=1)
        check_date = df_dummies.drop([c for c in df.columns if c != "label"],axis=1).groupby('label').count()
        check_date = pd.unique([c for c in check_date.columns for i in check_date[c] if i == 0])
        dict = {0:"Client moyen du milieu d'année",1:"Clients fêtes de fin d'année",2:"Gros clients allemands",3:"Les Artistes occasionnels",4:"Reste du monde"}
        graph={}
        fig = go.Figure()
        for i in seg :
            df_c = df[df['label'] == i]
            df_gr = df_c.groupby(by=['date']).CA.sum().apply(lambda x : round(x,2))
            date = [d for d in df_gr.index if d not in check_date][-12:]
            ca = df_gr.values[-12:]
            fig.add_trace(
                        go.Scatter(
                            x=date, # assign x as the dataframe column 'x'
                            y=ca,
                            mode='lines',
                            marker_color='rgb('+str(randrange(0,255))+', '+str(randrange(0,255))+', '+str(randrange(0,255))+')',                
                            name= dict[int(i)]
                        )
                    )
        fig.update_layout(hovermode="x",title={
        'text': "Evolution du chiffre d'affaires par catégorie de client",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
        graph = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph 
    #repartion des clients par segments et par pays
    def bar_country_seg(self):
        seg = sorted(pd.unique(self.df['label']))
        dict = {0:"Clients moyen du milieu d'année",1:"Clients fêtes de fin d'année",2:"Gros clients allemands",3:"Les Artistes occasionnels",4:"Reste du monde"}
        graph = {}
        for s in seg :
            df = self.df[self.df['label']  == s]
            df_c = df.groupby('Country').count()
            fig = go.Figure()
            fig.add_trace(go.Bar(
                    x=[w for w in df_c.index], # assign x as the dataframe column 'x'
                    y=[v for v in df_c['CA']],
                    name=dict[s]
                ))
            fig.update_layout(hovermode="x",title={
            'text': "Répartition des clients par pays",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
            graph[s] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph, seg , dict
    
    #tableau résumant les segments
    def table_seg(self):
        seg = sorted(pd.unique(self.df['label']))
        values = {}
        for s in seg :
            df = self.df_customer[self.df_customer['label']  == s]
            nombre_c = len(df)
            mediane_ca = round(np.quantile(df['CA'], 0.5))
            moyenne_ca = round(np.mean(df['CA']))
            mediane_freq = round(np.quantile(df['frequence'], 0.5))
            moyenne_freq = round(np.mean(df['frequence']))
            mediane_pan= round(np.quantile(df['panier_moyen'], 0.5))
            moyenne_pan = round(np.mean(df['panier_moyen']))
            cat_fav = Counter([c for c in df['Catégorie_fav']]).most_common()[0][0]
            list = [nombre_c,mediane_ca,moyenne_ca,mediane_freq,moyenne_freq,mediane_pan,moyenne_pan,cat_fav]
            values[s] = list
        return values
    
    def conso_seg(self):
        seg = sorted(pd.unique(self.df['label']))
        graph = {}
        for s in seg :
            df = self.df[self.df['label'] == s]
            df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
            df = df.sort_values(by=['date'], ascending=False)
            date = pd.unique(df['date'])[:12][::-1]
            nb_v = [i*0.001 for i in df.groupby(by=['date']).InvoiceNo.count()][-12:]
            df_c = df.groupby(by=['date','CustomerID'], as_index=False).sum()
            nb_c = [i*0.01 for i in df_c.groupby(by=['date']).CustomerID.count()][-12:]
            fig = go.Figure(go.Bar(
                        x=date, # assign x as the dataframe column 'x'
                        y=nb_v,
                        name="Nombre de transaction par mois (en millier)"
                    ))
            fig.add_trace(go.Scatter(
                y = nb_c, x=date, name="Nombre de client ayant acheté (en centaine)"))
            fig.update_layout(hovermode="x",title={
            'text': "Evolution de la consommation client",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
            graph[s] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graph
    
    #analyse par client
    def scatter_ca_client(self,limit=100):
        df = self.df
        customers  = pd.unique(df['CustomerID'])[:limit]
        df['date'] = df['InvoiceDate'].apply(lambda x : "/".join(str(x).split("-")[:2]))
        graph={}
        achat = {}
        df_cu={}
        for c in customers :
            df_c = df[df['CustomerID'] == c]
            df_gr = df_c.groupby(by=['date']).CA.sum().apply(lambda x : round(x,2))
            date = df_gr.index
            ca = df_gr.values
            data = [
                        go.Scatter(
                            x=date, # assign x as the dataframe column 'x'
                            y=ca,
                            mode='lines',
                            marker_color='rgb('+str(randrange(0,255))+', '+str(randrange(0,255))+', '+str(randrange(0,255))+')',                
                            name= str(c)
                        )
                    ]
            graph[c] = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
            df_cu[c] = [v for v in self.df_customer.set_index('CustomerID').loc[c,['label','frequence','panier_moyen','Country']]]
            achat[c] = self.df.set_index('CustomerID').loc[c,['StockCode','InvoiceDate','Quantity','CA']]
        return graph, df_cu, achat

    