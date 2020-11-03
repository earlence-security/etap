#!/bin/bash

export FLASK_ENV=development
export FLASK_APP=tap.py
flask run --port 5001 --host 0.0.0.0