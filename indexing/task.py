import logging
import sys
from contextlib import closing
from urllib import parse as urllib_parse

from lxml import html as lxml_html


class IndexingTask:

    def __init__(self, debug, url, page):
        self.debug = debug
        self.url = url
        self.page = page

        self.result = None

    def run(self, response, *args, **kwargs):
        with closing(response) as response:
            content_type = response.headers['Content-Type'].lower()

            if content_type is None:
                return

            if content_type.find('html') > -1:
                try:
                    html = lxml_html.document_fromstring(response.text)
                except Exception as e:
                    html = lxml_html.document_fromstring(response.content)

                if self.debug:
                    file = open(sys.path[0] + "/debug/" + urllib_parse.quote_plus(self.url) + ".html", "w",
                                encoding='utf-8')
                    file.write(lxml_html.tostring(html, encoding='unicode'))
                    file.close()
                self.parse(html)

    def parse(self, html):
        try:
            paths = self.page.get_indexer().get_paths()

            self.result = []
            for element in paths['item'](html):
                link = paths['link'](element)
                if len(link) != 0:
                    self.result.append(self.process_value('link', link[0]))
        except Exception as e:
            logging.error("Indexing task failed (" + self.url + ")", exc_info=True)

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
        if key in self.page.get_indexer().get_append():
            return text + self.page.get_indexer().get_append()[key]
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


class PaginationCheckTask(IndexingTask):

    def parse(self, html):
        try:
            config = self.page.get_indexer().get_pagination_config()
            paths = config.get_selectors()

            self.result = []
            if paths["pages-count"] != "":
                for x in range(config.get_starting_page(), int(paths["pages-count"](html)[0])+1):
                    self.result.append(self.url.replace(str(config.get_starting_page()), str(x)))

            if paths["per-page"] != "" \
                    and paths["items-count"] != "":
                pass  # TODO

            if paths["next-page"] != "":
                pass  # TODO
        except Exception as e:
            logging.error("Indexing task failed (" + self.url + ")", exc_info=True)
