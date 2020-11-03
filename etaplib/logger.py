import logging

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


s_logger = logging.getLogger('storage')
e_logger = logging.getLogger('execution')
s_logger.setLevel(logging.INFO)
e_logger.setLevel(logging.INFO)

s_handler = logging.StreamHandler()
e_handler = logging.StreamHandler()

s_formatter = logging.Formatter(f'{bcolors.OKBLUE}%(message)s{bcolors.ENDC}')
e_formatter = logging.Formatter(f'{bcolors.OKGREEN}%(message)s{bcolors.ENDC}')
s_handler.setFormatter(s_formatter)
e_handler.setFormatter(e_formatter)

s_logger.addHandler(s_handler)
e_logger.addHandler(e_handler)