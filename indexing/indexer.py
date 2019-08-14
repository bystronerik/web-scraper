import functools
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
                                  headers={
                                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                                      'Accept-Language': 'cs,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,sk;q=0.6',
                                      'Accept-Encoding': 'gzip, deflate, br',
                                      'Cache-Control': 'max-age=0',
                                      'Connection': 'keep-alive',
                                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
                                  },
                                  hooks={
                                      'response': functools.partial(task.run),
                                  })
        return future, task
