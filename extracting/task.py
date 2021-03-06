import base64
import logging
import sys
from contextlib import closing
from urllib import parse as urllib_parse

import requests
from lxml import html as lxml_html
from lxml.etree import Element, SubElement
from lxml.html import HtmlElement


class ExtractingTask:

    def __init__(self, debug, url, structure_config, enums_config, page):
        self.debug = debug
        self.url = url
        self.base_url = url[0:url.find('/', 8)]

        self.structure_config = structure_config
        self.enums_config = enums_config
        self.page = page

        self.xml = None

    def run(self, response, *args, **kwargs):
        logging.info("Running extracting task (" + self.url + ")")
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
            root = self.structure_config.get_structure()['root']
            xml = Element(root['xml-tag'])
            self.read(html, xml, list(root['childs'])[0], root['childs'][list(root['childs'])[0]])
            self.xml = xml
        except Exception as e:
            logging.error("Extracting task failed (" + self.url + ")", exc_info=True)

    def read(self, html, xml, key, data):
        try:
            path = self.page.get_extractor().get_items()[key]

            if path == "url":
                result = self.url
            else:
                result = path(html)

            if result is None:
                SubElement(xml, data['xml-tag'])
                return

            if isinstance(result, bool):
                result = str(result)

            if isinstance(result, list):
                if len(result) == 0:
                    SubElement(xml, data['xml-tag'])
                    return

                if not data['multiple']:
                    if isinstance(result[0], HtmlElement):
                        result = result[0]
                    else:
                        result = ' '.join(result)

            if isinstance(result, str):
                text, found = self.process_text(key, result)
                element = SubElement(xml, data['xml-tag'])
                element.text = text
                if not found:
                    element.set("found", "false")
                return

            if isinstance(result, HtmlElement):
                result = [result]

            for html_element in result:
                element = SubElement(xml, data['xml-tag'])
                if len(data['childs']) != 0:
                    for key, child in data['childs'].items():
                        self.read(html_element, element, key, child)
                else:
                    if isinstance(html_element, HtmlElement):
                        if html_element.tag == "img":
                            text, found = self.process_text(key, html_element.get("src"))
                            text = base64.b64encode(requests.get(text).content)
                        else:
                            text, found = self.process_text(key, html_element.text)
                    else:
                        text, found = self.process_text(key, html_element)
                    element.text = text
                    if not found:
                        element.set("found", "false")
        except Exception as e:
            logging.error("Extracting task failed (" + self.url + ")", exc_info=True)

    def process_text(self, key, text):
        if text is not None:
            text = self.add_append(key, text)
            text = self.add_prepend(key, text)
            text = self.search_for_value(key, text)
            text = self.replace_parts(key, text)
            text, found = self.replace_enums(key, text)

            text = text.replace("\n", " ")
            text = text.replace("\r", " ")
            text = text.replace("\r\n", " ")

            return text.strip(), found
        return text, True

    def add_prepend(self, key, text):
        if key in self.page.get_extractor().get_prepend():
            return self.page.get_extractor().get_prepend()[key] + text
        return text

    def add_append(self, key, text):
        if key in self.page.get_extractor().get_append():
            return text + self.page.get_extractor().get_append()[key]
        return text

    def search_for_value(self, key, text):
        if key in self.page.get_extractor().get_values_regexps():
            match = self.page.get_extractor().get_values_regexps()[key].search(text)
            if match is not None:
                return match.group(0)
            else:
                return ""
        return text

    def replace_parts(self, key, string):
        if key in self.page.get_extractor().get_replace_parts():
            for item in self.page.get_extractor().get_replace_parts()[key]:
                string = string.replace(item['part'], item['value'])
        return string

    def replace_enums(self, key, string):
        if key in self.enums_config.get_enums():
            enums = self.enums_config.get_enums()[key]
            for enum in enums:
                if string.lower().find(enum['value'].lower()) != -1:
                    return enum['value'], True
                else:
                    for value in enum['other-values']:
                        if string.lower().find(value.lower()) != -1:
                            return enum['value'], True
            return string, False
        return string, True

    def get_xml(self):
        return self.xml
