#!/bin/bash

export FLASK_ENV=development
export FLASK_APP=tap.py
export EMP_TAP_BINARY="../emp_src/bin/tap"
flask run --port 5001