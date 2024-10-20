# This file is part of HOMEctlx. Copyright (C) 2024 Christian Rauch.
# Distributed under terms of the GPL3 license.

"""
Offers create, read, update, delete and more for the database.
"""

import datetime
import logging
import sqlite3
from sqlite3 import Error

from flask import g, has_request_context


log = logging.getLogger(__file__)


def init():
    """ Initializes the database."""
    execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            desc TEXT,
            start TEXT,
            state INTEGER)''', False)


def connect():
    """ Open the connection."""
    dbaccess = sqlite3.connect("data.db", check_same_thread=False)
    dbaccess.row_factory = sqlite3.Row  # rows as dictionaries
    return dbaccess


init_dbaccess = None
def connect_cached():
    """ Get the connection."""
    if has_request_context():
        if 'dbaccess' in g: return g.dbaccess
        g.dbaccess = connect()
        return g.dbaccess
    else:
        global init_dbaccess
        if init_dbaccess == None: init_dbaccess = connect()
        return init_dbaccess


def close_cached():
    """ Close the connection."""
    if has_request_context():
        dbaccess = g.pop('dbaccess', None)
        if dbaccess is not None: dbaccess.close()
    else:
        global init_dbaccess
        init_dbaccess.close()
        init_dbaccess = None


def execute(sql:str, fetch:bool, data:tuple=()):
    """ Execute a single command."""
    try:
        connection = connect_cached()
        cursor = connection.cursor()
        cursor.execute(sql, data)
        if fetch: return cursor.fetchall()
        else:
            connection.commit()
            return cursor.lastrowid
    except Error as e: log.error(e)
    finally: 
        if cursor: cursor.close()
        #if connection: connection.close()
        # # closed in teardown_request


state_mapping = {
    'scheduled': 0,
    'running':   1,
    'completed': 2,
    'canceled':  3,
    'failed':    4,
    'unknown':   5,
}
state_mapping_reverse = {v: k for k, v in state_mapping.items()}
def get_tasks(states:list, types:list=None):
    """ Get tasks."""
    states_str = ",".join([str(state_mapping[s]) for s in states])
    sql = f"SELECT * FROM tasks WHERE state IN ({states_str})"
    if types != None:
        types_str = ",".join([f"'{t}'" for t in types])
        sql = f"{sql} AND type IN ({types_str})"
    tasks = execute(sql, True)
    return tasks


def clear_tasks(ids:list=None):
    """ Clear tasks."""
    sql = "DELETE FROM tasks"
    if ids == None: execute(sql, False)
    else: execute(f"{sql} WHERE id IN (?)", False, ([int(i) for i in ids]))


def add_task(type:str, desc:str, state:str='scheduled') -> int:
    """ Add task."""
    now = datetime.datetime.now()
    state = state_mapping[state]
    id = execute(
        """INSERT INTO tasks (type, desc, start, state) 
        VALUES (?, ?, ?, ?)""", False, 
        (type, desc, now, state))
    return id


def get_task_state(id:int):
    states = execute("SELECT state FROM tasks WHERE id = ?", True, tuple([id]))
    if len(states) == 0: return 'unknown'
    state = states[0]['state']
    state = state_mapping_reverse[state]
    return state
