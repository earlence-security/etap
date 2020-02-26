from flask.blueprints import Blueprint
from flask import request
from .helper import trigger_id_resoluter
from trigger.Trigger import Trigger

bp = Blueprint('server', __name__)
MAX_SIZE = 3
C_SIZE = 12
t = Trigger('/home/ruizhe/example_rules')

trigger_data = ""


@bp.route('/add', methods=['POST'])
@t.add_wrapper()
def add():
    print('succeed.')
    return {'data': 'ok',
            'src': 'server-trigger'}


@bp.route('/recall', methods=['POST'])
def recall():
    rule_id = request.values.get('trigger_id')
    global trigger_data
    trigger_data = trigger_id_resoluter(rule_id)
    operate()
    return {
        'data': 'ok',
        'src': 'server-trigger'
    }


@t.enc_wrapper(trigger_data)
def operate():
    print("Running...")
    pass
