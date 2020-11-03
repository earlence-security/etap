import json

from flask import Flask, request
import logging
import requests
from cryptography.fernet import Fernet

import sys
sys.path.insert(0, '/home/ychen459/etaplib')
as_address = 'http://127.0.0.1:5002'

import etap

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


etap.init('/tmp/tmp.MiQois5BcC/cmake-build-debug/bin/tap')


# Additional API to receive circuit encoding info from client
@app.route('/add', methods=['POST'])
def add():
    rule_id = int(request.files.get('rule_id').read())
    circuit_id = int(request.files.get('circuit_id').read())
    F = request.files.get('F').read()
    d = request.files.get('d').read()

    if (desc_file := request.files.get('description')) is not None:
        description = desc_file.read().decode()
    else:
        description = None

    etap.add_new_circuit(rule_id, circuit_id, F, d, description)

    return 'success'



@app.route('/run', methods=['POST'])
def run():
    rule_id = int(request.files.get('trigger_id').read())
    circuit_id = int(request.files.get('circuit_id').read())
    X = request.files.get('X').read()
    ct = request.files.get('ct').read()

    Y, d = etap.execute(rule_id, circuit_id, X)

    #  send trigger data to tap
    requests.request("POST",
                     f'{as_address}/action',
                     files={
                         "action_id": rule_id,
                         "j": circuit_id.to_bytes(4, byteorder='big'),
                         "Y": Y,
                         "d": d,
                         "ct": ct
                     })

    return app.make_response('success')


key = b'0FJ1Cx4TAA_TmAgWoKxx62aHLtzqr56KHvLiA71Kgpk='
f = Fernet(key)

@app.route('/run/plain', methods=['POST'])
def run_plain():
    rule_id = int(request.files.get('trigger_id').read())
    blob = request.files.get('blob').read()

    data = f.decrypt(blob)
    data = json.loads(data.decode())

    cur = etap._db.cursor()
    row = cur.execute('SELECT * FROM rule_description WHERE rule_id = ?', (rule_id,)).fetchone()

    if row is None:
        raise ValueError(f'rule id {rule_id} does not exist.')

    data = json.dumps(data).encode()
    blob = f.encrypt(data)

    #  send trigger data to tap
    requests.request("POST",
                     f'{as_address}/action/plain',
                     files={
                         "action_id": rule_id,
                         "blob": blob
                     })

    return app.make_response('success')