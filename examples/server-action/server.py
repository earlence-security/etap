from flask.blueprints import Blueprint
from action.Action import Action

bp = Blueprint('server', __name__)
MAX_SIZE = 3

t = Action('/home/ruizhe/example_rules/')


@bp.route('/add', methods=['POST'])
@t.add_wrapper()
def add():
    print('succeed.')
    return {'data': 'ok',
            'src': 'server-action'}


@bp.route('/recall', methods=['POST'])
@t.dec_wrapper()
def recall():
    return {'data': 'ok',
            'src': 'server-action'}
