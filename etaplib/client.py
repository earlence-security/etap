import base64
import subprocess
import hashlib
from pathlib import Path
import sys
import json

from cryptography.fernet import Fernet
import requests

import emp_utils


ts_address = 'http://127.0.0.1:5000'
as_address = 'http://127.0.0.1:5002'
tap_address = 'http://127.0.0.1:5001'
emp_client_binary = '/home/ychen459/dtap-confidentiality/emp_src/bin/client'
dfa_directory = '/home/ychen459/dtap-confidentiality/emp_src/dfa'


def setup(rule_id: int, circuit_id: int, trigger_secret: bytes, action_secret: bytes):
    j = circuit_id.to_bytes(4, byteorder='big')

    e_s = hashlib.shake_128(trigger_secret + j + (0).to_bytes(1, byteorder='big')).digest(16)
    e_r = hashlib.shake_128(trigger_secret + j + (1).to_bytes(1, byteorder='big')).digest(16)
    k = hashlib.shake_256(trigger_secret + j + (2).to_bytes(1, byteorder='big')).digest(32)

    Path('/tmp/enc.txt').write_bytes(e_s + e_r)
    subprocess.run([emp_client_binary, str(rule_id), '/tmp/enc.txt', '/tmp/table.txt', '/tmp/dec.txt',
                    dfa_directory], cwd='/tmp')

    L = Path('/tmp/dec.txt').read_bytes()
    F = Path('/tmp/table.txt').read_bytes()


    L_0 = L[:16]
    L = L[16:]

    h = hashlib.shake_128(L).digest(16)
    d = L[15:len(L):16]
    d = bytes([di & 1 for di in d])


    f = Fernet(base64.urlsafe_b64encode(action_secret + emp_utils.xor(L_0, e_r)))
    d_ = f.encrypt(j + k + e_r + h + d)

    return j, F, d_



circuit_id = 0
trigger_secret = b'\xf3\x9d\x91\xc9\xccw\\\xd2\xd25F\x11/\xd2\x1eu'
action_secret = b'r@\xeb6\xc2\x00\xe2\x95-\xe6W\xa4\xd6\xdf\xee\xa6'


rule_id = 1

j, F, d_ = setup(rule_id, circuit_id, trigger_secret, action_secret)


requests.post(
            url=f'{ts_address}/add',
            files={
                "id": rule_id,
                "secret_key": trigger_secret,
                "formatter": json.dumps([{'type': 'str', 'length': 140}])
            }
        )

requests.post(
            url=f'{as_address}/add',
            files={
                "id": rule_id,
                "secret_key": action_secret,
                "formatter": json.dumps([{'type': 'str', 'length': 140}])
            }
        )

requests.post(
            url=f'{tap_address}/add',
            files={
                "rule_id": rule_id,
                "circuit_id": circuit_id,
                "F": F,
                "d": d_
            }
        )


requests.post(
    url=f'{ts_address}/trigger',
    data=json.dumps({'id': rule_id, 'data': ['this one has http']})
)