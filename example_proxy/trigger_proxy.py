import os
import sys
import hashlib
import time
import base64
from pathlib import Path
from typing import List, Any
from cryptography.fernet import Fernet
import dtaplib
import twitter
from flask import Flask, request, make_response
from requests_toolbelt import MultipartEncoder


app = Flask(__name__)
client = twitter.Api(consumer_key='UfuujryE9L0NS2XMdQ1YeroBz',
                     consumer_secret='3nGi56yRr2z3AESH8YSbXeKIc0cxAm18ExTXdNtN4gBuVmVbVQ',
                     access_token_key='1255514428088487938-TG6Ar2EzWUVpsmWNujxMecCsPpvhO8',
                     access_token_secret='kXeRvREP0Bp1pCSsfeUphZVKH3M3DLpx5UyOmVAGAndgY')

last_tweet = None


circuit_id = 1
trigger_secret = b'\xf3\x9d\x91\xc9\xccw\\\xd2\xd25F\x11/\xd2\x1eu'


def exec_rule(circuit_id: int, secret: bytes, x: List[Any], payload=None):
    j = circuit_id.to_bytes(4, byteorder='big')

    e_s = hashlib.shake_128(secret + j + (0).to_bytes(1, byteorder='big')).digest(16)
    e_r = hashlib.shake_128(secret + j + (1).to_bytes(1, byteorder='big')).digest(16)
    k = hashlib.shake_256(secret + j + (2).to_bytes(1, byteorder='big')).digest(32)

    dtaplib.trigger_init(e_s, e_r)

    X = []
    for x_i in x:
        if isinstance(x_i, bool):
            X.append(dtaplib.encode_bit(x_i))
        elif isinstance(x_i, int):
            X.append(dtaplib.encode_int(x_i))
        elif isinstance(x_i, str):
            X.append(dtaplib.encode_ascii_str(x_i))
        elif isinstance(x_i, tuple) and isinstance(x_i[0], str) and isinstance(x_i[1], int):
            X.append(dtaplib.encode_ascii_str(x_i[0], x_i[1]))
        else:
            print('Unsupported data type:', x_i)
    X = b''.join(X)

    k = base64.urlsafe_b64encode(k)
    f = Fernet(k)

    payload = b'' if payload is None else payload
    ct = f.encrypt(payload)

    return j, X, ct



@app.route("/fetch_dummy", methods=["POST"])
def fetch_dummy():
    text = 'http://www.twitter.com'

    x = [(text, 140)]
    payload = None

    j, X, ct = exec_rule(circuit_id, trigger_secret, x, payload)

    response = make_response()
    response.set_data()

    Path('/tmp/X').write_bytes(X)
    Path('/tmp/ct').write_bytes(ct)

    m = MultipartEncoder({'circuit_id': j,
                          'X': ('X', X, 'application/octet-stream'),
                          'ct': ('ct', ct, 'application/octet-stream')})

    return m.to_string(), {'Content-Type': m.content_type}



@app.route("/fetch_tweet", methods=["POST"])
def fetch_tweet():
    global last_tweet
    tweets = client.GetUserTimeline(user_id='1255514428088487938', count=10)

    if tweets[0] == last_tweet:
        return make_response(), 200

    last_tweet = tweets[0]
    text = tweets[0].text

    x = [(text, 140)]
    payload = None

    j, X, ct = exec_rule(circuit_id, trigger_secret, x, payload)

    Path('/tmp/X').write_bytes(X)
    Path('/tmp/ct').write_bytes(ct)

    m = MultipartEncoder({'circuit_id': j,
                          'X': ('X', X, 'application/octet-stream'),
                          'ct': ('ct', ct, 'application/octet-stream')})

    return m.to_string(), {'Content-Type': m.content_type}


@app.route("/connect", methods=["POST"])
def connect():
    pass
