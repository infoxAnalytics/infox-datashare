#!/usr/bin/python
# -*- coding: utf-8 -*-


import json
import os
import sys
import math
import uuid

from db_handler import Db
from flask import session
from tools import response_create


class Processor(Db):
    def __init__(self):
        super(Processor, self).__init__(couchbase_sup=False)


    def save_survey_results(self, args, person, ip):
        return response_create(json.dumps({"STATUS": "error", "ERROR": args}))
