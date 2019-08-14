import functools
import sys
import traceback
from concurrent.futures.thread import ThreadPoolExecutor

from lxml import etree
from lxml.etree import Element, ElementTree
from requests_futures.sessions import FuturesSession

from extracting.task import ExtractingTask
from utils import Utils


class Extractor:

    def __init__(self, config, structure_config, enums_config):
        self.config = config
        self.structure_config = structure_config
        self.enums_config = enums_config

        try:
            self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=self.config.get_max_threads()))
        except Exception as e:
            traceback.print_exc()

    def start(self, page, data):
        self.session.cookies = page.get_cookie_jar()
        data_chunks = Utils.chunks_list(data, round(len(data) / self.config.get_max_threads()) + 1)

        root = Element(self.structure_config.get_structure()['root']['xml-tag'])
        for data_chunk in data_chunks:
            tasks = {}
            for url in data_chunk:
                future, task = self.extract(page, url)
                tasks[future] = task

            for future, task in tasks.items():
                try:
                    future.result()
                    for item in task.get_xml():
                        root.append(item)
                except Exception as e:
                    print('extractor error - ' + str(e))
                    traceback.print_exc()

        xml = ElementTree(root)
        with open(self.config.get_output_directory() + page.get_id() + '.xml', 'wb') as f:
            f.write(etree.tostring(xml, xml_declaration=True, encoding='UTF-8'))

    def extract(self, page, url):
        task = ExtractingTask(url, self.structure_config, self.enums_config, page)
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
