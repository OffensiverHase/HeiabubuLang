import os
import sys

from Shell import start


def main():
    if sys.platform == 'win32':
        os.system('color')
    start()


if __name__ == '__main__':
    main()
