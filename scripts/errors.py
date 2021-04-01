# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 23:51:30 2021

@author: arman
"""

from flask import Blueprint, render_template, flash


errors = Blueprint('errors', __name__)

@errors.errorhandler(404)
def not_found(error):
    flash("ERROR 404 ")
    return render_template('errors.html'), 404

@errors.errorhandler(500)
def not_found(error):
    flash("ERROR 500")
    return render_template('errors.html'), 500