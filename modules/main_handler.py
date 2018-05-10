#!/usr/bin/python
# -*- coding: utf-8 -*-


from db_handler import Db
from tools import write_log_to_mysql, get_username, response_create, datetime_patern, catch_exception
from raw_data_handler import get_system_logs_table, get_surveys_table, get_users_table, get_projects_table
from flask import abort, session

import json


class Processor(Db):
    def __init__(self):
        super(Processor, self).__init__(couchbase_sup=False, mongo_sup=True)
        self.system_username = "Main Handler"
        self.mongodb = self.mongodb_client.datashare

    @staticmethod
    def get_survey(survey_id):
        if get_surveys_table(where="ID='" + survey_id + "'", count=True) == 0:
            abort(404)
        return get_surveys_table(where="ID='" + survey_id + "'")[0]

    @staticmethod
    def get_pending_account_count():
        return get_users_table(where="STATUS='Pending'", count=True)

    @staticmethod
    def get_pending_account_list():
        return get_users_table(where="STATUS='Pending'", column="F_NAME,L_NAME,EMAIL,MAJORITY,COUNTRY,CITY,HOSPITAL,ROLE,ID")

    @staticmethod
    def get_all_account():
        return get_users_table(where="STATUS!='Pending' ORDER BY STATUS DESC", column="F_NAME,L_NAME,EMAIL,MAJORITY,COUNTRY,CITY,HOSPITAL,ROLE,ID,STATUS,PROJECT")

    @staticmethod
    def get_projects():
        return get_projects_table(where="STATUS='Active'", column="ID,NAME,EXPLANATION")

    @staticmethod
    def get_project_name(project_id):
        if project_id == "none":
            return "None"
        return get_projects_table(where="ID='" + project_id + "'", column="NAME")[0][0]

    @catch_exception
    def save_survey_results(self, args, person, ip):
        event_type = "SAVE_SURVEY"
        survey_data, survey_session_id = args
        survey_data = json.loads(survey_data)
        if session.get("survey_id") != survey_session_id:
            return response_create(json.dumps({"STATUS": "error", "ERROR": "Survey ID is wrong."}))
        survey_data["survey_identifier"] = survey_session_id
        survey_id = self.mongodb.survey.insert_one(survey_data)
        session.pop("survey_id", None)
        f_name, l_name = get_username(person)
        log = "Survey completed by \"{0} {1}\".Survey ID: {2}".format(f_name.title(), l_name.upper(), survey_id.inserted_id)
        write_log_to_mysql(event_type, ip, "INFO", log, self.system_username)
        self.mysql_commit()
        return response_create(json.dumps({"STATUS": "OK", "MESSAGE": "Complete survey successful."}))

    @catch_exception
    def search_log(self, args, person, ip):
        event_type = "LOG_SEARCH"
        where = None
        f_name, l_name = get_username(person)
        navigations = {
            "EVENT_IP": "EVENT_IP",
            "EVENT_KEYWORD": "EVENT",
            "EVENT_TYPE": "EVENT_TYPE",
            "EVENT_SEVERITY": "EVENT_SEVERITY",
            "EVENT_USERS": "USERNAME"
        }
        if args["ALL_LOG"] != "True":
            where = ""
            del args["ALL_LOG"]
            for k, v in args.iteritems():
                if "none" not in v:
                    if not k.endswith("DATE"):
                        if isinstance(v, list):
                            qlist = []
                            for val in v:
                                if val != "none":
                                    if val.endswith("*") and val.startswith("*"):
                                        qlist.append(" {0} LIKE '%{1}%'".format(navigations[k], val.replace("*", "")))
                                    elif val.endswith("*"):
                                        qlist.append(" {0} LIKE '{1}%'".format(navigations[k], val.replace("*", "")))
                                    elif val.startswith("*"):
                                        qlist.append(" {0} LIKE '%{1}'".format(navigations[k], val.replace("*", "")))
                                    else:
                                        qlist.append(" {0}='{1}'".format(navigations[k], val))
                            if len(qlist) > 0:
                                where += " ("
                                where += " OR".join(qlist)
                                where += ") AND"
                        else:
                            if v != "none":
                                if v.endswith("*"):
                                    where += " {0} LIKE '{1}%' AND".format(navigations[k], v.replace("*", ""))
                                elif v.startswith("*"):
                                    where += " {0} LIKE '%{1}' AND".format(navigations[k], v.replace("*", ""))
                                elif v.startswith("*") and v.endswith("*"):
                                    where += " {0} LIKE '%{1}%' AND".format(navigations[k], v.replace("*", ""))
                                else:
                                    where += " {0}='{1}' AND".format(navigations[k], v)
            if args["EVENT_START_DATE"] != "none" and args["EVENT_END_DATE"] != "none":
                where += " EVENT_TIME BETWEEN '{0}' AND '{1}'".format(datetime_patern(pt="js", dt=args["EVENT_START_DATE"], ct="%d.%m.%Y %H:%M"), datetime_patern(pt="js", dt=args["EVENT_END_DATE"], ct="%d.%m.%Y %H:%M"))
            elif args["EVENT_START_DATE"] != "none":
                where += " EVENT_TIME='{0}' AND".format(datetime_patern(pt="js", dt=args["EVENT_START_DATE"], ct="%d.%m.%Y %H:%M"))
            elif args["EVENT_END_DATE"] != "none":
                where += " EVENT_TIME='{0}' AND".format(datetime_patern(pt="js", dt=args["EVENT_END_DATE"], ct="%d.%m.%Y %H:%M"))

            if where.endswith("AND"):
                where = where[0:-3] + " ORDER BY EVENT_TIME ASC"
            if where.endswith("WHERE"):
                return response_create(json.dumps({"STATUS": "error", "ERROR": "No results found for your search criteria."}))
        if where is not None and len(where) > 0:
            result_set = get_system_logs_table(where=where)
        else:
            result_set = get_system_logs_table()
        if len(result_set) > 0:
            html = []
            colors = {
                "ERROR": "btn btn-danger",
                "INFO": "btn btn-info",
                "WARNING": "btn btn-warning",
                "SUCCESS": "btn btn-success",
                "CRITICAL": "btn btn-critical",
                "ATTACK": "btn btn-attack"
            }
            for i in result_set:
                data_set = {
                    "id": i[0],
                    "type": i[1],
                    "ip": i[2],
                    "severity": [i[3], colors[i[3]]],
                    "log": i[4],
                    "timestamp": datetime_patern(dt=i[5]),
                    "username": i[6]
                }
                html.append(data_set)
            return response_create(json.dumps({"STATUS": "OK", "content": html, "q": "Results found."}))
        else:
            log = "Unsuccessful search by \"{0} {1}\" .Search criteria: \"{2}\" .".format(f_name, l_name, "; ".join(["{0}:{1}".format(k, ", ".join(v)) for k, v in args.iteritems() if "none" not in v]))
            write_log_to_mysql(event_type, ip, "ERROR", log, self.system_username)
            return response_create(json.dumps({"STATUS": "error", "ERROR": "No results found for your search criteria."}))

    @catch_exception
    def decide_user_first_status(self, args, person, ip):
        event_type = "REGISTERED_USER_STATUS"
        f_name, l_name = get_username(person)
        t_name, t_surname = get_username(args["USER_ID"])
        if args["USER_STATUS"] == "enable":
            if args["PROJECT"][0] == "none":
                return response_create(json.dumps({"STATUS": "error", "ERROR": "Project is not none for this process."}))
            self.write_mysql("UPDATE users SET STATUS='Enabled', PROJECT='{0}' WHERE ID='{1}'".format(",".join([self.get_project_name(i) for i in args["PROJECT"] if i != "none"]), args["USER_ID"]))
        elif args["USER_STATUS"] == "delete":
            self.write_mysql("DELETE FROM users WHERE ID='{0}'".format(args["USER_ID"]))
            self.write_mysql("DELETE FROM user_profile WHERE ID='{0}'".format(args["USER_ID"]))
        log = "User status changed by \"{0} {1}\".Status: {2}, Projects: {3}, Name: {4}, Surname: {5}.".format(f_name, l_name, args["USER_STATUS"].capitalize(), ",".join([self.get_project_name(i) for i in args["PROJECT"]]), t_name, t_surname)
        write_log_to_mysql(event_type, ip, "INFO", log, self.system_username)
        self.mysql_commit()
        return response_create(json.dumps({"STATUS": "OK", "MESSAGE": "Status changed."}))

    @catch_exception
    def change_user_status(self, args, person, ip):
        event_type = "USER_STATUS_CHANGE"
        f_name, l_name = get_username(person)
        t_name, t_surname = get_username(args["USER_ID"])
        if args["USER_STATUS"] == "enable" or args["USER_STATUS"] == "activate":
            if get_users_table(where="ID='" + args["USER_ID"] + "' AND STATUS IN ('Disabled', 'Deleted')", count=True) > 0:
                self.write_mysql("UPDATE users SET STATUS='Enabled' WHERE ID='{0}'".format(args["USER_ID"]))
        elif args["USER_STATUS"] == "disable":
            if get_users_table(where="ID='" + args["USER_ID"] + "' AND STATUS='Enabled'", count=True) > 0:
                self.write_mysql("UPDATE users SET STATUS='Disabled' WHERE ID='{0}'".format(args["USER_ID"]))
        elif args["USER_STATUS"] == "delete":
            if get_users_table(where="ID='" + args["USER_ID"] + "' AND STATUS IN ('Enabled', 'Disabled')", count=True) > 0:
                self.write_mysql("UPDATE users SET STATUS='Disabled' WHERE ID='{0}'".format(args["USER_ID"]))
        log = "User status changed by \"{0} {1}\".Status: {2}, Name: {3}, Surname: {4}.".format(f_name, l_name, args["USER_STATUS"].capitalize(), t_name, t_surname)
        write_log_to_mysql(event_type, ip, "INFO", log, self.system_username)
        self.mysql_commit()
        return response_create(json.dumps({"STATUS": "OK", "MESSAGE": "Status changed."}))
