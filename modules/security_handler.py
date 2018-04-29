#!/usr/bin/python
# -*- coding: utf-8 -*-


from tools import response_create
from main_handler import Processor
from raw_data_handler import get_users_table, get_country_table, get_pages_table

import json
import re

main_handler = Processor()


def is_disabled_account(uid):
    if get_users_table(where="ID='" + str(uid) + "' AND STATUS='Disabled'", count=True) > 0:
        return True
    return False


def arguman_controller(args, access=False):
    mail = re.compile("^[a-zA-Z0-9.\-_]+@[a-zA-Z0-9]{,8}\.([a-zA-Z0-9]{,8}\.[a-zA-Z0-9]{,8}|[a-zA-Z0-9]{,8})$")
    names = re.compile(r"^[a-zA-Z ]{,20}$", re.UNICODE)
    hospital = re.compile(r"^[a-zA-Z ]{,50}$", re.UNICODE)
    password = re.compile("^(?=.*?\d)(?=.*?[A-Z])(?=.*?[@.*\-_!])(?=.*?[a-z])[A-Za-z\d@.*\-_!]{8,}$")
    country_codes = re.compile("^{0}$".format("|".join([i[0] for i in get_country_table(column="CODE")])))
    patern = {
        "EMAIL": [mail, "Mail address syntax error."],
        "FIRSTNAME": [names, "Firstname syntax error."],
        "LASTNAME": [names, "Lastname syntax error."],
        "PASSWORD": [password, "Your password is week."],
        "RE-PASSWORD": [password, "Your password is week."],
        "MAJORITY": [names, "Majority syntax error."],
        "COUNTRY": [country_codes, "Invalid country code."],
        "CITY": [names, "Invalid city name."],
        "HOSPITAL": [hospital, "Invalid hospital name."]
    }
    try:
        for k, v in args.iteritems():
            if isinstance(v, list):
                for key in v:
                    if not bool(patern[k][0].search(key)):
                        return False, json.dumps({"STATUS": "error", "ERROR": patern[k][1]})
            elif v not in ["none", "None", "NONE", "all", "All", "ALL"]:
                if not bool(patern[k][0].search(v)):
                    return False, json.dumps({"STATUS": "error", "ERROR": patern[k][1]})
            elif v in ["all", "All", "ALL"]:
                if not access:
                    return False, json.dumps({"STATUS": "error", "ERROR": "Do not use 'All' keyword in this area."})
        return True, 0
    except Exception as e:
        return False, response_create(json.dumps({"STATUS": "error", "ERROR": "Something went wrong.Exception is : " + str(e)}))


def permitted_pages(user_roles):
    where_clause = "(ROLE LIKE '%All%'"
    for r in user_roles:
        where_clause += " OR ROLE LIKE '%{0}%'".format(r)
    where_clause += ") AND APPLICATION='False'"
    return get_pages_table(where=where_clause, column="NAME,LOCATION")


def permitted_application(user_roles):
    where_clause = "(ROLE LIKE '%All%'"
    for r in user_roles:
        where_clause += " OR ROLE LIKE '%{0}%'".format(r)
    where_clause += ") AND APPLICATION='True'"
    return get_pages_table(where=where_clause, column="NAME,LOCATION,IMAGE")
