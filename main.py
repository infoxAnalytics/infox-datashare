#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import wraps

from flask import Flask, render_template, session, redirect, url_for, request, abort
from modules.main_handler import Processor
from modules.security_handler import is_disabled_account, arguman_controller, permitted_pages, permitted_application, uploaded_file_security
from modules.login_handler import Protector
from modules.tools import get_event_users, get_country_name, get_profile_pic

import MySQLdb as mdb

app = Flask(__name__)
app.secret_key = "19d40f906d1f67cf66ccce9d2ea575604ad5f6a4497c5b3863c15eb7db5be779"
app.config["USER_BASE"] = "/home/ghost/Desktop/Workshop/AnalyticsProject/infox-datashare/static/user_base"

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


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for r in session.get("ROLE").split(","):
                if r in roles:
                    return f(*args, **kwargs)
            abort(401, "You don't have permission to do this action!!!")

        return wrapped

    return wrapper


@app.route("/register")
def register():
    return render_template('register.html', page_title="Infox Data Share")


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
@requires_roles("User", "Admin")
def index():
    return render_template('index.html', page_title="Infox Data Share", pages=permitted_pages(session.get("ROLE").split(",")), application=permitted_application(session.get("ROLE").split(",")))


@app.route("/survey")
@login_required
@requires_roles("User", "Admin")
def survey():
    return render_template('survey.html', page_title="Infox Data Share / Survey", pages=permitted_pages(session.get("ROLE").split(",")))


@app.route("/analytics")
@login_required
@requires_roles("User", "Admin")
def analytics():
    return render_template('analytics.html', page_title="Infox Data Share / Analytics", pages=permitted_pages(session.get("ROLE").split(",")))


@app.route("/profile")
@login_required
@requires_roles("User", "Admin")
def profile():
    return render_template(
        'profile.html',
        page_title="Infox Data Share / Profile",
        pages=permitted_pages(session.get("ROLE").split(",")),
        get_country_name=get_country_name,
        get_profile_pic=get_profile_pic(session.get("UID"))
    )


@app.route("/system-log")
@login_required
@requires_roles("Admin")
def system_log():
    return render_template('log.html', page_title="Infox Data Share / System Log", pages=permitted_pages(session.get("ROLE").split(",")), log_event_users=get_event_users())


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
@requires_roles("User", "Admin")
def main_components():
    process = mdb.escape_string(request.form["PROCESS"])
    ip = request.headers.get("X-Forwarded-For")
    person = session.get("UID")
    if process == "SaveSurvey":
        return main_handler.save_survey_results(args=request.form["DATA"], person=person, ip=ip)
    elif process == "ProfilePicChange":
        return uploaded_file_security(_file=request.files["profile_pic"], _type="picture", uid=session.get("UID"))


@app.route("/admin-components", methods=["POST"])
@requires_roles("Admin")
def admin_components():
    process = mdb.escape_string(request.form["PROCESS"])
    ip = request.headers.get("X-Forwarded-For")
    person = session.get("UID")
    if process == "SearchLog":
        args = {
            "ALL_LOG": mdb.escape_string(request.form["ALL_LOG"]),
            "EVENT_IP": mdb.escape_string(request.form["EVENT_IP"]).split(";"),
            "EVENT_KEYWORD": mdb.escape_string(request.form["EVENT_KEYWORD"]).split(";"),
            "EVENT_START_DATE": mdb.escape_string(request.form["EVENT_START_DATE"]),
            "EVENT_END_DATE": mdb.escape_string(request.form["EVENT_END_DATE"]),
            "EVENT_TYPE": mdb.escape_string(request.form["EVENT_TYPE"]).split(","),
            "EVENT_SEVERITY": mdb.escape_string(request.form["EVENT_SEVERITY"]).split(","),
            "EVENT_USERS": mdb.escape_string(request.form["EVENT_USERS"]).split(",")
        }
        control = arguman_controller(args, log_patern=True)
        if not control[0]:
            return control[1]
        return main_handler.search_log(args=args, person=person, ip=ip)


if __name__ == '__main__':
    app.run(port=5000, debug=True)
