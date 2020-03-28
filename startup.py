import sys
import os
from os import path

from scraper.scraper import Scraper

if __name__ == '__main__':
    config = None
    debug = False

    args = sys.argv[1:]
    for arg in args:
        if arg[:1] == "-":
            if arg == "-c":
                config = args[args.index(arg) + 1]
            if arg == "-d":
                debug = True

                if not path.exists("debug"):
                    os.mkdir(str(sys.path[0]) + "/debug")

    if config is None:
        print('startup.py -c <configuration>')
        sys.exit(2)

    scraper = Scraper(config, debug)
    scraper.start()
