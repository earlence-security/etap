import sqlite3
import subprocess
import requests
from flask import Flask, request

from functools import wraps

from typing import List, Any
from cryptography.fernet import Fernet


_database = None
_max_size = None
_emp_lib = None


def init(emp_lib, init_db=True, max_size=10):
    if emp_lib is None:
        raise ValueError('emp_lib is none.')

    global _max_size, _emp_lib
    _max_size = max_size
    _emp_lib = emp_lib

    if init_db:
        _init_database()

    subprocess.run(['cp', '-r', _emp_lib + '/dfa', '/tmp'])


def _init_database():
    global _database
    _database = sqlite3.connect(':memory')
    db = _database.cursor()
    db.row_factory = sqlite3.Row

    db.execute(
        'DROP TABLE IF EXISTS trigger_info'
    )
    db.execute(
        'DROP TABLE IF EXISTS trigger_data'
    )
    db.execute(
        'CREATE TABLE trigger_data (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        literal_id TEXT NOT NULL,\
        data_enc BLOB NOT NULL,\
        data_index INTEGER NOT NULL,\
        FOREIGN KEY (literal_id) REFERENCES trigger_info (literal_id))'
    )
    db.execute(
        'CREATE TABLE trigger_info (\
        id INTEGER PRIMARY KEY AUTOINCREMENT, \
        literal_id TEXT UNIQUE NOT NULL, \
        data_top INTEGER NOT NULL, \
        data_end INTEGER NOT NULL)'
    )

    _database.commit()


def _add(param):
    if 'user_id' not in param:
        raise ValueError('user_id is none.')
    if 'trigger_id' not in param:
        raise ValueError('trigger_id is none.')
    if 'enc' not in param:
        raise ValueError('enc is none.')

    user_id = param['user_id']
    trigger_id = param['trigger_id']
    enc = param['enc']

    query_id = user_id + ':' + trigger_id
    db = _database.cursor()
    db.row_factory = sqlite3.Row

    id_data = db.execute(
        'SELECT * FROM trigger_info WHERE literal_id = ?',
        (query_id,)
    ).fetchone()

    if id_data is None:

        db.execute(
            'INSERT INTO trigger_info (literal_id, data_top, data_end) '
            'VALUES (?, ?, ?)',
            (query_id, 2, 1,)
        )

        db.execute(
            'INSERT INTO trigger_data (literal_id, data_enc, data_index) '
            'VALUES (?, ?, ?)',
            (query_id, enc, 1)
        )
        _database.commit()
    else:
        if int(id_data['data_top']) - int(id_data['data_end']) >= _max_size:
            db.execute(
                'DELETE FROM trigger_data WHERE literal_id = ? AND data_index = ?',
                (query_id, id_data['data_end'])
            )
            db.execute(
                'INSERT INTO trigger_data (literal_id, data_enc, data_index) '
                'VALUES (?, ?, ?)',
                (query_id, enc, id_data['data_top'])
            )

            db.execute(
                'UPDATE trigger_info SET data_top = ?, data_end = ? '
                'WHERE literal_id = ?',
                (int(id_data['data_top']) + 1, int(id_data['data_end']) + 1, query_id)
            )

            _database.commit()
        else:
            db.execute(
                'INSERT INTO trigger_data (literal_id, data_enc, data_index) '
                'VALUES (?, ?, ?)',
                (query_id, enc, id_data['data_top'])
            )
            db.execute(
                'UPDATE trigger_info SET data_top = ? '
                'WHERE literal_id = ?',
                (int(id_data['data_top']) + 1, query_id)
            )
            _database.commit()


def _enc(param):
    if 'user_id' not in param:
        raise ValueError('user_id is none.')
    if 'trigger_id' not in param:
        raise ValueError('trigger_id is none.')
    if 'trigger_data' not in param:
        raise ValueError('trigger_data is none')
    if 'tap_address' not in param:
        raise ValueError('tap_address is none')

    user_id = param['user_id']
    trigger_id = param['trigger_id']
    tap_address = param['tap_address']
    trigger_data = param['trigger_data']

    payload = None
    if 'payload' in param:
        payload = param['payload']

    query_id = user_id + ':' + trigger_id
    db = _database.cursor()
    db.row_factory = sqlite3.Row

    entry_info = db.execute(
        'SELECT * FROM trigger_info WHERE literal_id = ?',
        (query_id,)
    ).fetchone()

    if not entry_info:
        raise ValueError('Invalid user_id or trigger_id')

    entry_data = db.execute(
        'SELECT * FROM trigger_data WHERE literal_id = ? AND data_index = ?',
        (query_id, entry_info['data_end'])
    ).fetchone()

    if not entry_data:
        raise ValueError('Expired enc.')

    db.execute(
        'DELETE FROM trigger_data WHERE literal_id = ? AND data_index = ?',
        (query_id, entry_info['data_end'])
    )

    db.execute(
        'UPDATE trigger_info SET data_end = ? '
        'WHERE literal_id = ?',
        (int(entry_info['data_end']) + 1, query_id)
    )

    _database.commit()
    X, ct = _exec_rule(j=entry_data['id'],
                            enc=entry_data['data_enc'],
                            x=[trigger_data],
                            rule_id=trigger_id,
                            payload=payload)

    query_action = {
        'trigger_id': trigger_id,
        'user_id': user_id,
        'X_len': len(X),
        'ct_len': len(ct)
    }

    requests.request("POST",
                     tap_address,
                     params=query_action,
                     data=X + ct,
                     headers={'Content-Type': 'application/octet-stream'},
                     verify=False
                     )


def _exec_rule(j: int, enc: bytes, x: List[Any], rule_id, payload=None):
    e_x = enc[:32]
    k = enc[32:]

    open('/tmp/enc.txt', 'wb').write(e_x)

    subprocess.run([_emp_lib + '/bin/trigger', str(rule_id)] + x, cwd='/tmp')

    X = open('/tmp/input.txt', 'rb').read()

    f = Fernet(k)
    data = j.to_bytes(4, byteorder='big')
    if payload:
        data += payload

    return X, f.encrypt(data)


def add_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.values.get('user_id')
        trigger_id = request.values.get('trigger_id')
        enc = request.data

        add_param = {
            'user_id': user_id,
            'trigger_id': trigger_id,
            'enc': enc
        }
        _add(args[0])
        return func(*args, **kwargs)
    return wrapper


def enc_data(x, payload, user_id, trigger_id):
    query_id = user_id + ':' + trigger_id
    db = _database.cursor()
    db.row_factory = sqlite3.Row

    entry_info = db.execute(
        'SELECT * FROM trigger_info WHERE literal_id = ?',
        (query_id,)
    ).fetchone()

    if not entry_info:
        raise ValueError('Invalid user_id or trigger_id')

    entry_data = db.execute(
        'SELECT * FROM trigger_data WHERE literal_id = ? AND data_index = ?',
        (query_id, entry_info['data_end'])
    ).fetchone()

    if not entry_data:
        raise ValueError('Expired enc.')

    db.execute(
        'DELETE FROM trigger_data WHERE literal_id = ? AND data_index = ?',
        (query_id, entry_info['data_end'])
    )

    db.execute(
        'UPDATE trigger_info SET data_end = ? '
        'WHERE literal_id = ?',
        (int(entry_info['data_end']) + 1, query_id)
    )

    _database.commit()
    X, ct = _exec_rule(j=entry_data['id'],
                       enc=entry_data['data_enc'],
                       x=[x],
                       rule_id=trigger_id,
                       payload=payload)
    return X, ct


