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
emp_client_binary = '/tmp/tmp.MiQois5BcC/cmake-build-debug/bin/client'


def get_input_formatter(rule_description: str):
    formatter = []
    for line in rule_description.splitlines():
        tokens = line.split()
        if len(tokens) > 0 and tokens[0].startswith('x'):
            f = {'type': tokens[1]}
            if tokens[1] == 'str':
                f['length'] = int(tokens[2])
            formatter.append(f)
    return json.dumps(formatter)


def get_output_formatter(output_description: str):
    formatter = []
    for line in output_description.splitlines():
        tokens = line.split()
        if len(tokens) > 0 and tokens[0].startswith('y'):
            f = {'type': tokens[1]}
            if tokens[1] == 'str':
                f['length'] = int(tokens[2])
            formatter.append(f)
    return json.dumps(formatter)


def setup(circuit_id: int, trigger_secret: bytes, action_secret: bytes, capture_output_format=True):
    j = circuit_id.to_bytes(4, byteorder='big')

    e_s = hashlib.shake_128(trigger_secret + j + (0).to_bytes(1, byteorder='big')).digest(16)
    e_r = hashlib.shake_128(trigger_secret + j + (1).to_bytes(1, byteorder='big')).digest(16)
    k = hashlib.shake_256(trigger_secret + j + (2).to_bytes(1, byteorder='big')).digest(32)

    Path(f'/tmp/{rule_id}').mkdir(parents=True, exist_ok=True)
    Path(f'/tmp/{rule_id}/enc.txt').write_bytes(e_s + e_r)
    p = subprocess.run([emp_client_binary, sys.argv[1], f'/tmp/{rule_id}/enc.txt', f'/tmp/{rule_id}/table.txt',
                        f'/tmp/{rule_id}/dec.txt', '1' if capture_output_format else '0'], cwd=f'/tmp/{rule_id}',
                       capture_output=True)

    L = Path(f'/tmp/{rule_id}/dec.txt').read_bytes()
    F = Path(f'/tmp/{rule_id}/table.txt').read_bytes()

    L_0 = L[:16]
    L = L[16:]

    h = hashlib.shake_128(L).digest(16)
    d = L[15:len(L):16]
    d = bytes([di & 1 for di in d])

    if L_0 == b'\xff'*16:
        f = Fernet(base64.urlsafe_b64encode(action_secret + L_0))
    else:
        f = Fernet(base64.urlsafe_b64encode(action_secret + emp_utils.xor(L_0, e_r)))
    d_ = f.encrypt(j + k + e_r + h + d)

    if capture_output_format:
        return j, F, d_, get_output_formatter(p.stdout.decode())
    else:
        return j, F, d_


rule_description = Path(sys.argv[1]).read_text()
input_format = get_input_formatter(rule_description)

circuit_id = 0
trigger_secret = b'\xf3\x9d\x91\xc9\xccw\\\xd2\xd25F\x11/\xd2\x1eu'
action_secret = b'r@\xeb6\xc2\x00\xe2\x95-\xe6W\xa4\xd6\xdf\xee\xa6'


rule_id = 1

j, F, d_, output_format = setup(circuit_id, trigger_secret, action_secret, capture_output_format=True)


requests.post(
            url=f'{ts_address}/add',
            files={
                "id": rule_id,
                "secret_key": trigger_secret,
                "formatter": input_format
            }
        )

requests.post(
            url=f'{as_address}/add',
            files={
                "id": rule_id,
                "secret_key": action_secret,
                "formatter": output_format
            }
        )

requests.post(
            url=f'{tap_address}/add',
            files={
                "rule_id": rule_id,
                "circuit_id": circuit_id,
                "F": F,
                "d": d_,
                "description": rule_description
            }
        )

print(input_format)
print(output_format)


requests.post(
    url=f'{ts_address}/trigger',
    data=json.dumps({'test_mode': True, 'id': rule_id, 'data': ['this one has http', 42]})
)
