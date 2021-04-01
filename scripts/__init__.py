# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 13:20:18 2021

@author: arman
"""

from .sql import *
from .main import *
from .auth import *
from .analyse import *

TEMPLATE_DIR =  getcwd() + '/templates'
STATIC_DIR =  getcwd()+'/static'
from pandas import read_sql, read_csv
from flask import Flask





def create_app():
    
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
    app.secret_key = '5951'
    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .chart import chart as chart_blueprint
    app.register_blueprint(chart_blueprint)
    
    from .errors import errors as errors_blueprint
    app.register_blueprint(errors_blueprint)
    
    return app