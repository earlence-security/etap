from flask import Flask, request
import logging
import os
import requests
from .helper import gen_trigger_data


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/trigger', methods=['POST'])
def enc():
    user_id = request.values.get('user_id')
    trigger_id = request.values.get('trigger_id')
    tap_address = request.values.get('tap_address')

    trigger_data = gen_trigger_data(trigger_id)  # generate the trigger data based on the rule id
    trigger_payload = os.urandom(1000)

    params = {
        'trigger_id': trigger_id,
        'user_id': user_id,
        'data': trigger_data,
    }

    requests.request("POST",
                     tap_address,
                     params=params,
                     data=trigger_payload,
                     headers={'Content-Type': 'application/octet-stream'},
                     verify=False
                     )
    return app.make_response('success')
