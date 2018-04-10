#!/usr/bin/python
# -*- coding: utf-8 -*-


import json
import os
import sys
import math
import uuid

from db_handler import Db
from tools import write_log_to_mysql, get_username
from tools import response_create
from pymongo import MongoClient


class Processor(Db):
    def __init__(self):
        super(Processor, self).__init__(couchbase_sup=False)
        self.system_username = "Main Handler"
        self.mongodb_client = MongoClient(port=27017)
        self.mongodb = self.mongodb_client.datashare


    def save_survey_results(self, args, person, ip):
        event_type = "SAVE_SURVEY"
        try:
            survey_id = self.mongodb.survey.insert_one(json.loads(args))
            log = "Survey completed by {0}.Survey ID: {1}".format(get_username(person), survey_id.inserted_id)
            write_log_to_mysql(event_type, ip, "INFO", log, self.system_username)
            self.mysql_commit()
            return response_create(json.dumps({"STATUS": "OK", "MESSAGE": "Complete survey successful."}))
        except Exception as e:
            self.mysql_rollback()
            return response_create(json.dumps({"STATUS": "error", "ERROR": e}))
