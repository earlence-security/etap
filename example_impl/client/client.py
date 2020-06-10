import requests
import os
import random
import base64
import subprocess
from client_helper import *


token_action = '1234'
token_trigger = '5678'

base_trigger = 'https://127.0.0.1:5000'
base_action = 'https://127.0.0.1:9000'
base_platform = 'https://127.0.0.1:7000'


def gen_binary():
    return os.urandom(16)


def gen_c():
    MAX_C = 12
    array_i = []
    array_j = []
    while len(array_i) == 0 or len(array_j) == 0:
        array_j = []
        array_i = []
        for i in range(MAX_C):
            rand_val = random.random()
            if rand_val < 0.3:
                array_i.append(i)
            elif rand_val < 0.6:
                array_j.append(i)

    return str(array_i), str(array_j)


def trigger_action(user, id):
    query = {"trigger_id": id,
             "tap_address": base_platform + '/recall',
             "user_id": user}

    r_data = requests.request("POST",
                              base_trigger + "/recall",
                              params=query,
                              verify=False)
    print(r_data.text)


def add_combine_f(user, id):
    # process = subprocess.run("~/example_rules/bin/client " + str(id), shell=True)
    e, d, F = setup(id)

    # trigger
    data = e
    gen_val = gen_c()
    query = {"trigger_id": id,
             "user_id": user,
             "data_enc": base64.b64encode(data),
             "const1": gen_val[0],
             "const2": gen_val[1]}

    r_data = requests.request("POST",
                              base_trigger + "/add",
                              params=query,
                              headers={'Content-Type': 'application/octet-stream'},
                              data=data,
                              verify=False)
    print(r_data.text)

    # action
    data = d
    gen_val = gen_c()
    query = {"trigger_id": id,
             "user_id": user,
             "const1": gen_val[0],
             "const2": gen_val[1]}

    r_data = requests.request("POST",
                              base_action + "/add", params=query,
                              headers={'Content-Type': 'application/octet-stream'},
                              data=data,
                              verify=False)
    print(r_data.text)

    # platform
    data = F
    query = {"trigger_id": id,
             "user_id": user,
             "api_trigger": base_trigger + "/recall",
             "api_action": base_action + "/recall",
             "token_trigger": token_trigger,
             "token_action": token_action}

    r_data = requests.request("POST",
                              base_platform + "/add", params=query,
                              headers={'Content-Type': 'application/octet-stream'},
                              data=data,
                              verify=False)
    print(r_data.text)


def add_combine(user, id):
    process = subprocess.run(f"~/example_rules/bin/client " + str(id), shell=True)

    # action
    with open("dec.txt", mode='rb') as file:
        data = file.read()
        query = {"trigger_id": id,
                 "user_id": user,
                 "data_dec": base64.b64encode(data)}

        r_data = requests.request("POST",
                                  base_action + "/add",
                                  params=query,
                                  headers={'Content-Type': 'application/octet-stream'},
                                  data=data,
                                  verify=False)
        print(r_data.text)

    # platform
    with open("table.txt", mode='rb') as file:
        data = file.read()
        query = {"trigger_id": id,
                 "user_id": user}
        r_data = requests.request("POST",
                                  base_platform + "/add",
                                  params=query,
                                  headers={'Content-Type': 'application/octet-stream'},
                                  data=data,
                                  verify=False)
        print(r_data.text)

    # trigger
    with open("enc.txt", mode='rb') as file:
        data = file.read()
        query = {"trigger_id": id,
                 "user_id": user}

        r_data = requests.request("POST",
                                  base_trigger + "/add",
                                  params=query,
                                  headers={'Content-Type': 'application/octet-stream'},
                                  data=data,
                                  verify=False)
        print(r_data.text)
