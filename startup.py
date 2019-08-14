import getopt
import sys

from scraper.scraper import Scraper

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["config="])
    except getopt.GetoptError:
        print('startup.py -c <configuration>')
        sys.exit(2)

    config = None

    for opt, arg in opts:
        if opt == '-h':
            print('startup.py -c <configuration>')
            sys.exit()
        elif opt in ("-c", "--config"):
            config = arg

    if config is None:
        print('startup.py -c <configuration>')
        sys.exit(2)

    scraper = Scraper(config)
    scraper.start()
