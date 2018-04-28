#!/usr/bin/python
# -*- coding: utf-8 -*-


from db_handler import Db
from flask import Response
from raw_data_handler import get_users_table
from _mysql_exceptions import ProgrammingError

import datetime
import random

db_object = Db()


def calculate_banned_time(banned_time):
    return datetime.datetime.now() + datetime.timedelta(minutes=banned_time)


def sorter(data, index, reverse=False):
    return sorted(data, key=lambda k: k[index], reverse=reverse)


def datetime_patern(pt=None, dt=None, ct=None):
    patern_dict = {
        "ts": "%d-%m-%Y %H:%M:%S",
        "br": "%d/%m/%Y",
        "mysql": "%Y-%m-%d %H:%M:%S",
        "js": "%Y-%m-%d %H:%M"
    }
    if pt is None:
        pt = "ts"
    if dt is not None:
        if ct is None:
            return dt.strftime(patern_dict[pt])
        return datetime.datetime.strptime(dt, ct).strftime(patern_dict[pt])
    return datetime.datetime.now().strftime(patern_dict[pt])


def response_create(data, rtype="json"):
    avail_rsp = {
        "json": "application/json"
    }
    return Response(data, mimetype=avail_rsp[rtype])


def write_log_to_mysql(event_type, event_ip, severity, event_log, username):
    try:
        query = "INSERT INTO system_logs VALUES (NULL, '{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(
            event_type,
            event_ip,
            severity,
            event_log.replace("'", "-"),
            datetime_patern("mysql"),
            username
        )
        db_object.write_mysql(query)
        db_object.mysql_commit()
    except ProgrammingError:
        db_object.mysql_rollback()


def get_random_pass():
    pass_gen = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    return "".join(random.sample(pass_gen, 8))


def get_username(uid):
    return get_users_table(where="ID='" + uid + "'", column="F_NAME,L_NAME")[0]
