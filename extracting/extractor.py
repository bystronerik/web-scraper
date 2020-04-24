import functools
import logging
import time
from concurrent.futures.thread import ThreadPoolExecutor

from lxml import etree
from lxml.etree import Element, ElementTree
from requests_futures.sessions import FuturesSession

from extracting.task import ExtractingTask


class Extractor:

    def __init__(self, config, debug, structure_config, enums_config):
        self.config = config
        self.debug = debug
        self.structure_config = structure_config
        self.enums_config = enums_config

        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=self.config.get_max_threads()))

    def start(self, page, data):
        self.session.cookies = page.get_cookie_jar()
        root = Element(self.structure_config.get_structure()['root']['xml-tag'])

        count = 0

        tasks = {}
        for url in data:
            if len(url) == 0:
                continue

            future, task = self.extract(page, url)
            tasks[future] = task

            if self.config.get_extractor().get_wait_after_request()['enabled']:
                time.sleep(self.config.get_extractor().get_wait_after_request()['seconds'])

            count += 1
            if count >= self.config.get_max_threads():
                for future, task in tasks.items():
                    try:
                        future.result()
                        count -= 1
                        for item in task.get_xml():
                            root.append(item)
                    except Exception as e:
                        logging.error("Extracting failed", exc_info=True)

        for future, task in tasks.items():
            try:
                future.result()
                count -= 1
                for item in task.get_xml():
                    root.append(item)
            except Exception as e:
                logging.error("Extracting failed", exc_info=True)

        xml = ElementTree(root)
        with open(self.config.get_output_directory() + page.get_id() + '.xml', 'wb') as f:
            f.write(etree.tostring(xml, xml_declaration=True, encoding='UTF-8'))

    def extract(self, page, url):
        task = ExtractingTask(self.debug, url, self.structure_config, self.enums_config, page)
        future = self.session.get(url,
                                  proxies=self.config.get_proxies_config().get_proxies_for_url(url[0:url.find('/', 8)]),
                                  headers=self.config.get_extractor().get_headers(),
                                  hooks={
                                      'response': functools.partial(task.run),
                                  })
        return future, task
