#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import wraps

from flask import Flask, render_template, session, redirect, url_for, request
from modules.main_handler import Processor
from modules.security_handler import is_disabled_account, arguman_controller
from modules.login_handler import Protector

import MySQLdb as mdb

app = Flask(__name__)
app.secret_key = "19d40f906d1f67cf66ccce9d2ea575604ad5f6a4497c5b3863c15eb7db5be779"

main_handler = Processor()
login_handler = Protector()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("logged-in") is None or not session:
            return redirect(url_for('login', next=request.url))
        elif is_disabled_account(session.get("UID")):
            return login_handler.kickout()
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def login():
    return render_template('login.html', page_title="Infox Data Share")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/main")
@login_required
def index():
    return render_template('index.html', page_title="Infox Data Share")


@app.route("/register")
def register():
    return render_template('register.html', page_title="Infox Data Share")


@app.route("/survey")
@login_required
def survey():
    return render_template('survey.html', page_title="Infox Survey")

@app.route("/analytics")
@login_required
def analytics():
    return render_template('analytics.html', page_title="Infox Analytics")


@app.route("/verifier", methods=["POST"])
def verifier():
    process = mdb.escape_string(request.form["PROCESS"])
    ip = request.headers.get("X-Forwarded-For")
    if process == "Register":
        args = {
            "FIRSTNAME": mdb.escape_string(request.form["FIRSTNAME"]).title(),
            "LASTNAME": mdb.escape_string(request.form["LASTNAME"]).upper(),
            "EMAIL": mdb.escape_string(request.form["EMAIL"]).lower(),
            "PASSWORD": mdb.escape_string(request.form["PASSWORD"]),
            "RE-PASSWORD": mdb.escape_string(request.form["RE-PASSWORD"]),
            "MAJORITY": mdb.escape_string(request.form["MAJORITY"]).title(),
            "COUNTRY": mdb.escape_string(request.form["COUNTRY"]).upper(),
            "HOSPITAL": mdb.escape_string(request.form["HOSPITAL"]).title(),
            "CITY": mdb.escape_string(request.form["CITY"]).capitalize()
        }
        control = arguman_controller(args)
        if not control[0]:
            return control[1]
        return login_handler.register(args=args, ip=ip)
    elif process == "Login":
        email = mdb.escape_string(request.form["EMAIL"])
        password = mdb.escape_string(request.form["PASSWORD"])
        return login_handler.sign_in(email=email, password=password, ip=ip)


@app.route("/main-components", methods=["POST"])
def main_components():
    process = mdb.escape_string(request.form["PROCESS"])
    ip = request.headers.get("X-Forwarded-For")
    person = session.get("UID")
    if process == "SaveSurvey":
        return main_handler.save_survey_results(request.form["DATA"], person, ip)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
