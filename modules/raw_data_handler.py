#!/usr/bin/python
# -*- coding: utf-8 -*-


from db_handler import Db

db_object = Db()


def get_users_table(where=None, column="*", count=False):
    q = "SELECT {0} FROM users".format(column)
    if where is not None:
        q = "SELECT {0} FROM users WHERE {1}".format(column, where)
    if not count:
        return db_object.readt_mysql(q)
    return db_object.count_mysql(q)


def get_country_table(where=None, column="*", count=False):
    q = "SELECT {0} FROM country".format(column)
    if where is not None:
        q = "SELECT {0} FROM country WHERE {1}".format(column, where)
    if not count:
        return db_object.readt_mysql(q)
    return db_object.count_mysql(q)


def get_pages_table(where=None, column="*", count=False):
    q = "SELECT {0} FROM pages".format(column)
    if where is not None:
        q = "SELECT {0} FROM pages WHERE {1}".format(column, where)
    if not count:
        return db_object.readt_mysql(q)
    return db_object.count_mysql(q)


def get_system_logs_table(where=None, column="*", count=False):
    q = "SELECT {0} FROM system_logs".format(column)
    if where is not None:
        q = "SELECT {0} FROM system_logs WHERE {1}".format(column, where)
    if not count:
        return db_object.readt_mysql(q)
    return db_object.count_mysql(q)


def get_user_profile_table(where=None, column="*", count=False):
    q = "SELECT {0} FROM user_profile".format(column)
    if where is not None:
        q = "SELECT {0} FROM user_profile WHERE {1}".format(column, where)
    if not count:
        return db_object.readt_mysql(q)
    return db_object.count_mysql(q)


def get_surveys_table(where=None, column="*", count=False):
    q = "SELECT {0} FROM surveys".format(column)
    if where is not None:
        q = "SELECT {0} FROM surveys WHERE {1}".format(column, where)
    if not count:
        return db_object.readt_mysql(q)
    return db_object.count_mysql(q)


def get_projects_table(where=None, column="*", count=False):
    q = "SELECT {0} FROM projects".format(column)
    if where is not None:
        q = "SELECT {0} FROM projects WHERE {1}".format(column, where)
    if not count:
        return db_object.readt_mysql(q)
    return db_object.count_mysql(q)


def get_user_roles_table(where=None, column="*", count=False):
    q = "SELECT {0} FROM user_roles".format(column)
    if where is not None:
        q = "SELECT {0} FROM user_roles WHERE {1}".format(column, where)
    if not count:
        return db_object.readt_mysql(q)
    return db_object.count_mysql(q)
