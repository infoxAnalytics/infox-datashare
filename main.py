#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import wraps
import os
import sys

from flask import Flask, render_template, session, redirect, url_for, request
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = "19d40f906d1f67cf66ccce9d2ea575604ad5f6a4497c5b3863c15eb7db5be779"
app.config['MONGO_DBNAME'] = 'datashare'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/datashare'
mongo = PyMongo(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("logged-in") is None or not session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def login():
    return render_template('login.html', page_title="Infox Data Share")


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/main')
@login_required
def index():
    return render_template('index.html', page_title="Infox Data Share")


@app.route('/register')
def register():
    return render_template('register.html', page_title="Infox Data Share")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
