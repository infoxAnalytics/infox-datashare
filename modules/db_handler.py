#!/usr/bin/python
# -*- coding: utf-8 -*-


from couchbase.bucket import Bucket
from pymongo import MongoClient
from config import election

import couchbase
import MySQLdb as mdb
import hashlib
import os


def calculate_hash(arg, method="sha256"):
    method_dict = {
        "md5": hashlib.md5(arg),
        "sha256": hashlib.sha256(arg),
        "sha512": hashlib.sha512(arg)
    }
    return method_dict[method].hexdigest()


class Db(object):
    def __init__(self, couchbase_sup=False, mongo_sup=False):
        self.cfg = election[os.getenv("TARGET_PLATFORM")]
        self.vt = None
        self.mysql = None
        self.connect_mysql()
        if couchbase_sup:
            cb_config = self.cfg.COUCHBASE_PARAM
            self.cb = Bucket("couchbase://{0}/{1}".format(cb_config[0], cb_config[1]), username=cb_config[2], password=cb_config[3])
        if mongo_sup:
            mongo_cfg = self.cfg.MONGO_PARAM
            self.mongodb_client = MongoClient(host=mongo_cfg[0], port=int(mongo_cfg[1]))

    def connect_mysql(self):
        mysql_config = self.cfg.MYSQL_PARAM
        self.mysql = mdb.connect(host=mysql_config[0], user=mysql_config[1], passwd=mysql_config[2], db=mysql_config[3], port=int(mysql_config[4]))
        self.mysql.autocommit(False)
        self.vt = self.mysql.cursor()

    def write_mysql(self, query):
        try:
            self.vt.execute(query)
            return True
        except mdb.OperationalError:
            self.connect_mysql()
            self.vt.execute(query)
            return True

    def count_mysql(self, query):
        try:
            self.vt.execute(query)
            return self.vt.rowcount
        except mdb.OperationalError:
            self.connect_mysql()
            self.vt.execute(query)
            return self.vt.rowcount

    def readt_mysql(self, query):
        try:
            self.vt.execute(query)
            self.mysql_commit()
            return self.vt.fetchall()
        except mdb.OperationalError:
            self.connect_mysql()
            self.vt.execute(query)
            self.mysql_commit()
            return self.vt.fetchall()

    def mysql_commit(self):
        self.mysql.commit()

    def mysql_rollback(self):
        self.mysql.rollback()

    def write_couchbase(self, arg):
        key = calculate_hash(arg.keys()[0])
        values = []
        for i in arg.values():
            if isinstance(i, str):
                values.append(calculate_hash(i))
                continue
            if isinstance(i, list):
                for e in i:
                    values.append(calculate_hash(e))
                continue
            values.append(i)
        try:
            self.cb.insert(key, values)
        except couchbase.exceptions.KeyExistsError:
            self.cb.replace(key, values)
        return True

    def readt_couchbase(self, key):
        try:
            return True, self.cb.get(calculate_hash(key)).value
        except couchbase.exceptions.NotFoundError:
            return False, 0

    def delete_key_couchbase(self, key):
        try:
            self.cb.delete(calculate_hash(key), quiet=True)
        except couchbase.exceptions.NotFoundError:
            pass
        finally:
            return True
