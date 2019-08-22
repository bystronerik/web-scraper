import functools
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor

from requests_futures.sessions import FuturesSession

from indexing.task import IndexingTask


class Indexer:

    def __init__(self, config):
        self.config = config

        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=self.config.get_max_threads()))

    def start(self, page):
        self.session.cookies = page.get_cookie_jar()
        results = list()

        tasks = {}
        for url in page.get_indexer().get_urls():
            future, task = self.index(page, url)
            tasks[future] = task

            if self.config.get_indexer().get_wait_after_request()['enabled']:
                time.sleep(self.config.get_indexer().get_wait_after_request()['seconds'])

        for future, task in tasks.items():
            try:
                future.result()
                results.extend(task.get_result())
            except Exception as e:
                print('indexing error - ' + str(e))
                traceback.print_exc()

        return results

    def index(self, page, url):
        task = IndexingTask(url, page)
        future = self.session.get(url,
                                  headers=self.config.get_extractor().get_headers(),
                                  hooks={
                                      'response': functools.partial(task.run),
                                  })
        return future, task
