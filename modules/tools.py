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
import json
import logging
import uuid

db_object = Db()


class FileLogger(object):
    def __init__(self):
        from config import election
        logger = logging.getLogger("InfoxAnalytics")
        handler = logging.FileHandler(os.path.join(election[os.getenv("TARGET_PLATFORM")].LOGGING_BASE, "application.log"))
        formatter = logging.Formatter("%(custom_timestamp)s %(event_type)s %(event_ip)s %(levelname)s %(event_user)s [%(message)s]")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.getLevelName(election[os.getenv("TARGET_PLATFORM")].LOG_LEVEL))
        self.logging_convert_table = {
            "INFO": logger.info,
            "ERROR": logger.error,
            "WARNING": logger.warning,
            "CRITICAL": logger.critical
        }

    def write_log(self, event_type, event_ip, severity, event_log, username):
        logger_extras = {
            "custom_timestamp": datetime_patern(),
            "event_type": event_type,
            "event_ip": event_ip,
            "event_user": username
        }
        self.logging_convert_table[severity](event_log, extra=logger_extras)


f_logger = FileLogger()


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


def get_uuid():
    return str(uuid.uuid4()).split("-")[-1]


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
    f_logger.write_log(event_type, event_ip, severity, event_log, username)
    try:
        query = "INSERT INTO system_logs VALUES (NULL, '{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(
            event_type,
            event_ip,
            severity,
            event_log.replace("\'", "\\'"),
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


def get_survey_image_base_folder():
    return current_app.config.get("SURVEY_IMAGE_BASE")


def is_obj_in(obj, target, make_list=False, sep=","):
    if not make_list:
        return obj in target
    return obj in target.split(sep)


def image_resize(file_path, w, h):
    image = Image.open(file_path)
    width = image.size[0]
    height = image.size[0]
    new_width = int(round((width/width) * w))
    new_height = int(round((height/height) * h))
    new_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    new_image.format = image.format
    new_image.save(file_path)


def update_db_changeset(changeset_config, env):
    with open(changeset_config, "r") as config:
        cfg = json.load(config)
    for c_set in cfg["changeset"]:
        if "id" not in c_set or "id" in c_set and db_object.count_mysql("SELECT ID FROM changelog WHERE ID='" + c_set["id"] + "'") == 0:
            if "id" not in c_set and env == "prod":
                raise ValueError("Database changes should ran development environment firstly !!!")
            if "id" in c_set:
                change_id = c_set["id"]
            else:
                change_id = get_uuid()
                c_set["id"] = change_id
            change_dml = None
            for ch in c_set["changes"]:
                if ch["object"] in ["table"]:
                    if ch["type"] in ["create"]:
                        change_dml = ch["type"].upper() + " " + ch["object"].upper() + " " + ch["name"] + "({0})".format(", ".join(ch["properties"]))
                    elif ch["type"] in ["alter"]:
                        change_dml = ch["type"].upper() + " " + ch["object"].upper() + " " + ch["name"] + " {0}".format("".join(ch["properties"]))
                elif ch["object"] in ["data"]:
                    if ch["type"] in ["delete"]:
                        change_dml = "DELETE FROM " + ch["name"] + " " + "".join(ch["properties"])
                db_object.write_mysql(change_dml)
            db_object.write_mysql("INSERT INTO changelog VALUES (\"{0}\",\"{1}\",\"{2}\")".format(change_id, c_set["author"], change_dml))
            db_object.mysql_commit()
            with open(changeset_config, "w") as config:
                json.dump(cfg, config, indent=4)
