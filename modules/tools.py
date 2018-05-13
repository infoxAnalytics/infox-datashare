#!/usr/bin/python
# -*- coding: utf-8 -*-


from functools import wraps
from db_handler import Db
from flask import Response, current_app
from raw_data_handler import get_users_table, get_system_logs_table, get_country_table, get_user_profile_table
from _mysql_exceptions import ProgrammingError
from PIL import Image

import datetime
import random
import os
import re
import json

db_object = Db()


def catch_exception(f):
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            db_object.mysql_rollback()
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Somethings went wrong.Error: {0}".format(e)}))

    return decorated_function


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
            event_log.replace("'", "\'"),
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


def get_event_users():
    return get_system_logs_table(column="DISTINCT(USERNAME)")


def get_country_name(c_code):
    return get_country_table(where="CODE='" + c_code + "'", column="NAME")[0][0]


def get_profile_pic(uid):
    _file = get_user_profile_table(where="ID='" + uid + "'", column="IMAGE")[0][0]
    if not os.path.exists(os.path.join(current_app.config.get("PROJECT_BASE") + current_app.config.get("USER_BASE"), uid + "/images/" + _file)):
        return "http://ssl.gstatic.com/accounts/ui/avatar_2x.png"
    return os.path.join(current_app.config.get("USER_BASE"), uid + "/images/" + _file)


def get_user_base_folder(uid):
    return os.path.join(current_app.config.get("PROJECT_BASE") + current_app.config.get("USER_BASE"), uid)


def image_resize(file_path, w, h):
    image = Image.open(file_path)
    width = image.size[0]
    height = image.size[0]
    newWidth = int(round((width/width) * w))
    newHeight = int(round((height/height) * h))
    newImage = image.resize((newWidth, newHeight), Image.ANTIALIAS)
    newImage.format = image.format
    newImage.save(file_path)
