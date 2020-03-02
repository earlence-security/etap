from flask import Flask, request
import logging
import sys


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

import oblivtap.action as action

action.init()


@app.route('/add', methods=['POST'])
def add():
    user_id = request.values.get('user_id')
    trigger_id = request.values.get('trigger_id')
    dec = request.data

    add_param = {
        'user_id': user_id,
        'trigger_id': trigger_id,
        'dec': dec
    }

    add_data(add_param)

    return {'data': 'ok',
            'src': 'server-action'}


@action.add_wrapper
def add_data(*args):
    pass


@app.route('/recall', methods=['POST'])
def recall():
    P_len = int(request.values.get('P_len'))
    Y_len = int(request.values.get('Y_len'))
    ct_len = int(request.values.get('ct_len'))
    request_data = request.data
    user_id = request.values.get('user_id')
    trigger_id = request.values.get('trigger_id')

    P = request_data[:P_len]
    Y = request_data[P_len:][:Y_len]
    ct = request_data[P_len:][Y_len:]

    enc_param = {
        'user_id': user_id,
        'trigger_id': trigger_id,
        'P': P,
        'Y': Y,
        'ct': ct
    }

    decode_data(enc_param)

    return {'data': 'ok',
            'src': 'server-action'}


@action.dec_wrapper
def decode_data(*args):
    pass
