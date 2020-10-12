import os
import json

from flask import Flask, request
import logging
import requests

import sys

sys.path.insert(0, '/home/ychen459/etaplib')
tap_address = ''

import action

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

action.init()


# Additional API to receive circuit encoding info from client
@app.route('/add', methods=['POST'])
def add():
    action_id = int(request.files.get('id').read())
    secret_key = request.files.get('secret_key').read()

    formatter = request.files.get('formatter').read().decode()

    action.add_new_secret(action_id, secret_key, formatter)

    return 'success'


@app.route('/action', methods=['POST'])
def action_func():

    action_id = int(request.files.get('action_id').read())

    j = request.files.get('j').read()
    Y = request.files.get('Y').read()
    ct = request.files.get('ct').read()
    d = request.files.get('d').read()

    y, payload = action.decode(action_id, [j, Y, ct, d])

    print(y)

    return app.make_response('success')
