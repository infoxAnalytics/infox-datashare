#!/usr/bin/python
# -*- coding: utf-8 -*-

from db_handler import Db, calculate_hash
from tools import response_create, write_log_to_mysql, get_username
from flask import session, url_for, redirect
from raw_data_handler import get_users_table

import json
import re
import uuid
import MySQLdb as mdb


class Protector(Db):
    def __init__(self):
        super(Protector, self).__init__(couchbase_sup=False)
        self.system_username = "system"

    """
        Ana fonksiyonların bulunduğu alan aşağıdadır.Ana fonksiyonlar sadece bu alanda tanımlanmalıdır.
    """

    def sign_in(self, email, password, ip):
        event_type = "LOGIN"
        password = calculate_hash(password, method="sha256")
        session_environ = ["UID", "FIRSTNAME", "LASTNAME", "EMAIL", "MAJORITY", "COUNTRY", "STATUS"]
        try:
            user_data = get_users_table(where="EMAIL='" + email + "' AND PASSWORD='" + password + "'", column="ID,F_NAME,L_NAME,EMAIL,MAJORITY,COUNTRY,STATUS")[0]
        except IndexError:
            user_data = tuple()
        if len(user_data) > 0:
            if user_data[-1] in ["Disabled"]:
                return response_create(json.dumps({"STATUS": "error", "ERROR": "Your account is disabled.Please contact Middleware Team."}))
            session["logged-in"] = True
            for i in range(len(session_environ)):
                session[session_environ[i]] = user_data[i]
            log = "Successful login. Email: {0}".format(email)
            write_log_to_mysql("LOGIN", ip, "INFO", log, self.system_username)
            return response_create(json.dumps({"STATUS": "OK", "target": "/main"}))
        log = "Failed login. Email: {0}".format(email)
        write_log_to_mysql(event_type, ip, "WARNING", log, self.system_username)
        return response_create(json.dumps({"STATUS": "error", "ERROR": "Incorrect username or password."}))

    def logout(self):
        session.clear()
        return redirect(url_for('login'))

    def kickout(self):
        session.clear()
        return """<body>
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
                <script>
                        alert('{0}');
                        $(location).attr('href','/');
                    </script>
                </body>""".format("Your account status has been changed.Please contact the system admin.")

    def password_change(self, curr_pass, new_pass, again_pass, ip):
        event_type = "PASSWORD_CHANGE"
        user_id = session.get("UID")
        old_pass = get_users_table(where="ID='" + session.get("UID") + "'", column="PASSWORD")[0][0]
        control = re.compile("^(?=.*?\d)(?=.*?[A-Z])(?=.*?[@.*\-_!])(?=.*?[a-z])[A-Za-z\d@.*\-_!]{8,}$")
        if not bool(control.search(new_pass)):
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Your password is weak.Your password may only contain special characters (@. * -_!), Upper / lower case, and numbers."}))
        if str(old_pass) == str(calculate_hash(new_pass, method="sha512")):
            return response_create(json.dumps({"STATUS": "error", "ERROR": "You have to your change password."}))
        elif str(old_pass) != str(calculate_hash(curr_pass, method="sha512")):
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Your old password is incorrect."}))
        elif str(new_pass) != str(again_pass):
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Your new passwords not match."}))
        else:
            secret = calculate_hash(new_pass, method="sha256")
            changer = "UPDATE users SET PASSWORD='{0}' WHERE UID='{1}'".format(secret, user_id)
            try:
                self.write_mysql(changer)
                session.clear()
                log = "Password changed.User: {0}.".format(" ".join(get_username(user_id)))
                write_log_to_mysql(event_type, ip, "INFO", log, self.system_username)
                return response_create(json.dumps({"STATUS": "OK", "target": "/"}))
            except Exception as e:
                self.mysql_rollback()
                return response_create(json.dumps({"STATUS": "error", "ERROR": "Query could not be completed.Error: {0}".format(e)}))

    def register(self, args, ip):
        event_type = "REGISTER"
        if get_users_table(where="IP='" + ip + "'", count=True) > 0:
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Your IP address not permitted."}))
        if args["PASSWORD"] != args["RE-PASSWORD"]:
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Your passwords does not match."}))
        try:
            uid = str(uuid.uuid4()).split("-")[-1]
            self.write_mysql("INSERT INTO users(ID,F_NAME,L_NAME,EMAIL,MAJORITY,COUNTRY,PASSWORD,CITY,HOSPITAL,IP) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(
                uid, args["FIRSTNAME"], args["LASTNAME"], args["EMAIL"], args["MAJORITY"], args["COUNTRY"], calculate_hash(args["PASSWORD"], "sha256"), args["CITY"], args["HOSPITAL"], ip
            ))
            log = "New user created.Name: {0}, Surname: {1}, Majority: {2}, Country: {3}, UserID: {4}.".format(args["FIRSTNAME"], args["LASTNAME"], args["MAJORITY"], args["COUNTRY"], uid)
            write_log_to_mysql(event_type, ip, "INFO", log, self.system_username)
            self.mysql_commit()
            return response_create(json.dumps({"STATUS": "OK", "target": "/"}))
        except mdb.IntegrityError:
            self.mysql_rollback()
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Your account already created.If you forget your password, contact us."}))
        except Exception as e:
            self.mysql_rollback()
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Query could not be completed.Error: {0}".format(e)}))
