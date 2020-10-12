import json
import trigger

trigger.init()

formatter = [{'type': 'int'}, {'type': 'str', 'length': 4}]
formatter = json.dumps(formatter)

trigger.add_new_secret(1, b'0' * 8, formatter)
trigger.add_new_secret(1, b'1' * 8, formatter)

blob = trigger.encode(1, [1, 2])

trigger.print_db()



