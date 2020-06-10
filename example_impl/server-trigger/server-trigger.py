from flask import Flask, request
import logging
import os
import requests
import sys
from .helper import gen_trigger_data


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


from oblivtap import trigger
trigger.init('/home/ruizhe/example_rules')  # init, basically just add the emp binary path


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

    encoded_data, encoded_payload = trigger.encode(trigger_data, trigger_payload, user_id, trigger_id)

    params = {
        'trigger_id': trigger_id,
        'user_id': user_id,
        'X_len': len(encoded_data),     #
        'ct_len': len(encoded_payload)  # TODO: simplify/remove these two fields
    }

    requests.request("POST",
                     tap_address,
                     params=params,
                     data=encoded_data + encoded_payload,
                     headers={'Content-Type': 'application/octet-stream'},
                     verify=False
                     )
    return app.make_response('success')
