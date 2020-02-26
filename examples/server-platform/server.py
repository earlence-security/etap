from flask.blueprints import Blueprint
from flask import request
from .db import get_db
import requests
from .tap import *

bp = Blueprint('server', __name__)
MAX_SIZE = 3


@bp.route("/add", methods=["POST"])
def add():

    db = get_db()

    if not len(request.data):
        return {
            "error": "no data_table",
            "src": "server-platform"}

    if 'user_id' not in request.values:
        return {"error": "no user",
                "src": "server-platform"}

    if 'trigger_id' not in request.values:
        return {"error": "no id",
                "src": "server-platform"}

    data_table = request.data
    id = request.values.get('user_id') + ':' + request.values.get('trigger_id')

    id_data = db.execute(
        "SELECT * FROM platform_info WHERE literal_id = ?",
        (id,)
    ).fetchone()

    if id_data:
        if int(id_data["data_top"]) - int(id_data["data_end"]) >= MAX_SIZE:
            db.execute(
                "DELETE FROM platform_data WHERE literal_id = ? AND data_index = ?",
                (id, id_data["data_end"])
            )
            db.execute(
                "INSERT INTO platform_data (literal_id, data_table, data_index) "
                "VALUES (?, ?, ?)",
                (id, data_table, id_data["data_top"])
            )

            # update data_index info
            db.execute(
                "UPDATE platform_info SET data_top = ?, data_end = ? "
                "WHERE literal_id = ?",
                (int(id_data["data_top"]) + 1, int(id_data["data_end"]) + 1, id)
            )
            db.commit()
        else:
            db.execute(
                "INSERT INTO platform_data (literal_id, data_table, data_index) "
                "VALUES (?, ?, ?)",
                (id, data_table, id_data["data_top"])
            )
            #  since insert, update size
            db.execute(
                "UPDATE platform_info SET data_top = ? "
                "WHERE literal_id = ?",
                (int(id_data["data_top"]) + 1, id)
            )
            db.commit()
    else:
        if 'api_trigger' not in request.values:
            return {"error": "no api_trigger",
                    "src": "server-platform"}

        if 'api_action' not in request.values:
            return {"error": "no api_action",
                    "src": "server-platform"}

        if 'token_trigger' not in request.values:
            return {"error": "no token_trigger",
                    "src": "server-platform"}

        if 'token_action' not in request.values:
            return {"error": "no token_action",
                    "src": "server-platform"}

        api_trigger = request.values.get('api_trigger')
        api_action = request.values.get('api_action')
        token_trigger = request.values.get('token_trigger')
        token_action = request.values.get('token_action')

        db.execute(
            "INSERT INTO platform_info (literal_id, api_trigger, api_action, "
            "token_trigger, token_action, data_top, data_end) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (id, api_trigger, api_action, token_trigger, token_action, 2, 1)
        )

        db.execute(
            "INSERT INTO platform_data (literal_id, data_table, data_index) "
            "VALUES (?, ?, ?)",
            (id, data_table, 1)
        )
        db.commit()

    print("Added an table [", data_table[:5], "]")

    return {"data": "ok",
            "src": "server-platform"}


@bp.route('/recall', methods=['POST'])
def recall():

    db = get_db()
    print("REVEIVING..")

    if "trigger_id" not in request.values:
        return{"error": "no trigger_id",
               "src": "server-platform"}

    if "user_id" not in request.values:
        return{"error": "no user_id",
               "src": "server-platform"}

    if not request.data:
        return {
            "error": "no data",
            "src": "server-platform"
        }

    if 'X_len' not in request.values:
        return {
            "error": "no X_len",
            "src": "server-platform"
        }

    if 'ct_len' not in request.values:
        return {
            "error": "no ct_len",
            "src": "server-platform"
        }

    literal_id = request.values.get("user_id") + ':' + request.values.get('trigger_id')

    entry_info = db.execute(
        "SELECT * FROM platform_info WHERE literal_id = ?",
        (literal_id,)
    ).fetchone()

    if not entry_info:
        return {"error": "invalid id",
                "src": "server-platform"}

    if entry_info["data_top"] == entry_info["data_end"]:
        return {"error": "expiration token",
                "src": "server-platform"}

    entry = db.execute(
        "SELECT * FROM platform_data WHERE literal_id = ? AND data_index = ?",
        (entry_info["literal_id"], entry_info["data_end"])
    ).fetchone()

    F = entry['data_table']

    db.execute(
        "DELETE FROM platform_data WHERE literal_id = ? AND data_index = ?",
        (entry_info["literal_id"], entry_info["data_end"])
    )

    api_trigger = entry_info["api_trigger"]
    db.execute(
        "UPDATE platform_info SET data_end = ? "
        "WHERE literal_id = ?",
        (int(entry_info["data_end"]) + 1, entry_info["literal_id"])
    )
    db.commit()

    request_data = request.data
    X_len = int(request.values.get('X_len'))
    ct_len = int(request.values.get('ct_len'))

    X = request_data[:X_len]
    ct = request_data[X_len:]
    if len(ct) != ct_len:
        return {
            "error": "length conflict",
            "src": "server-platform"
        }

    send_action(X, ct, F)
    return {"data": "ok",
            "src": "server-platform"}


@bp.route('/send_action', methods=['POST'])
def send_action(X, ct, F):

    print("Preparing to send to action...")
    db = get_db()

    trigger_id = request.values.get("trigger_id")
    user_id = request.values.get('user_id')

    literal_id = user_id + ':' + trigger_id

    entry = db.execute(
        "SELECT * FROM platform_info WHERE literal_id = ?",
        (literal_id,)
    ).fetchone()

    if not entry:
        print("Invalid id: [", trigger_id, "]")
        return {"error": "invalid id",
                "src": "server-platform"}

    api_action = entry["api_action"]

    print("Running [cloud]")
    P, Y = exec_rule(X, F, trigger_id)
    print("Finish [cloud]")

    query_action = {
        "user_id": user_id,
        'trigger_id': trigger_id,
        'P_len': len(P),
        'Y_len': len(Y),
        'ct_len': len(ct)
        }

    print("Preparing to send requests to action...")
    requests.request("POST",
                     api_action,
                     params=query_action,
                     data=P+Y+ct,
                     headers={'Content-Type': 'application/octet-stream'})
    return {"data": "ok",
            "src": "server-platform"}
