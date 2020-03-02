from flask import Flask, request
import logging
import os
import requests
from .helper import gen_trigger_data


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


import oblivtap.trigger as trigger
trigger.init('/home/ruizhe/example_rules')  # init, basically just add the emp path


# Additional API to receive circuit encoding info from client
@app.route('/add', methods=['POST'])
@trigger.add_wrapper
def add():
    return app.make_response('success')


@app.route('/trigger', methods=['POST'])
def enc():
    user_id = request.values.get('user_id')
    trigger_id = request.values.get('trigger_id')
    tap_address = request.values.get('tap_address')

    trigger_data = gen_trigger_data(trigger_id)  # generate the trigger data based on the rule id
    trigger_payload = os.urandom(1000)

    X, ct = trigger.enc_data(trigger_data, trigger_payload, user_id, trigger_id)

    params = {
        'trigger_id': trigger_id,
        'user_id': user_id,
        'X_len': len(X),
        'ct_len': len(ct)
    }

    requests.request("POST",
                     tap_address,
                     params=params,
                     data=X + ct,
                     headers={'Content-Type': 'application/octet-stream'},
                     verify=False
                     )
    return {
        'data': 'ok',
        'src': 'server-trigger'
    }
