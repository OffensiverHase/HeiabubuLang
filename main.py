import os
import platform
from sys import exit

from Driver import start

"""the main entry for Heiabubu, kind of useless though"""


def main() -> int:
    if platform.system() == 'Windows':
        os.system('color')
    return start()


if __name__ == '__main__':
    code = main()
    exit(code)
