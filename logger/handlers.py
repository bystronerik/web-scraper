import re
from datetime import datetime
from logging import Handler


class StatusLogsHandler(Handler):

    def __init__(self, config):
        Handler.__init__(self)
        self.config = config
        self.file = './logs/' + self.config + '/'+datetime.now().strftime("%d-%m-%Y-%H:%M:%S")+'.status'
        self.success_pattern = re.compile("Ended scraping page \\((\\w+)\\)")
        self.fail_pattern = re.compile("Scraping page failed \\((\\w+)\\)")

    def emit(self, record):
        with open(self.file, 'a') as file:
            match = self.success_pattern.match(record.getMessage())
            if match:
                file.write(match.group(1) + "=SUCCESS\n")

            match = self.fail_pattern.match(record.getMessage())
            if match:
                file.write(match.group(1) + "=ERROR\n")
