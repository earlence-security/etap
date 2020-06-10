import os
import subprocess
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.fernet import Fernet


emp_client_binary = '/home/ruizhe/example_rules/bin/client'


def setup(rule_id):
    subprocess.run([emp_client_binary, str(rule_id)], cwd='/tmp')

    enc = Path('/tmp/enc.txt').read_bytes()
    dec = Path('/tmp/dec.txt').read_bytes()
    F = Path('/tmp/table.txt').read_bytes()

    d1 = dec[:16]
    d1_ = dec[16:32]

    dec = dec[32:]
    d2 = b''
    for i in range(0, len(dec), 16):
        digest = hashes.Hash(hashes.SHAKE128(16), backend=default_backend())
        digest.update(dec[i:i+16])
        d2 += digest.finalize()


    k = Fernet.generate_key()

    data = k + d2

    nonce = b'0'*13
    aesgcm = AESCCM(d1_)
    d2_ = aesgcm.encrypt(nonce, data, None)

    return enc + k, d1 + d2_, F


# e, d, F = setup()
#
# Path('/tmp/enc').write_bytes(e)
# Path('/tmp/dec').write_bytes(d)
# Path('/tmp/F').write_bytes(F)

