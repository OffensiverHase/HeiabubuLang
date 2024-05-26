import os
import platform
import shutil
from sys import exit

from termcolor import colored

from Driver import start

"""the main entry for Heiabubu, kind of useless though"""


def main() -> int:
    if platform.system() == 'Windows':
        os.system('color')
    if shutil.which('gcc') is None:
        print(colored('For now Heiabubu needs gcc installed', 'red'))
        return 1
    return start()


if __name__ == '__main__':
    code = main()
    exit(code)
