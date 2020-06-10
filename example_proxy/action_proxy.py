import os
from pathlib import Path
import sys
import time
import binascii
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
import dtaplib
import slack
from slack.errors import SlackApiError
from flask import Flask, request
from requests_toolbelt import MultipartDecoder


client_id = ''
client_secret = ''
channel_id = ''
oauth_scope = ''
oauth_token = ''

app = Flask(__name__)
client = slack.WebClient(token=oauth_token)




DELTA = 30


def exec_rule(secret: bytes, Y: bytes, ct: bytes, d_: bytes):
    P = Y[:16]
    Y = Y[16:]

    try:
        f = Fernet(base64.urlsafe_b64encode(secret + P))
        # d_ = f.encrypt(j + k + e_r + h + d)
        z = f.decrypt(d_)
    except InvalidToken:
        return -1, None, None

    j = int.from_bytes(z[:4], byteorder='big')
    k = z[4:36]
    e_r = z[36:52]
    h = z[52:68]
    d = z[68:]

    dtaplib.action_init(Y, d, len(d))

    y = [dtaplib.decode_bit() for _ in d]

    digest = hashlib.shake_128()
    for i in range(len(y)):
        L_yi = Y[i * 16:i * 16 + 16]
        if y[i]:
            digest.update(dtaplib.xor(L_yi, e_r))
        else:
            digest.update(L_yi)
    h2 = digest.digest(16)

    k = base64.urlsafe_b64encode(k)
    f = Fernet(k)

    payload = f.decrypt(ct)
    t = f.extract_timestamp(ct)

    if t > time.time() + DELTA or h2 != h:
        return -1, None, None

    y = [b'1' if yi else b'0' for yi in y]
    y = b''.join(y)

    return j, y, payload



def ascii2str(b):
    n = int(b'0b' + b, 2)
    return binascii.unhexlify('%x' % n)


circuit_id = 1
action_secret = b'r@\xeb6\xc2\x00\xe2\x95-\xe6W\xa4\xd6\xdf\xee\xa6'
rule_id = 1



@app.route("/begin_auth", methods=["GET"])
def pre_install():
    return f'<a href="https://slack.com/oauth/v2/authorize?scope={ oauth_scope }&client_id={ client_id }&redirect_uri=http://127.0.0.1:5000/finish_auth">Add to Slack</a>'


@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
    # Retrieve the auth code from the request params
    auth_code = request.args['code']

    # An empty string is a valid token for this request
    client = slack.WebClient(token="")

    # Request the auth tokens from Slack
    response = client.oauth_v2_access(
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )

    # Save the bot token to an environmental variable or to your data store
    # for later use
    os.environ["SLACK_BOT_TOKEN"] = response['access_token']
    print(response['access_token'])

    # Don't forget to let the user know that auth has succeeded!
    return "Auth complete!"



@app.route("/send_msg", methods=["POST"])
def send_msg():
    m = MultipartDecoder.from_response(request)

    Y = m.parts[1].content
    d = m.parts[2].content
    ct = m.parts[3].content

    j, y, payload = exec_rule(action_secret, Y,
                              ct, d)

    if j == -1:
        print('No action performed')
        return 'No action performed'

    msg = ascii2str(y).decode('ascii')

    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=msg
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        return e.response["error"]  # str like 'invalid_auth', 'channel_not_found'

    return str(response)
