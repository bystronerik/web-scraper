from contextlib import closing
from lxml import html as lxml_html


class IndexingTask:

    def __init__(self, url, page):
        self.url = url
        self.page = page

        self.result = None

    def run(self, response, *args, **kwargs):
        with closing(response) as response:
            content_type = response.headers['Content-Type'].lower()

            if content_type is None:
                return

            if content_type.find('html') > -1:
                self.parse(lxml_html.document_fromstring(response.text))

    def parse(self, html):
        paths = self.page.get_indexer().get_paths()

        self.result = []
        for element in paths['item'](html):
            self.result.append(self.process_value('link', paths['link'](element)[0]))

    def process_value(self, key, text):
        if text is not None:
            text = self.add_append(key, text)
            text = self.add_prepend(key, text)
            text = self.search_for_value(key, text)
            text = self.replace_parts(key, text)
        return text

    def add_prepend(self, key, text):
        if key in self.page.get_indexer().get_prepend():
            return self.page.get_indexer().get_prepend()[key] + text
        return text

    def add_append(self, key, text):
        if key in self.page.get_extractor().get_append():
            return self.page.get_extractor().get_append()[key] + text
        return text

    def search_for_value(self, key, text):
        if key in self.page.get_indexer().get_values_regexps():
            match = self.page.get_indexer().get_values_regexps()[key].search(text)
            if match is not None:
                return match.group(0)
        return text

    def replace_parts(self, key, string):
        if key in self.page.get_indexer().get_replace_parts():
            for item in self.page.get_indexer().get_replace_parts()[key]:
                string = string.replace(item['part'], item['value'])
        return string

    def get_result(self):
        return self.result
