import sqlite3

from functools import wraps

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.fernet import Fernet


_database = None
_max_size = None


def init(init_db=True, max_size=10):
    global _max_size
    _max_size = max_size

    if init_db:
        _init_database()


def _init_database():
    global _database
    _database = sqlite3.connect(':memory')
    db = _database.cursor()
    db.row_factory = sqlite3.Row

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
                data_end INTEGER NOT NULL)')

    _database.commit()


def _add(param):
    if 'user_id' not in param:
        raise ValueError('user_id is none.')
    if 'trigger_id' not in param:
        raise ValueError('trigger_id is none.')
    if 'dec' not in param:
        raise ValueError('dec is none.')

    user_id = param['user_id']
    trigger_id = param['trigger_id']
    dec = param['dec']

    query_id = user_id + ':' + trigger_id
    db = _database.cursor()
    db.row_factory = sqlite3.Row

    id_data = db.execute(
        'SELECT * FROM action_info WHERE literal_id = ?',
        (query_id,)
    ).fetchone()

    if id_data is None:
        db.execute(
            'INSERT INTO action_info (literal_id, data_top, data_end) '
            'VALUES (?, ?, ?)',
            (query_id, 2, 1,)
        )

        db.execute(
            'INSERT INTO action_data (literal_id, data_dec, data_index) '
            'VALUES (?, ?, ?)',
            (query_id, dec, 1)
        )
        _database.commit()
    else:
        if int(id_data['data_top']) - int(id_data['data_end']) >= _max_size:
            db.execute(
                'DELETE FROM action_data WHERE literal_id = ? AND data_index = ?',
                (query_id, id_data['data_end'])
            )
            db.execute(
                'INSERT INTO action_data (literal_id, data_dec, data_index) '
                'VALUES (?, ?, ?)',
                (query_id, dec, id_data['data_top'])
            )

            db.execute(
                'UPDATE action_info SET data_top = ?, data_end = ? '
                'WHERE literal_id = ?',
                (int(id_data['data_top']) + 1, int(id_data['data_end']) + 1, query_id)
            )

            _database.commit()
        else:
            db.execute(
                'INSERT INTO action_data (literal_id, data_dec, data_index) '
                'VALUES (?, ?, ?)',
                (query_id, dec, id_data['data_top'])
            )

            db.execute(
                'UPDATE action_info SET data_top = ? '
                'WHERE literal_id = ?',
                (int(id_data['data_top']) + 1, query_id)
            )
            _database.commit()


def _dec(param):
    if 'user_id' not in param:
        raise ValueError('user_id is none.')
    if 'trigger_id' not in param:
        raise ValueError('trigger_id is none.')
    if 'P' not in param:
        raise ValueError('P is none.')
    if 'Y' not in param:
        raise ValueError('Y is none.')
    if 'ct' not in param:
        raise ValueError('ct is none.')

    user_id = param['user_id']
    trigger_id = param['trigger_id']

    P = param['P']
    Y = param['Y']
    ct = param['ct']

    query_id = user_id + ':' + trigger_id
    db = _database.cursor()
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

    _database.commit()
    return _exec_rule(P, Y, ct, entry_data['data_dec'])


def _exec_rule(P: bytes, Y: bytes, ct: bytes, dec: bytes):
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


def add_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _add(args[0])
        return func(*args, **kwargs)
    return wrapper


def dec_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        _dec(args[0])
        return func(*args, **kwargs)
    return wrapper
