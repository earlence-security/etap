import sqlite3
import subprocess
import requests

from functools import wraps

from werkzeug.security import gen_salt
from flask import request
from typing import List, Any
from cryptography.fernet import Fernet


class Trigger:
    _database = None
    _database_path = None
    _max_size = None
    _emp_lib = None

    def __init__(self, emp_lib, init_db=True, db_path=None, max_size=10):
        if db_path is None:
            self._database_path = gen_salt(6)
        else:
            self._database_path = db_path

        if emp_lib is None:
            raise ValueError('emp_lib is none.')

        self._max_size = max_size
        self._emp_lib = emp_lib

        if init_db:
            self._init_database(path=self._database_path)

        subprocess.run(['cp', '-r', self._emp_lib + '/dfa', '/tmp'])

    def _init_database(self, path=None):
        self._database = sqlite3.connect('trigger_' + path + '.db')
        db = self._database.cursor()
        db.row_factory = sqlite3.Row
        # with open('db_trigger.sql', mode='r') as sql:
        #     db.execute(sql.read())

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
            data_end INTEGER NOT NULL, \
            array TEXT NOT NULL)'
        )

        self._database.commit()

    def _add(self):
        if 'user_id' not in request.values:
            raise ValueError('user_id is none.')
        if 'trigger_id' not in request.values:
            raise ValueError('trigger_id is none.')
        if len(request.data) == 0:
            raise ValueError('enc is none.')
        if 'const1' not in request.values:
            raise ValueError('const1 is none.')
        if 'const2' not in request.values:
            raise ValueError('const2 is none.')

        user_id = request.values.get('user_id')
        trigger_id = request.values.get('trigger_id')
        enc = request.data
        const1 = request.values.get('const1')
        const2 = request.values.get('const2')

        query_id = user_id + ':' + trigger_id
        db = self._database.cursor()
        db.row_factory = sqlite3.Row

        id_data = db.execute(
            'SELECT * FROM trigger_info WHERE literal_id = ?',
            (query_id,)
        ).fetchone()

        if id_data is None:
            int1 = list(map(int, const1[1: -1].split(', ')))
            int2 = list(map(int, const2[1: -1].split(', ')))

            converted_array = ''
            for i in range(12):
                if i in int1:
                    converted_array += '1'
                    continue
                if i in int2:
                    converted_array += '2'
                    continue
                converted_array += '0'

            db.execute(
                'INSERT INTO trigger_info (literal_id, data_top, data_end, array) '
                'VALUES (?, ?, ?, ?)',
                (query_id, 2, 1, converted_array,)
            )

            db.execute(
                'INSERT INTO trigger_data (literal_id, data_enc, data_index) '
                'VALUES (?, ?, ?)',
                (query_id, enc, 1)
            )
            self._database.commit()
        else:
            # print(id_data)
            if int(id_data['data_top']) - int(id_data['data_end']) >= self._max_size:
                db.execute(
                    'DELETE FROM trigger_data WHERE literal_id = ? AND data_index = ?',
                    (query_id, id_data['data_end'])
                )
                db.execute(
                    'INSERT INTO trigger_data (literal_id, data_enc, data_index) '
                    'VALUES (?, ?, ?)',
                    (query_id, enc, id_data['data_top'])
                )

                # update data_index info
                db.execute(
                    'UPDATE trigger_info SET data_top = ?, data_end = ? '
                    'WHERE literal_id = ?',
                    (int(id_data['data_top']) + 1, int(id_data['data_end']) + 1, query_id)
                )

                self._database.commit()
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
                self._database.commit()

    def _enc(self, trigger_data, payload=None):
        if 'user_id' not in request.values:
            raise ValueError('user_id is none.')
        if 'trigger_id' not in request.values:
            raise ValueError('trigger_id is none.')
        if trigger_data is None:
            raise ValueError('trigger_data is none')
        if 'tap_address' not in request.values:
            raise ValueError('tap_address is none')

        user_id = request.values.get('user_id')
        trigger_id = request.values.get('trigger_id')
        tap_address = request.values.get('tap_address')

        query_id = user_id + ':' + trigger_id
        db = self._database.cursor()
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

        self._database.commit()
        X, ct = self._exec_rule(j=entry_data['id'],
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
                         headers={'Content-Type': 'application/octet-stream'}
                         )

    def _exec_rule(self, j: int, enc: bytes, x: List[Any], rule_id, payload=None):
        e_x = enc[:32]
        k = enc[32:]

        open('/tmp/enc.txt', 'wb').write(e_x)

        subprocess.run([self._emp_lib + '/bin/trigger', str(rule_id)] + x, cwd='/tmp')

        X = open('/tmp/input.txt', 'rb').read()

        f = Fernet(k)
        data = j.to_bytes(4, byteorder='big')
        if payload:
            data += payload

        return X, f.encrypt(data)

    def add_wrapper(self):
        def wrapper(func):
            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                self._add()
                return func(*args, **kwargs)

            return inner_wrapper

        return wrapper

    def enc_wrapper(self, trigger_data, payload=None):
        def wrapper(func):
            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                self._enc(trigger_data, payload)
                return func(*args, **kwargs)

            return inner_wrapper

        return wrapper
