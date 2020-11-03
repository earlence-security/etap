import base64
import hashlib
import json
from typing import List, Any

import sqlite3
import pandas as pd
from cryptography.fernet import Fernet

import emp_utils


_db: sqlite3.Connection = None


def init(db_file=":memory:", init_db=True):
    """
    :param db_file: location of the database
    :param init_db: create a new database or not
    """
    global _db

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
        'DROP TABLE IF EXISTS trigger_secret;'
    )
    cur.execute(
        'DROP TABLE IF EXISTS trigger_format;'
    )

    cur.execute(
        '''
        CREATE TABLE trigger_secret (
            trigger_id INTEGER PRIMARY KEY,
            circuit_id INTEGER DEFAULT 0,
            secret_key BLOB NOT NULL
        );
        '''
    )

    cur.execute(
        '''
        CREATE TABLE trigger_format (
            trigger_id INTEGER PRIMARY KEY,
            formatter TEXT NOT NULL
        );
        '''
    )

    db.commit()


def add_new_secret(trigger_id, secret_key, formatter=None):
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

    old_key = cur.execute('SELECT secret_key FROM trigger_secret WHERE trigger_id = ?', (trigger_id,)).fetchone()

    if old_key is not None and old_key == secret_key:
        return

    cur.execute(
        'INSERT OR REPLACE INTO trigger_secret (trigger_id, secret_key) '
        'VALUES (?, ?)',
        (trigger_id, secret_key)
    )

    if formatter is not None:
        cur.execute(
            'INSERT OR REPLACE INTO trigger_format (trigger_id, formatter) '
            'VALUES (?, ?)',
            (trigger_id, formatter)
        )

    _db.commit()


def encode(trigger_id, data: List[Any], payload: bytes = None, test_mode=True):
    cur = _db.cursor()
    row = cur.execute('SELECT * FROM trigger_secret WHERE trigger_id = ?', (trigger_id,)).fetchone()

    if row is None:
        raise ValueError(f'trigger id {trigger_id} does not exist.')

    circuit_id = row['circuit_id']
    secret_key = row['secret_key']

    row = cur.execute('SELECT * FROM trigger_format WHERE trigger_id = ?', (trigger_id,)).fetchone()
    if row is not None:
        data = _format(data, row['formatter'])

    if test_mode:
        _, X, ct = _encode(0, secret_key, data, payload)
    else:
        _, X, ct = _encode(circuit_id, secret_key, data, payload)

    cur.execute('UPDATE trigger_secret SET circuit_id = circuit_id + 1 WHERE trigger_id = ?', (trigger_id,))
    _db.commit()

    return circuit_id, X, ct


def _format(x: List[Any], formatter: str):
    formatter = json.loads(formatter)

    if len(x) != len(formatter):
        raise ValueError('incorrect format of trigger data')

    x_ = []
    for x_i, f in zip(x, formatter):
        if f['type'] == 'int':
            x_.append(int(x_i))
        elif f['type'] == 'bool':
            x_.append(bool(x_i))
        elif f['type'] == 'str':
            length = int(f['length'])
            x_.append((str(x_i), length))
    return x_


def _encode(circuit_id: int, secret: bytes, x: List[Any], payload: bytes = None):
    j = circuit_id.to_bytes(4, byteorder='big')

    e_s = hashlib.shake_128(secret + j + (0).to_bytes(1, byteorder='big')).digest(16)
    e_r = hashlib.shake_128(secret + j + (1).to_bytes(1, byteorder='big')).digest(16)
    k = hashlib.shake_256(secret + j + (2).to_bytes(1, byteorder='big')).digest(32)

    emp_utils.init_encoder(e_s, e_r)

    X = []
    for x_i in x:
        if isinstance(x_i, bool):
            X.append(emp_utils.encode_bit(x_i))
        elif isinstance(x_i, int):
            X.append(emp_utils.encode_int(x_i))
        elif isinstance(x_i, str):
            X.append(emp_utils.encode_ascii_str(x_i))
        elif isinstance(x_i, tuple) and isinstance(x_i[0], str) and isinstance(x_i[1], int):
            X.append(emp_utils.encode_ascii_str(x_i[0], x_i[1]))
        else:
            raise TypeError('Unsupported data type:', type(x_i))
    X = b''.join(X)

    k = base64.urlsafe_b64encode(k)
    f = Fernet(k)

    payload = b'' if payload is None else payload
    ct = f.encrypt(payload)

    return j, X, ct


def print_db():
    table = pd.read_sql_query("SELECT * FROM trigger_secret", _db)
    print(table)
    table = pd.read_sql_query("SELECT * FROM trigger_format", _db)
    print(table)