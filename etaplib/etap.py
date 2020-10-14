import base64
import hashlib
import json
import subprocess
from typing import List, Any
from pathlib import Path

import sqlite3
import pandas as pd


_emp_tap_binary = ''
_db: sqlite3.Connection = None


def init(emp_tap_binary, db_file=":memory:", init_db=True):
    """
    :param db_file: location of the database
    :param init_db: create a new database or not
    """
    global _db, _emp_tap_binary

    _emp_tap_binary = emp_tap_binary

    _db = sqlite3.connect(db_file, check_same_thread=False)
    _db.row_factory = sqlite3.Row

    if init_db:
        _init_db(_db)


def _init_db(db: sqlite3.Connection):
    """
    Create a new database in the memory
    :return: None
    """
    cur = db.cursor()

    cur.execute(
        'DROP TABLE IF EXISTS circuit_pool;'
    )
    cur.execute(
        'DROP TABLE IF EXISTS rule_description;'
    )

    cur.execute(
        '''
        CREATE TABLE circuit_pool (
            rule_id INTEGER,
            circuit_id INTEGER NOT NULL,
            F BLOB NOT NULL,
            D BLOB NOT NULL,
            PRIMARY KEY (rule_id, circuit_id)
        );
        '''
    )
    cur.execute(
        '''
        CREATE TABLE rule_description (
            rule_id INTEGER PRIMARY KEY,
            description TEXT NOT NULL
        );
        '''
    )

    db.commit()


def add_new_circuit(rule_id, circuit_id, F, D, description=None):
    """
    Insert a rule into the database. If it is already in the database, insert the enc only.
    If the enc queue is already full, replace the oldest enc.
    :param user_id: id of the user who generates this rule
    :param rule_id: id of the rule
    :param rule_info: how the rule is performed
    :param enc: enc code of the rule
    :return: None
    """

    cur = _db.cursor()

    cur.execute(
        'INSERT OR REPLACE INTO circuit_pool (rule_id, circuit_id, F, D) '
        'VALUES (?, ?, ?, ?)',
        (rule_id, circuit_id, F, D)
    )

    if description is not None:
        cur.execute(
            'INSERT OR REPLACE INTO rule_description (rule_id, description) '
            'VALUES (?, ?)',
            (rule_id, description)
        )
    print_db()
    _db.commit()


def execute(rule_id, circuit_id, X):
    cur = _db.cursor()
    row = cur.execute('SELECT * FROM circuit_pool WHERE rule_id = ? AND circuit_id = ?', (rule_id, circuit_id)).fetchone()

    if row is None:
        raise ValueError(f'rule id {rule_id} with circuit id {circuit_id} does not exist.')

    F = row['F']
    D = row['D']

    row = cur.execute('SELECT description FROM rule_description WHERE rule_id = ?',
                      (rule_id, )).fetchone()

    if row is None:
        raise ValueError(f'description for rule id {rule_id} does not exist.')
    description = row['description']

    Y = _evaluate(F, X, description)


    return Y, D


def _evaluate(F: bytes, X: bytes, description: str):
    Path('/tmp/table.txt').write_bytes(F)
    Path('/tmp/input.txt').write_bytes(X)
    Path('/tmp/description.txt').write_text(description)

    subprocess.run([_emp_tap_binary, '/tmp/description.txt', '/tmp/table.txt', '/tmp/input.txt', '/tmp/output.txt'],
                   cwd='/tmp')

    Y = Path('/tmp/output.txt').read_bytes()

    return Y


def print_db():
    # table = pd.read_sql_query("SELECT * FROM circuit_pool", _db)
    # print(table)
    table = pd.read_sql_query("SELECT * FROM rule_description", _db)
    print(table)
