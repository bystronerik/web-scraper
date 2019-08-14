import json


class EnumsConfig:

    def __init__(self, config_file):
        self.config_file = config_file

        self.enums = None

        self.load()

    def load(self):
        with open(self.config_file, 'r', encoding="utf8") as fd:
            self.enums = json.load(fd)['enums']

    def get_enums(self):
        return self.enums
