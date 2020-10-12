import json

from flask import Flask, request
import logging
import requests

import sys
sys.path.insert(0, '/home/ychen459/etaplib')
as_address = 'http://127.0.0.1:5002'

import etap

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


etap.init('/home/ychen459/dtap-confidentiality/emp_src/bin/tap', '/home/ychen459/dtap-confidentiality/emp_src/dfa')


# Additional API to receive circuit encoding info from client
@app.route('/add', methods=['POST'])
def add():
    rule_id = int(request.files.get('rule_id').read())
    circuit_id = int(request.files.get('circuit_id').read())
    F = request.files.get('F').read()
    d = request.files.get('d').read()

    etap.add_new_circuit(rule_id, circuit_id, F, d)

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
