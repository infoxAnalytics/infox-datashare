#!/usr/bin/python
# -*- coding: utf-8 -*-


import json
import os
import sys
import math
import uuid

from db_handler import Db, calculate_hash
from flask import session


class Processor(Db):
    def __init__(self):
        super(Processor, self).__init__(couchbase_sup=False)
