import functools
import sys
from concurrent.futures.process import ProcessPoolExecutor
from pathlib import Path

from config.enums import EnumsConfig
from config.scraper import ScraperConfig
from config.xml import StructureConfig
from scraper.process import ScraperProcess
from utils import Utils


class Scraper:

    def __init__(self, config, debug, pages=None):
        self.debug = debug
        self.pages = {}

        base_path = str(sys.path[0]) + '/configurations/' + config + '/'
        self.config = ScraperConfig(base_path + 'config.json', base_path + 'proxies.json')
        self.structure_config = StructureConfig(base_path + 'structure.json')
        self.enums_config = EnumsConfig(base_path + 'enums.json')

        path = Path(str(sys.path[0]) + '/configurations/' + config + '/pages/')
        for file in path.glob("*.json"):
            page_id = str(file)[len(str(path)) + 1:-5]

            if page_id == "example":
                continue

            if pages is not None:
                if page_id not in pages:
                    continue

            self.pages[page_id] = file

    def start(self):
        data_chunks = Utils.chunks_dict(self.pages, round(len(self.pages) / self.config.get_max_processes()) + 1)
        with ProcessPoolExecutor(self.config.get_max_processes()) as executor:
            tasks = list()
            for data in data_chunks:
                tasks.append(executor.submit(
                    functools.partial(self.create_process, data)))

            for task in tasks:
                task.result()

    def create_process(self, data):
        ScraperProcess(self.config, self.structure_config, self.enums_config, data, self.debug).run()
