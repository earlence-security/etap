import subprocess
from pathlib import Path


emp_tap_binary = '/home/ruizhe/example_rules/bin/tap'
# rule_id = 1


def exec_rule(X: bytes, F: bytes, rule_id):

    with open('/tmp/input.txt', 'wb') as file:
        file.write(X)

    with open('/tmp/table.txt', 'wb') as file:
        file.write(F)

    print(rule_id)
    subprocess.run([emp_tap_binary, str(rule_id)], cwd='/tmp')

    Y = open('/tmp/output.txt', 'rb').read()

    P = Y[:16]
    Y = Y[16:]
    return P, Y


# P, Y = exec_rule(Path('/tmp/X').read_bytes(), Path('/tmp/F').read_bytes())
#
# Path('/tmp/P').write_bytes(P)
# Path('/tmp/Y').write_bytes(Y)