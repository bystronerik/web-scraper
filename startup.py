import logging
import sys
import os
from datetime import datetime
from os import path

from logger.handlers import StatusLogsHandler
from scraper.scraper import Scraper

if __name__ == '__main__':
    config = None
    debug = False
    pages = None

    args = sys.argv[1:]
    for arg in args:
        if arg[:1] == "-":
            if arg == "-c":
                config = args[args.index(arg) + 1]

            if arg == "-d":
                debug = True

                if not path.exists("debug"):
                    os.mkdir(str(sys.path[0]) + "/debug")

            if arg == "-p":
                pages = args[args.index(arg) + 1]
                pages = pages.split(";")

    if config is None:
        print('startup.py -c <configuration>')
        sys.exit(2)

    loggingLevel = logging.INFO
    if debug:
        loggingLevel = logging.DEBUG

    if not path.exists("logs"):
        os.mkdir(str(sys.path[0]) + "/logs")
    if not path.exists("logs/" + config):
        os.mkdir(str(sys.path[0]) + "/logs/" + config)
    logging.basicConfig(format='[%(asctime)s][%(levelname)s]: %(message)s',  datefmt='%d/%m/%Y %H:%M:%S',
                        level=loggingLevel, filename="logs/" + config + "/" + datetime.now().strftime("%d-%m-%Y-%H:%M:%S") + '.log')

    logFormatter = logging.Formatter('[%(asctime)s][%(levelname)s]: %(message)s', '%d/%m/%Y %H:%M:%S')
    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    statusLogsHandler = StatusLogsHandler(config)
    statusLogsHandler.setFormatter(logFormatter)
    rootLogger.addHandler(statusLogsHandler)

    logging.info("System init")
    try:
        scraper = Scraper(config, debug, pages)
        logging.info("Scraping start")
        scraper.start()
        logging.info("Scraping end")
        # logging.info("Import start")
        # import
        # logging.info("Import end")
    except Exception as e:
        logging.error("System failed", exc_info=True)
    logging.info("System shutdown")
