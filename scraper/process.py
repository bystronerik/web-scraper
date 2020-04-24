import logging
from concurrent.futures.thread import ThreadPoolExecutor

from requests_futures.sessions import FuturesSession

from config.page import PageConfig
from extracting.extractor import Extractor
from indexing.indexer import Indexer


class ScraperProcess:

    def __init__(self, config, structure_config, enums_config, pages, debug):
        self.debug = debug
        self.config = config
        self.structure_config = structure_config
        self.enums_config = enums_config
        self.pages = pages

        self.indexer = Indexer(self.config, debug)
        self.extractor = Extractor(self.config, debug, self.structure_config, self.enums_config)

        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=self.config.get_max_threads()))

    def run(self):
        for page_id, file in self.pages.items():
            try:
                logging.info("Started scraping page (" + page_id + ")")
                page = PageConfig(page_id, file)

                if page.get_login().is_enabled():
                    self.perform_login(page)

                self.extractor.start(page, self.indexer.start(page) if page.get_indexer().is_enabled() else page
                                     .get_indexer().get_urls())
                logging.info("Ended scraping page (" + page_id + ")")
            except Exception as e:
                logging.error("Scraping page failed (" + page_id + ")", exc_info=True)

    def perform_login(self, page):
        self.session.cookies = page.get_cookie_jar()
        self.session.post(url=page.get_login().get_url(), data=page.get_login().get_data()).result()
