import functools
import logging
import time
from concurrent.futures.thread import ThreadPoolExecutor

from requests_futures.sessions import FuturesSession

from indexing.task import IndexingTask, PaginationCheckTask


class Indexer:

    def __init__(self, config, debug):
        self.config = config
        self.debug = debug

        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=self.config.get_max_threads()))

    def start(self, page):
        self.session.cookies = page.get_cookie_jar()
        results = list()

        urls = page.get_indexer().get_urls()
        if page.get_indexer().get_pagination_config().is_enabled():
            pagination_config = page.get_indexer().get_pagination_config()
            if pagination_config.get_selectors()["pages-count"] is not None\
                    or pagination_config.get_selectors()["per-page"] is not None \
                    or pagination_config.get_selectors()["items-count"] is not None\
                    or pagination_config.get_selectors()["next-page"] is not None:
                tasks = {}
                for url in page.get_indexer().get_urls():
                    if len(url) == 0:
                        continue

                    future, task = self.check_pagination(page, url.replace("{page}", str(pagination_config.get_starting_page())))
                    tasks[future] = task

                    if self.config.get_indexer().get_wait_after_request()['enabled']:
                        time.sleep(self.config.get_indexer().get_wait_after_request()['seconds'])

                urls = []
                for future, task in tasks.items():
                    try:
                        future.result()
                        urls.extend(task.get_result())
                    except Exception as e:
                        logging.error("Indexing failed", exc_info=True)
        tasks = {}
        for url in urls:
            if len(url) == 0:
                continue

            future, task = self.index(page, url)
            tasks[future] = task

            if self.config.get_indexer().get_wait_after_request()['enabled']:
                time.sleep(self.config.get_indexer().get_wait_after_request()['seconds'])

        for future, task in tasks.items():
            try:
                future.result()
                results.extend(task.get_result())
            except Exception as e:
                logging.error("Indexing failed", exc_info=True)

        return results

    def index(self, page, url):
        task = IndexingTask(self.debug, url, page)
        future = self.session.get(url,
                                  proxies=self.config.get_proxies_config().get_proxies_for_url(url[0:url.find('/', 8)]),
                                  headers=self.config.get_indexer().get_headers(),
                                  hooks={
                                      'response': functools.partial(task.run),
                                  })
        return future, task

    def check_pagination(self, page, url):
        task = PaginationCheckTask(self.debug, url, page)
        future = self.session.get(url,
                                  proxies=self.config.get_proxies_config().get_proxies_for_url(url[0:url.find('/', 8)]),
                                  headers=self.config.get_indexer().get_headers(),
                                  hooks={
                                      'response': functools.partial(task.run),
                                  })
        return future, task
