import json
import os
import sys


class ScraperConfig:

    def __init__(self, config_file):
        self.config_file = config_file

        self.max_processes = None
        self.max_threads = None
        self.output_directory = None

        self.load()

    def load(self):
        with open(self.config_file, 'r', encoding="utf-8") as fd:
            config = json.load(fd)

            self.max_threads = config['max-threads']
            self.max_processes = config['max-processes']

            self.output_directory = config['output-directory']
            if self.output_directory[0] == ".":
                self.output_directory = self.output_directory.replace(".", str(sys.path[0]), 1)

            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory, exist_ok=True)

    def get_max_threads(self):
        return self.max_threads

    def get_max_processes(self):
        return self.max_processes

    def get_output_directory(self):
        return self.output_directory
