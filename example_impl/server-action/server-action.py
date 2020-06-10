from flask import Flask, request
import logging


app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

import oblivtap.action as action
action.init()


@app.route('/add', methods=['POST'])
def add():
    return app.make_response('success')


@app.route('/action', methods=['POST'])
def recall():
    request_data = request.data
    user_id = request.values.get('user_id')
    action_id = request.values.get('trigger_id')


    # TODO: move this step into library
    P_len = int(request.values.get('P_len'))
    Y_len = int(request.values.get('Y_len'))
    P = request_data[:P_len]
    Y = request_data[P_len:][:Y_len]
    ct = request_data[P_len:][Y_len:]

    p, action_data, payload = action.decode(P, Y, ct, user_id, action_id)

    if p:
        print(action_data, payload)

    return app.make_response('success')

