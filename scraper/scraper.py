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

    def __init__(self, config):
        self.pages = {}
        self.config = ScraperConfig(str(sys.path[0]) + '/configurations/' + config + '/config.json')
        self.structure_config = StructureConfig(str(sys.path[0]) + '/configurations/' + config + '/structure.json')
        self.enums_config = EnumsConfig(str(sys.path[0]) + '/configurations/' + config + '/enums.json')

        path = Path(str(sys.path[0]) + '/configurations/' + config + '/pages/')
        for file in path.glob("*.json"):
            page_id = str(file)[len(str(path)) + 1:-5]

            if page_id == "example":
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
        ScraperProcess(self.config, self.structure_config, self.enums_config, data).run()
