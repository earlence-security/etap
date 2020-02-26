import sqlite3

from werkzeug.security import gen_salt
from flask import request

from functools import wraps

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.fernet import Fernet


class Action:
    _database = None
    _database_path = None
    _max_size = None

    def __init__(self, init_db=True, db_path=None, max_size=10):
        if db_path is None:
            self._database_path = gen_salt(6)
        else:
            self._database_path = db_path

        self._max_size = max_size

        if init_db:
            self._init_database(path=self._database_path)

    def _init_database(self, path=None):
        self._database = sqlite3.connect('action_' + path + '.db')
        db = self._database.cursor()
        db.row_factory = sqlite3.Row
        # with open('db_action.sql', mode='r') as sql:
        #     db.execute(sql.read())
        db.execute('DROP TABLE IF EXISTS action_info')
        db.execute('DROP TABLE IF EXISTS action_data')
        db.execute(
                   'CREATE TABLE action_data (\
                    id INTEGER PRIMARY KEY AUTOINCREMENT,\
                    literal_id TEXT NOT NULL,\
                    data_dec BLOB NOT NULL,\
                    data_index INTEGER NOT NULL,\
                    FOREIGN KEY (literal_id) REFERENCES action_info (literal_id))')
        db.execute('CREATE TABLE action_info (\
                    id INTEGER PRIMARY KEY AUTOINCREMENT,\
                    literal_id TEXT UNIQUE NOT NULL,\
                    data_top INTEGER NOT NULL,\
                    data_end INTEGER NOT NULL,\
                    array TEXT NOT NULL)')

        self._database.commit()

    def _add(self):
        if 'user_id' not in request.values:
            raise ValueError('user_id is none.')
        if 'trigger_id' not in request.values:
            raise ValueError('trigger_id is none.')
        if len(request.data) == 0:
            raise ValueError('dec is none.')
        if 'const1' not in request.values:
            raise ValueError('const1 is none.')
        if 'const2' not in request.values:
            raise ValueError('const2 is none.')

        user_id = request.values.get('user_id')
        trigger_id = request.values.get('trigger_id')
        dec = request.data
        const1 = request.values.get('const1')
        const2 = request.values.get('const2')

        query_id = user_id + ':' + trigger_id
        db = self._database.cursor()
        db.row_factory = sqlite3.Row

        id_data = db.execute(
            'SELECT * FROM action_info WHERE literal_id = ?',
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
                'INSERT INTO action_info (literal_id, data_top, data_end, array) '
                'VALUES (?, ?, ?, ?)',
                (query_id, 2, 1, converted_array,)
            )

            db.execute(
                'INSERT INTO action_data (literal_id, data_dec, data_index) '
                'VALUES (?, ?, ?)',
                (query_id, dec, 1)
            )
            self._database.commit()
        else:
            # id_data = id_data[0]
            if int(id_data['data_top']) - int(id_data['data_end']) >= self._max_size:
                db.execute(
                    'DELETE FROM action_data WHERE literal_id = ? AND data_index = ?',
                    (query_id, id_data['data_end'])
                )
                db.execute(
                    'INSERT INTO action_data (literal_id, data_dec, data_index) '
                    'VALUES (?, ?, ?)',
                    (query_id, dec, id_data['data_top'])
                )

                # update data_index info
                db.execute(
                    'UPDATE action_info SET data_top = ?, data_end = ? '
                    'WHERE literal_id = ?',
                    (int(id_data['data_top']) + 1, int(id_data['data_end']) + 1, query_id)
                )

                self._database.commit()
            else:
                db.execute(
                    'INSERT INTO action_data (literal_id, data_dec, data_index) '
                    'VALUES (?, ?, ?)',
                    (query_id, dec, id_data['data_top'])
                )
                #  since insert, update size
                db.execute(
                    'UPDATE action_info SET data_top = ? '
                    'WHERE literal_id = ?',
                    (int(id_data['data_top']) + 1, query_id)
                )
                self._database.commit()

    def _dec(self):
        if 'user_id' not in request.values:
            raise ValueError('user_id is none.')
        if 'trigger_id' not in request.values:
            raise ValueError('trigger_id is none.')
        if 'P_len' not in request.values:
            raise ValueError('P_len is none.')
        if 'Y_len' not in request.values:
            raise ValueError('Y_len is none.')
        if 'ct_len' not in request.values:
            raise ValueError('ct_len is none.')

        P_len = int(request.values.get('P_len'))
        Y_len = int(request.values.get('Y_len'))
        ct_len = int(request.values.get('ct_len'))
        request_data = request.data
        user_id = request.values.get('user_id')
        trigger_id = request.values.get('trigger_id')

        P = request_data[:P_len]
        Y = request_data[P_len:][:Y_len]
        ct = request_data[P_len:][Y_len:]

        query_id = user_id + ':' + trigger_id
        db = self._database.cursor()
        db.row_factory = sqlite3.Row

        entry_info = db.execute(
            'SELECT * FROM action_info WHERE literal_id = ?',
            (query_id,)
        ).fetchone()

        if not entry_info:
            raise ValueError('Invalid user_id or trigger_id')

        entry_data = db.execute(
            'SELECT * FROM action_data WHERE literal_id = ? AND data_index = ?',
            (query_id, entry_info['data_end'])
        ).fetchone()

        if not entry_data:
            raise ValueError('Expired dec.')

        db.execute(
            'DELETE FROM action_data WHERE literal_id = ? AND data_index = ?',
            (query_id, entry_info['data_end'])
        )

        db.execute(
            'UPDATE action_info SET data_end = ? '
            'WHERE literal_id = ?',
            (int(entry_info['data_end']) + 1, query_id)
        )

        self._database.commit()
        return self._exec_rule(P, Y, ct, entry_data['data_dec'])

    def _exec_rule(self, P: bytes, Y: bytes, ct: bytes, dec: bytes):
        d1 = dec[:16]
        d2_ = dec[16:]

        if d1 != P:
            aesccm = AESCCM(P)
            nonce = b'0' * 13

            data = aesccm.decrypt(nonce, d2_, None)

            k = data[:44]
            d2 = data[44:]

            y = ''

            for i in range(0, len(Y), 16):
                digest = hashes.Hash(hashes.SHAKE128(16), backend=default_backend())
                digest.update(Y[i:i + 16])
                Yi = digest.finalize()
                if Yi == d2[2 * i:2 * i + 16]:
                    y += '0'
                elif Yi == d2[2 * i + 16:2 * i + 32]:
                    y += '1'
                else:
                    raise ValueError('Invalid Y.')

            f = Fernet(k)
            data = f.decrypt(ct)

            j = int.from_bytes(data[:4], byteorder='big')
            payload = data[4:]

            return j, y, payload

        else:
            return -1, b'', b''

    def add_wrapper(self):
        def wrapper(func):
            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                self._add()
                return func(*args, **kwargs)
            return inner_wrapper
        return wrapper

    def dec_wrapper(self):
        def wrapper(func):
            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                self._dec()
                return func(*args, **kwargs)
            return inner_wrapper
        return wrapper
