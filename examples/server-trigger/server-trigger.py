from flask import Flask, request
import logging
import sys
from .helper import gen_trigger_data


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

sys.path.insert(0, "/home/ruizhe/oblivtap/")  # not installed in the sys path, need to add manually
import trigger

trigger.init('/home/ruizhe/example_rules')  # init, basically just add the emp path


@app.route('/add', methods=['POST'])
def add():
    user_id = request.values.get('user_id')
    trigger_id = request.values.get('trigger_id')
    enc = request.data

    add_param = {
        'user_id': user_id,
        'trigger_id': trigger_id,
        'enc': enc
    }

    add_data(add_param)
    return {'data': 'ok',
            'src': 'server-trigger'}


@trigger.add_wrapper
def add_data(*args):
    pass


@app.route('/recall', methods=['POST'])
def enc():
    user_id = request.values.get('user_id')
    trigger_id = request.values.get('trigger_id')
    tap_address = request.values.get('tap_address')
    trigger_data = gen_trigger_data(trigger_id)  # generate the trigger data based on the rule id

    enc_param = {
        'user_id': user_id,
        'trigger_id': trigger_id,
        'tap_address': tap_address,
        'trigger_data': trigger_data
    }

    enc_data(enc_param)
    return {
        'data': 'ok',
        'src': 'server-trigger'
    }


@trigger.enc_wrapper
def enc_data(*args):
    pass
