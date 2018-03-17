#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import ConfigParser
import couchbase
import MySQLdb as mdb
import hashlib

from couchbase.bucket import Bucket


def calculate_hash(arg, method="sha256"):
    method_dict = {
        "md5": hashlib.md5(arg),
        "sha256": hashlib.sha256(arg),
        "sha512": hashlib.sha512(arg)
    }
    return method_dict[method].hexdigest()


class Db(object):
    def __init__(self, couchbase_sup=False):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(os.getcwd(), "modules/config.cfg"))
        self.vt = None
        self.mysql = None
        self.connect_mysql()
        if couchbase_sup:
            cb_config = self.config.get("dbs", "couchbase_param").split(",")
            self.cb = Bucket("couchbase://{0}/{1}".format(cb_config[0], cb_config[1]), username=cb_config[2], password=cb_config[3])

    def connect_mysql(self):
        mysql_config = self.config.get("dbs", "mysql_param").split(",")
        self.mysql = mdb.connect(host=mysql_config[0], user=mysql_config[1], passwd=mysql_config[2], db=mysql_config[3])
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
