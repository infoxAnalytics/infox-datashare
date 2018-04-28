#!/usr/bin/python
# -*- coding: utf-8 -*-


from db_handler import Db
from tools import write_log_to_mysql, get_username
from tools import response_create

import json


class Processor(Db):
    def __init__(self):
        super(Processor, self).__init__(couchbase_sup=False, mongo_sup=True)
        self.system_username = "Main Handler"
        self.mongodb = self.mongodb_client.datashare

    def save_survey_results(self, args, person, ip):
        event_type = "SAVE_SURVEY"
        try:
            survey_id = self.mongodb.survey.insert_one(json.loads(args))
            f_name, l_name = get_username(person)
            log = "Survey completed by '{0} {1}'.Survey ID: {2}".format(f_name.title(), l_name.upper(), survey_id.inserted_id)
            write_log_to_mysql(event_type, ip, "INFO", log, self.system_username)
            self.mysql_commit()
            return response_create(json.dumps({"STATUS": "OK", "MESSAGE": "Complete survey successful."}))
        except KeyboardInterrupt as e:
            self.mysql_rollback()
            return response_create(json.dumps({"STATUS": "error", "ERROR": str(e)}))
