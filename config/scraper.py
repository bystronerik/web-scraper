import json
import os
import sys
import traceback


class ScraperConfig:

    def __init__(self, config_file, proxy_config_file):
        self.config_file = config_file
        self.proxy_config_file = proxy_config_file

        self.max_processes = None
        self.max_threads = None
        self.output_directory = None

        self.indexer_config = None
        self.extractor_config = None
        self.proxy_config = None

        self.load()

    def load(self):
        with open(self.config_file, 'r', encoding="utf-8") as fd:
            config = json.load(fd)

            self.max_threads = config['max-threads']
            self.max_processes = config['max-processes']

            self.output_directory = config['output-directory']
            if self.output_directory[0] == ".":
                self.output_directory = self.output_directory.replace(".", str(sys.path[0]), 1)

            indexer_config = config['indexer']
            self.indexer_config = ScraperIndexerConfig(indexer_config['headers'], indexer_config['wait-after-request'])

            extractor_config = config['extractor']
            self.extractor_config = ScraperExtractorConfig(extractor_config['headers'], extractor_config['wait-after-request'])

            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory, exist_ok=True)

        if os.path.exists(self.proxy_config_file):
            if os.path.isfile(self.proxy_config_file):
                with open(self.proxy_config_file, 'r', encoding="utf-8") as fd:
                    try:
                        config = json.load(fd)

                        proxies = {}
                        for proxy in config['proxies']:
                            proxies[proxy['base-url']] = proxy['proxies']

                        self.proxy_config = ProxyConfig(proxies)
                    except Exception as e:
                        print("proxy config error")
                        traceback.print_exc()
                return

        self.proxy_config = ProxyConfig({})

    def get_indexer(self):
        return self.indexer_config

    def get_extractor(self):
        return self.extractor_config

    def get_proxies_config(self):
        return self.proxy_config

    def get_max_threads(self):
        return self.max_threads

    def get_max_processes(self):
        return self.max_processes

    def get_output_directory(self):
        return self.output_directory


class ScraperExtractorConfig:

    def __init__(self, headers, wait_after_request):
        self.wait_after_request = wait_after_request
        self.headers = headers

    def get_wait_after_request(self):
        return self.wait_after_request

    def get_headers(self):
        return self.headers


class ScraperIndexerConfig:

    def __init__(self, headers, wait_after_request):
        self.wait_after_request = wait_after_request
        self.headers = headers

    def get_wait_after_request(self):
        return self.wait_after_request

    def get_headers(self):
        return self.headers


class ProxyConfig:

    def __init__(self, proxies):
        self.proxies = proxies

    def get_proxies(self):
        return self.proxies

    def get_proxies_for_url(self, url):
        if url in self.proxies:
            return {'http': self.proxies[url][0]}
        return {}
