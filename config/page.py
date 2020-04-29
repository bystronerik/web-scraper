import json
import logging
import re
import sys
from urllib import parse as urllib_parse

from lxml.etree import XPath

from scraper import cookies


class PageConfig:

    def __init__(self, id, config_file):
        self.id = id
        self.config_file = config_file

        self.indexer_config = None
        self.extractor_config = None
        self.login_config = None

        self.google_search_query = None
        self.cookie_jar = None

        self.load()

    def load(self):
        with open(self.config_file, 'r', encoding="utf-8") as fd:
            try:
                config = json.load(fd)

                if 'google-search-query' in config:
                    self.google_search_query = config['google-search-query']

                self.cookie_jar = cookies.cookiejar.LWPCookieJar()

                if not config["enable-cookies"]:
                    self.cookie_jar.set_policy(cookies.BlockAllCookies())

                login_config = config['login']
                self.login_config = LoginConfig(login_config['enabled'], login_config['url'], login_config['data'])

                indexer_config = config['indexer']
                indexer_enabled = indexer_config['enabled']

                indexing_urls = indexer_config['urls']
                if len(indexer_config['urls-files']) != 0:
                    for file in indexer_config['urls-files']:
                        if file[0] == ".":
                            file = file.replace(".", str(sys.path[0]), 1)
                        with open(file, 'r', encoding="utf-8") as urls_file:
                            urls = json.load(urls_file)
                            indexing_urls.extend(urls['urls'])

                completed_indexing_urls = list()
                if len(indexer_config["url-pattern"]) != 0:
                    for url in indexing_urls:
                        if isinstance(url, dict):
                            replaced_url = indexer_config["url-pattern"]
                            for key, value in url.items():
                                replaced_url = replaced_url.replace("{" + key + "}", urllib_parse.quote_plus(value))
                            completed_indexing_urls.append(replaced_url)
                        else:
                            completed_indexing_urls.append(url)
                else:
                    completed_indexing_urls = indexing_urls
                indexing_urls = completed_indexing_urls

                indexing_paths = {}
                if indexer_enabled:
                    for item, path in indexer_config['selectors'].items():
                        try:
                            indexing_paths[item] = XPath(path)
                        except Exception as e:
                            print(e)
                replace_parts = indexer_config['replace-parts']
                prepend = indexer_config['prepend']
                append = indexer_config['append']
                values_regexps = {}
                for item, regex in indexer_config['values-regexps'].items():
                    values_regexps[item] = re.compile(regex)

                pagination_config = indexer_config['pagination']

                pagination_paths = {}
                if pagination_config['enabled']:
                    for item, path in pagination_config['selectors'].items():
                        try:
                            pagination_paths[item] = XPath(path)
                        except Exception as e:
                            print(e)
                pagination_config = PaginationConfig(pagination_config['enabled'], pagination_config['starting-page'],
                                                     pagination_config['offset-per-page'], pagination_paths)

                self.indexer_config = PageIndexerConfig(indexer_enabled, replace_parts, values_regexps, prepend, append,
                                                        indexing_paths, indexing_urls, pagination_config)

                extractor_config = config['extractor']
                items = {}
                for item, path in extractor_config['selectors'].items():
                    try:
                        if path == "url":
                            items[item] = path
                            continue
                        items[item] = XPath(path)
                    except Exception as e:
                        print(e)
                replace_parts = extractor_config['replace-parts']
                prepend = extractor_config['prepend']
                append = extractor_config['append']
                values_regexps = {}
                for item, regex in extractor_config['values-regexps'].items():
                    values_regexps[item] = re.compile(regex)
                self.extractor_config = PageExtractorConfig(replace_parts, values_regexps, prepend, append, items)
            except Exception as e:
                logging.error("Page config error (" + self.id + ")", exc_info=True)

    def get_indexer(self):
        return self.indexer_config

    def get_extractor(self):
        return self.extractor_config

    def get_login(self):
        return self.login_config

    def get_id(self):
        return self.id

    def get_google_search_query(self):
        return self.google_search_query

    def get_cookie_jar(self):
        return self.cookie_jar


class LoginConfig:

    def __init__(self, enabled, url, data):
        self.enabled = enabled
        self.url = url
        self.data = data

    def is_enabled(self):
        return self.enabled

    def get_url(self):
        return self.url

    def get_data(self):
        return self.data


class PageIndexerConfig:

    def __init__(self, enabled, replace_parts, values_regexps, prepend, append, paths, urls, pagination_config):
        self.enabled = enabled
        self.replace_parts = replace_parts
        self.values_regexps = values_regexps
        self.prepend = prepend
        self.append = append
        self.paths = paths
        self.urls = urls
        self.pagination_config = pagination_config

    def is_enabled(self):
        return self.enabled

    def get_urls(self):
        return self.urls

    def get_paths(self):
        return self.paths

    def get_replace_parts(self):
        return self.replace_parts

    def get_prepend(self):
        return self.prepend

    def get_append(self):
        return self.append

    def get_values_regexps(self):
        return self.values_regexps

    def get_pagination_config(self):
        return self.pagination_config


class PaginationConfig:

    def __init__(self, enabled, starting_page, offset_per_page, selectors):
        self.enabled = enabled
        self.starting_page = starting_page
        self.offset_per_page = offset_per_page
        self.selectors = selectors

    def is_enabled(self):
        return self.enabled

    def get_starting_page(self):
        return self.starting_page

    def get_offset_per_page(self):
        return self.offset_per_page

    def get_selectors(self):
        return self.selectors


class PageExtractorConfig:

    def __init__(self, replace_parts, values_regexps, prepend, append, items):
        self.replace_parts = replace_parts
        self.values_regexps = values_regexps
        self.prepend = prepend
        self.append = append
        self.items = items

    def get_items(self):
        return self.items

    def get_prepend(self):
        return self.prepend

    def get_append(self):
        return self.append

    def get_replace_parts(self):
        return self.replace_parts

    def get_values_regexps(self):
        return self.values_regexps
