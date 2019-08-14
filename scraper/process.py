import sys
import traceback
from concurrent.futures.thread import ThreadPoolExecutor

from requests_futures.sessions import FuturesSession

from extracting.extractor import Extractor
from indexing.indexer import Indexer
from config.page import PageConfig


class ScraperProcess:

    def __init__(self, config, structure_config, enums_config, pages):
        self.config = config
        self.structure_config = structure_config
        self.enums_config = enums_config
        self.pages = pages

        self.indexer = Indexer(self.config)
        self.extractor = Extractor(self.config, self.structure_config, self.enums_config)

        try:
            self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=self.config.get_max_threads()))
        except Exception as e:
            traceback.print_exc()

    def run(self):
        for page_id, file in self.pages.items():
            page = PageConfig(page_id, file)

            if page.get_login().is_enabled():
                self.perform_login(page)

            if page.get_indexer().is_enabled():
                results = self.indexer.start(page)
            else:
                results = page.get_indexer().get_urls()
            self.extractor.start(page, results)

    def perform_login(self, page):
        self.session.cookies = page.get_cookie_jar()
        self.session.post(url=page.get_login().get_url(), data=page.get_login().get_data()).result()
