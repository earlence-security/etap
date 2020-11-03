import base64
import subprocess
import hashlib
from pathlib import Path
import time
import json
import random
import string
import multiprocessing
import asyncio

from cryptography.fernet import Fernet
import requests
import aiohttp

import emp_utils


ts_address = 'http://127.0.0.1:5000'
as_address = 'http://127.0.0.1:5002'
tap_address = 'http://127.0.0.1:5001'
emp_client_binary = '/tmp/tmp.MiQois5BcC/cmake-build-debug/bin/client'
rule_dir = '/home/ychen459/original_rules'


from logger import e_logger, s_logger


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


def setup(rule_id: int, circuit_id: int, trigger_secret: bytes, action_secret: bytes, capture_output_format=True):
    j = circuit_id.to_bytes(4, byteorder='big')

    e_s = hashlib.shake_128(trigger_secret + j + (0).to_bytes(1, byteorder='big')).digest(16)
    e_r = hashlib.shake_128(trigger_secret + j + (1).to_bytes(1, byteorder='big')).digest(16)
    k = hashlib.shake_256(trigger_secret + j + (2).to_bytes(1, byteorder='big')).digest(32)

    Path(f'/tmp/{rule_id}').mkdir(parents=True, exist_ok=True)
    Path(f'/tmp/{rule_id}/enc.txt').write_bytes(e_s + e_r)
    p = subprocess.run([emp_client_binary, f'{rule_dir}/{rule_id}.txt', f'/tmp/{rule_id}/enc.txt',
                        f'/tmp/{rule_id}/table.txt', f'/tmp/{rule_id}/dec.txt', '1' if capture_output_format else '0'],
                       cwd=f'/tmp/{rule_id}', capture_output=True)

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


def register_rule(rule_id, rule_description):
    input_format = get_input_formatter(rule_description)

    circuit_id = 0
    trigger_secret = b'\xf3\x9d\x91\xc9\xccw\\\xd2\xd25F\x11/\xd2\x1eu'
    action_secret = b'r@\xeb6\xc2\x00\xe2\x95-\xe6W\xa4\xd6\xdf\xee\xa6'

    start = time.time()
    j, F, d_, output_format = setup(rule_id, circuit_id, trigger_secret, action_secret, capture_output_format=True)
    e_logger.info(f'generate gc: {time.time() - start}')
    s_logger.info(f'gc size (bytes): {len(F) + len(d_)}')

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

    start = time.time()
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
    e_logger.info(f'upload gc: {time.time() - start}')


def gen_dummy_data(input_format):
    data = []
    for f in input_format:
        if f['type'] == 'int':
            data.append(random.randint(1, 100))
        elif f['type'] == 'bool':
            data.append(True)
        elif f['type'] == 'str':
            letters = string.ascii_letters
            dummy_str = ''.join(random.choice(letters) for _ in range(min(20, f['length'])))
            data.append(dummy_str)
    return data


def trigger_rule(rule_id, data, execute_mode='gc'):
    start = time.time()
    if execute_mode == 'gc':
        requests.post(
            url=f'{ts_address}/trigger',
            data=json.dumps({'test_mode': True, 'id': rule_id, 'data': data})
        )
    elif execute_mode == 'plain':
        requests.post(
            url=f'{ts_address}/trigger/plain',
            data=json.dumps({'test_mode': True, 'id': rule_id, 'data': data})
        )
    e_logger.info(f'R#{rule_id} latency: {time.time() - start}')


data = {}
for rule_id in range(1, 11):
    rule_fname = f'{rule_dir}/{rule_id}.txt'
    print(rule_fname)
    rule_description = Path(rule_fname).read_text()
    register_rule(rule_id, rule_description)
    data[rule_id] = gen_dummy_data(json.loads(get_input_formatter(rule_description)))



# n_trigger_per_rule = 1
#
#
# for _ in range(n_trigger_per_rule):
#     with multiprocessing.Pool(processes=4) as pool:
#         pool.starmap(trigger_rule, [(rule_id, data[rule_id], 'gc') for rule_id in range(1, 11)])



async def trigger_rule_async(session: aiohttp.ClientSession, rule_id, data, execute_mode='gc'):
    start = time.time()
    if execute_mode == 'gc':
        await session.post(
            url=f'{ts_address}/trigger',
            data=json.dumps({'test_mode': True, 'id': rule_id, 'data': data})
        )
    elif execute_mode == 'plain':
        await session.post(
            url=f'{ts_address}/trigger/plain',
            data=json.dumps({'test_mode': True, 'id': rule_id, 'data': data})
        )
    e_logger.info(f'#{rule_id} latency ({execute_mode}): {time.time() - start}')


async def bench_async(n_round=1, execute_mode='gc'):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*(trigger_rule_async(session, rule_id, data[rule_id], execute_mode) for rule_id in list(range(1, 11))*n_round))

start = time.time()
asyncio.run(bench_async(10, 'gc'))
e_logger.info(f'TOTAL latency: {time.time() - start}')

