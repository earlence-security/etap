import string
import random


def gen_random_text(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def gen_random_number(length, val_min=0, val_max=9):
    return_val = ''
    for i in range(length):
        return_val += str(random.randint(val_min, val_max))

    return return_val


def trigger_id_resoluter(id):
    if id == 1:
        return gen_random_text(144)
    elif id == 2:
        return gen_random_text(144)
    elif id == 3:
        return gen_random_text(144)  #
    elif id == 4:
        return gen_random_text(7)
    elif id == 5:
        return gen_random_text(7)
    elif id == 6:
        return gen_random_text(7)
    elif id == 7:
        return gen_random_text(144)  #
    elif id == 8:
        return gen_random_text(7)  #
    elif id == 9:
        return gen_random_text(20)
    elif id == 10:
        return gen_random_text(144)  #
    elif id == 11:
        return gen_random_text(30)
    elif id == 12:
        return gen_random_text(144)  #
    elif id == 13:
        return gen_random_text(7)  #
    elif id == 14:
        return gen_random_text(1000)
    elif id == 15:
        return gen_random_number(10)  #
    elif id == 16:
        return gen_random_text(144)
    elif id == 17:
        return gen_random_text(144)  #
    elif id == 18:
        return gen_random_text(144)  #
    elif id == 19:
        return gen_random_text(20)  #
    else:
        return ""
