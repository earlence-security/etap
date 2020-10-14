import base64
import binascii
import hashlib
import time
import json
from typing import List, Any

import sqlite3
import pandas as pd
from cryptography.fernet import Fernet, InvalidToken

import emp_utils

_accept_window = 30
_db: sqlite3.Connection = None


def init(db_file=":memory:", init_db=True, accept_window=30):
    """
    :param db_file: location of the database
    :param init_db: create a new database or not
    """
    global _db, _accept_window

    _accept_window = accept_window

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
        'DROP TABLE IF EXISTS action_secret;'
    )
    cur.execute(
        'DROP TABLE IF EXISTS action_format;'
    )

    cur.execute(
        '''
        CREATE TABLE action_secret (
            action_id INTEGER PRIMARY KEY,
            secret_key BLOB NOT NULL
        );
        '''
    )

    cur.execute(
        '''
        CREATE TABLE action_format (
            action_id INTEGER PRIMARY KEY,
            formatter TEXT NOT NULL
        );
        '''
    )

    db.commit()


def add_new_secret(action_id, secret_key, formatter=None):
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

    old_key = cur.execute('SELECT secret_key FROM action_secret WHERE action_id = ?', (action_id,)).fetchone()

    if old_key is not None and old_key == secret_key:
        return

    cur.execute(
        'INSERT OR REPLACE INTO action_secret (action_id, secret_key) '
        'VALUES (?, ?)',
        (action_id, secret_key)
    )

    if formatter is not None:
        cur.execute(
            'INSERT OR REPLACE INTO action_format (action_id, formatter) '
            'VALUES (?, ?)',
            (action_id, formatter)
        )

    _db.commit()


def decode(action_id, blobs: List[bytes]):
    cur = _db.cursor()
    row = cur.execute('SELECT * FROM action_secret WHERE action_id = ?', (action_id,)).fetchone()

    if row is None:
        raise ValueError(f'action id {action_id} does not exist.')

    secret_key = row['secret_key']

    j = blobs[0]
    Y = blobs[1]
    ct = blobs[2]
    d_ = blobs[3]

    j, y, payload = _verify_decode(secret_key, Y, ct, d_)

    if j == -1:
        return None, None


    row = cur.execute('SELECT * FROM action_format WHERE action_id = ?', (action_id,)).fetchone()
    if row is not None:
        y = _decode_format(secret_key, Y, d_, row['formatter'])

    return y, payload


def _verify_decode(secret: bytes, Y: bytes, ct: bytes, d_: bytes):
    P = Y[:16]
    Y = Y[16:]

    try:
        f = Fernet(base64.urlsafe_b64encode(secret + P))
        # d_ = f.encrypt(j + k + e_r + h + d)
        z = f.decrypt(d_)
    except InvalidToken:
        return -1, None, None

    j = int.from_bytes(z[:4], byteorder='big')
    k = z[4:36]
    e_r = z[36:52]
    h = z[52:68]
    d = z[68:]

    emp_utils.init_decoder(Y, d, len(d))

    y = [emp_utils.decode_bit() for _ in d]

    digest = hashlib.shake_128()
    for i in range(len(y)):
        L_yi = Y[i * 16:i * 16 + 16]
        if y[i]:
            if L_yi == b'\xff'*16:
                digest.update(L_yi)
            else:
                digest.update(emp_utils.xor(L_yi, e_r))
        else:
            digest.update(L_yi)
    h2 = digest.digest(16)

    k = base64.urlsafe_b64encode(k)
    f = Fernet(k)

    payload = f.decrypt(ct)
    t = f.extract_timestamp(ct)

    if t > time.time() + _accept_window or h2 != h:
        return -1, None, None

    y = [b'1' if yi else b'0' for yi in y]

    return j, y, payload


def _decode_format(secret: bytes, Y: bytes, d_: bytes, formatter):
    formatter = json.loads(formatter)
    P = Y[:16]
    Y = Y[16:]

    f = Fernet(base64.urlsafe_b64encode(secret + P))
    # d_ = f.encrypt(j + k + e_r + h + d)
    z = f.decrypt(d_)

    d = z[68:]

    emp_utils.init_decoder(Y, d, len(d))

    y = []
    for f in formatter:
        if f['type'] == 'int':
            y.append(emp_utils.decode_int())
        elif f['type'] == 'bool':
            y.append(emp_utils.decode_bit())
        elif f['type'] == 'str':
            length = int(f['length'])
            y.append(emp_utils.decode_ascii_str(length).rstrip('\x00'))

    return y


def _ascii2str(b):
    y = [b'1' if yi else b'0' for yi in b]
    y = b''.join(y)
    n = int(b'0b' + y, 2)
    return binascii.unhexlify('%x' % n).rstrip(b'\x00')


def print_db():
    table = pd.read_sql_query("SELECT * FROM action_secret", _db)
    print(table)