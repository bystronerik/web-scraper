import json


class StructureConfig:

    def __init__(self, config_file):
        self.config_file = config_file

        self.structure = None

        self.load()

    def load(self):
        with open(self.config_file, 'r', encoding="utf-8") as fd:
            self.structure = json.load(fd)

    def get_structure(self):
        return self.structure
