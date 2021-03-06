#!/usr/bin/python
# -*- coding: utf-8 -*-


from tools import response_create, get_user_base_folder, image_resize, get_survey_image_base_folder
from raw_data_handler import get_users_table, get_country_table, get_pages_table, get_system_logs_table, get_projects_table, get_user_roles_table
from flask import url_for, redirect
from db_handler import Db

import json
import re
import uuid
import os
import magic
import time

db_object = Db()


def is_disabled_account(uid):
    if get_users_table(where="ID='" + str(uid) + "' AND STATUS='Disabled'", count=True) > 0:
        return True
    return False


def arguman_controller(args, log_patern=False):
    mail = re.compile("^[a-zA-Z0-9.\-_]+@[a-zA-Z0-9]{,8}\.([a-zA-Z0-9]{,8}\.[a-zA-Z0-9]{,8}|[a-zA-Z0-9]{,8})$")
    names = re.compile(r"^[a-zA-Z ]{,20}$", re.UNICODE)
    identifier = re.compile(r"^[a-zA-Z0-9 \-]{1,50}$", re.UNICODE)
    hospital = re.compile(r"^[a-zA-Z ]{,50}$", re.UNICODE)
    password = re.compile("^(?=.*?\d)(?=.*?[A-Z])(?=.*?[@.*\-_!])(?=.*?[a-z])[A-Za-z\d@.*\-_!]{8,}$")
    ip = re.compile("^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[\d.*]{,12})$")
    keyword = re.compile("([a-zA-Z0-9.,\-]+)")
    date = re.compile("^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$")
    severity = re.compile("^none|{0}$".format("|".join([i[0] for i in get_system_logs_table(column="DISTINCT(EVENT_SEVERITY)")])))
    etype = re.compile("^none|{0}$".format("|".join([i[0] for i in get_system_logs_table(column="DISTINCT(EVENT_TYPE)")])))
    users = re.compile("^none|{0}$".format("|".join([i[0] for i in get_system_logs_table(column="DISTINCT(USERNAME)")])))
    country_codes = re.compile("^{0}$".format("|".join([i[0] for i in get_country_table(column="CODE")])))
    country_names = re.compile("^{0}$".format("|".join([i[0] for i in get_country_table(column="NAME")])))
    user_id = re.compile("^{0}$".format("|".join([i[0] for i in get_users_table(column="ID")])))
    user_role = re.compile("^{0}$".format("|".join([i[0] for i in get_user_roles_table(column="NAME")])))
    projects = re.compile("^All|none|{0}$".format("|".join([i[0] for i in get_projects_table(column="ID")])))
    patern = {
        "EMAIL": [mail, "Mail address syntax error."],
        "FIRSTNAME": [names, "Firstname syntax error."],
        "LASTNAME": [names, "Lastname syntax error."],
        "PASSWORD": [password, "Your password is week."],
        "RE-PASSWORD": [password, "Your password is week."],
        "MAJORITY": [names, "Majority syntax error."],
        "COUNTRY": [country_codes, "Invalid country code."],
        "CITY": [names, "Invalid city name."],
        "HOSPITAL": [hospital, "Invalid hospital name."],
        "USER_ID": [user_id, "Invalid user id."],
        "PROJECT_ID": [projects, "Invalid project ID."],
        "PROJECT": [projects, "Invalid project."],
        "PROJECT_IDENTIFIER": [identifier, "Invalid project."],
        "USER_STATUS": [re.compile("(enable|delete|disable|activate)"), "Invalid user status."],
        "PROJECT_STATUS": [re.compile("(Active|Passive)"), "Invalid project status."],
        "COUNTRY_NAME": [country_names, "Invalid country name."],
        "ROLE": [user_role, "Invalid role name."],
        "SURVEY_NAME": [names, "Invalid survey name."],
        "SURVEY_EXP": [keyword, "Invalid survey explanation."],
        "PROJECT_EXP": [keyword, "Invalid project explanation."],
        "SURVEY_PIC_FILE": []
    }
    for_log_patern = {
        "ALL_LOG": [re.compile("(True|False)"), "Invalid bool value error."],
        "EVENT_IP": [ip, "Invalid ip error."],
        "EVENT_KEYWORD": [keyword, "Invalid keyword options error."],
        "EVENT_START_DATE": [date, "Invalid date error."],
        "EVENT_END_DATE": [date, "Invalid date error."],
        "EVENT_TYPE": [etype, "Invalid type error."],
        "EVENT_SEVERITY": [severity, "Invalid severity error."],
        "EVENT_USERS": [users, "Invalid user error."]
    }
    try:
        if log_patern:
            if args["ALL_LOG"] == "True":
                return True, 0
            for k, v in args.iteritems():
                if v != "none":
                    if isinstance(v, list):
                        for key in v:
                            if key != "none":
                                if not bool(for_log_patern[k][0].search(key)):
                                    return False, json.dumps({"STATUS": "error", "ERROR": for_log_patern[k][1]})
                    elif not bool(for_log_patern[k][0].search(v)):
                        return False, json.dumps({"STATUS": "error", "ERROR": for_log_patern[k][1]})
        else:
            for k, v in args.iteritems():
                if isinstance(v, list):
                    for key in v:
                        if not bool(patern[k][0].search(key)):
                            return False, json.dumps({"STATUS": "error", "ERROR": patern[k][1]})
                elif k not in ["SURVEY_TEXT", "SURVEY_PIC_FILE"]:
                    if not bool(patern[k][0].search(v)):
                        return False, json.dumps({"STATUS": "error", "ERROR": patern[k][1]})
        return True, 0
    except Exception as e:
        return False, response_create(json.dumps({"STATUS": "error", "ERROR": "Something went wrong.Exception is : " + str(e)}))


def permitted_pages(user_roles):
    where_clause = "(ROLE LIKE '%All%'"
    for r in user_roles:
        where_clause += " OR ROLE LIKE '%{0}%'".format(r)
    where_clause += ") AND PAGE_TYPE='Option' AND STATUS='Enabled'"
    return get_pages_table(where=where_clause, column="NAME,LOCATION")


def permitted_application(user_roles, user_projects):
    where_clause = "(ROLE LIKE '%All%'"
    for r in user_roles:
        where_clause += " OR ROLE LIKE '%{0}%'".format(r)
    where_clause += ") AND PAGE_TYPE='Property' AND (PROJECT LIKE '%All%'"
    for p in user_projects:
        where_clause += " OR PROJECT LIKE '%{0}%'".format(p)
    where_clause += ") AND STATUS='Enabled'"
    return get_pages_table(where=where_clause, column="NAME,LOCATION,IMAGE")


def permitted_sub_application(user_roles, property_name, user_projects):
    where_clause = "(ROLE LIKE '%All%'"
    for r in user_roles:
        where_clause += " OR ROLE LIKE '%{0}%'".format(r)
    where_clause += ") AND PAGE_TYPE='SubProperty' AND PARENT_PAGE='{0}' AND (PROJECT LIKE '%All%'".format(property_name)
    for p in user_projects:
        where_clause += " OR PROJECT LIKE '%{0}%'".format(p)
    where_clause += ") AND STATUS='Enabled'"
    return get_pages_table(where=where_clause, column="NAME,LOCATION,IMAGE,RELATIONAL_ID")


def uploaded_file_security(_file, _type, uid):
    types = {
        "picture": [
            "image/jpeg",
            "image/png",
            "image/png",
            "image/tiff",
            "image/vnd.wap.wbmp",
            "image/x-icon",
            "image/x-jng",
            "image/x-ms-bmp",
            "image/svg+xml",
            "image/webp"
        ],
        "survey_pic": [
            "image/jpeg",
            "image/png",
            "image/png",
            "image/tiff",
            "image/vnd.wap.wbmp",
            "image/x-icon",
            "image/x-jng",
            "image/x-ms-bmp",
            "image/svg+xml",
            "image/webp"
        ]
    }
    tmp_base = os.path.join("/tmp", str(uuid.uuid4()).split("-")[-1])
    os.mkdir(tmp_base)
    _file.save(os.path.join(tmp_base, _file.filename))
    _file_mime = magic.from_file(os.path.join(tmp_base, _file.filename), mime=True)
    if _file_mime in types[_type]:
        if _type == "picture":
            user_base = get_user_base_folder(uid)
            if not os.path.exists(os.path.join(user_base, "images")):
                os.mkdir(os.path.join(user_base, "images"))
                time.sleep(0.5)
            image_resize(os.path.join(tmp_base, _file.filename), 192, 192)
            os.system("mv " + os.path.join(tmp_base, _file.filename) + " " + os.path.join(user_base, "images/{0}.{1}".format(uid, _file.filename.split(".")[-1])))
            time.sleep(0.5)
            os.system("rm -rf " + tmp_base)
            db_object.write_mysql("UPDATE user_profile SET IMAGE='{0}.{1}' WHERE ID='{0}'".format(uid, _file.filename.split(".")[-1]))
            return redirect(url_for("profile"))
        elif _type == "survey_pic":
            survey_base = get_survey_image_base_folder()
            image_resize(os.path.join(tmp_base, _file.filename), 192, 192)
            os.system("mv " + os.path.join(tmp_base, _file.filename) + " " + os.path.join(survey_base, "{0}.{1}".format(uid, _file.filename.split(".")[-1])))
            time.sleep(0.5)
            os.system("rm -rf " + tmp_base)
            return os.path.join(survey_base, "{0}.{1}".format(uid, _file.filename.split(".")[-1]))
    return json.dumps({"STATUS": "error", "ERROR": "Your image type is incompatible."})
