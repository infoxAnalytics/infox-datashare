#!/usr/bin/python
# -*- coding: utf-8 -*-

from functools import wraps

import sys
import os

try:
    os.environ["TARGET_PLATFORM"] = sys.argv[1]
except IndexError:
    os.environ["TARGET_PLATFORM"] = "dev"

from flask import Flask, render_template, session, redirect, url_for, request, abort
from modules.main_handler import Processor
from modules.security_handler import is_disabled_account, arguman_controller, permitted_pages, permitted_application, uploaded_file_security, permitted_sub_application
from modules.login_handler import Protector
from modules.tools import get_event_users, get_country_name, get_profile_pic, get_username
from datetime import timedelta
from modules.config import election
from modules.raw_data_handler import get_users_table, get_projects_table, get_user_roles_table

import MySQLdb as mdb

app = Flask(__name__)
app.secret_key = "19d40f906d1f67cf66ccce9d2ea575604ad5f6a4497c5b3863c15eb7db5be779"
app.config["DEBUG"] = election[os.getenv("TARGET_PLATFORM")].DEBUG
app.config["USER_BASE"] = election[os.getenv("TARGET_PLATFORM")].USER_BASE

main_handler = Processor()
login_handler = Protector()


@app.before_request
def make_session_permanent():
    if session.get("logged-in") is not None:
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=30)
        session.modified = True


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("logged-in") is None or not session:
            return redirect(url_for('login', next=request.path))
        elif is_disabled_account(session.get("UID")):
            return login_handler.kickout()
        return f(*args, **kwargs)

    return decorated_function


def session_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("logged-in") is not None or session:
            return redirect(url_for('index'))
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


def before_process(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session.pop("survey_id", None)
        if request.path == "/modify-user":
            if request.args.get("name") == session.get("UID"):
                abort(401, "You don't have permission to do this action!!!")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/register")
@session_check
def register():
    return render_template('register.html', page_title="Infox Data Share")


@app.route("/")
@session_check
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
@before_process
def index():
    return render_template(
        'index.html',
        page_title="Infox Data Share",
        pages=permitted_pages(session.get("ROLE").split(",")),
        application=permitted_application(session.get("ROLE").split(","), session.get("PROJECT").split(","))
    )


@app.route("/survey")
@login_required
@requires_roles("User", "Admin")
@before_process
def survey():
    return render_template(
        'survey.html',
        page_title="Infox Data Share",
        pages=permitted_pages(session.get("ROLE").split(",")),
        application=permitted_sub_application(session.get("ROLE").split(","), "Survey", session.get("PROJECT").split(","))
    )


@app.route("/do-survey")
@login_required
@requires_roles("User", "Admin")
def do_survey():
    survey_id = request.args.get("name")
    session["survey_id"] = survey_id
    p_data = main_handler.get_survey(survey_id)
    return render_template(
        'do_survey.html',
        page_title="Infox Data Share",
        pages=permitted_pages(session.get("ROLE").split(",")),
        survey_name=p_data[1],
        survey_explanation=p_data[3],
        survey_json=p_data[2],
        survey_id=survey_id
    )


@app.route("/analytics")
@login_required
@requires_roles("User", "Admin")
@before_process
def analytics():
    return render_template(
        'analytics.html',
        page_title="Infox Data Share",
        pages=permitted_pages(session.get("ROLE").split(","))
    )


@app.route("/profile")
@login_required
@requires_roles("User", "Admin")
@before_process
def profile():
    return render_template(
        'profile.html',
        page_title="Infox Data Share",
        pages=permitted_pages(session.get("ROLE").split(",")),
        get_country_name=get_country_name,
        get_profile_pic=get_profile_pic(session.get("UID"))
    )


@app.route("/modify-user")
@login_required
@requires_roles("User", "Admin")
@before_process
def modify_user():
    user_id = request.args.get("name")
    user_data = get_users_table(where="ID='" + user_id + "'", column="ID,EMAIL,MAJORITY,COUNTRY,CITY,HOSPITAL,ROLE,STATUS,PROJECT")[0]
    return render_template(
        'modify_user.html',
        page_title="Infox Data Share",
        pages=permitted_pages(session.get("ROLE").split(",")),
        username=" ".join(get_username(user_id)),
        user_data=user_data,
        get_country_name=get_country_name,
        get_profile_pic=get_profile_pic(user_id),
        projects=get_projects_table(where="STATUS='Active'"),
        roles=get_user_roles_table()
    )


@app.route("/system-log")
@login_required
@requires_roles("Admin")
@before_process
def system_log():
    return render_template(
        'log.html',
        page_title="Infox Data Share",
        pages=permitted_pages(session.get("ROLE").split(",")),
        log_event_users=get_event_users()
    )


@app.route("/management")
@login_required
@requires_roles("Admin")
@before_process
def management():
    return render_template(
        'management.html',
        page_title="Infox Data Share",
        pages=permitted_pages(session.get("ROLE").split(",")),
        pending_count=main_handler.get_pending_account_count(),
        pending_list=main_handler.get_pending_account_list(),
        get_country_name=get_country_name,
        projects=main_handler.get_projects(),
        all_users=main_handler.get_all_account()
    )


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
        return main_handler.save_survey_results(args=(request.form["DATA"], request.form["SURVEY_ID"]), person=person, ip=ip)
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
    elif process == "DecideFirstStatus":
        args = {
            "USER_ID": mdb.escape_string(request.form["USER_ID"]),
            "PROJECT": mdb.escape_string(request.form["PROJECT"]).split(","),
            "USER_STATUS": mdb.escape_string(request.form["USER_STATUS"])
        }
        control = arguman_controller(args)
        if not control[0]:
            return control[1]
        return main_handler.decide_user_first_status(args=args, person=person, ip=ip)
    elif process == "ChangeUserStatus":
        args = {
            "USER_ID": mdb.escape_string(request.form["USER_ID"]),
            "USER_STATUS": mdb.escape_string(request.form["USER_STATUS"])
        }
        control = arguman_controller(args)
        if not control[0]:
            return control[1]
        return main_handler.change_user_status(args=args, person=person, ip=ip)
    elif process == "ChangeUserDetails":
        args = {
            "USER_ID": mdb.escape_string(request.form["USER_ID"]),
            "MAJORITY": mdb.escape_string(request.form["MAJORITY"]).title(),
            "COUNTRY_NAME": mdb.escape_string(request.form["COUNTRY_NAME"]).title(),
            "HOSPITAL": mdb.escape_string(request.form["HOSPITAL"]).title(),
            "CITY": mdb.escape_string(request.form["CITY"]).capitalize(),
            "USER_ROLE": mdb.escape_string(request.form["ROLE"]).capitalize(),
            "PROJECT": mdb.escape_string(request.form["PROJECTS"])
        }
        control = arguman_controller(args)
        if not control[0]:
            return control[1]
        return main_handler.change_user_details(args=args, person=person, ip=ip)


if __name__ == '__main__':
    app.run(port=5000)
