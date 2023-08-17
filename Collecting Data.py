import scrapy
import json
import os
import requests
from scrapy.crawler import CrawlerProcess

class GitHubRepoSpider(scrapy.Spider):
    name = 'github_repo_spider'
    download_dir = 'javascript_files'

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    def start_requests(self):
        with open('Repositories link.txt', 'r') as file:
            input_links = file.readlines()
        for link in input_links:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse_directory(self, response):
        data = json.loads(response.body)
        for file in data:
            if file['type'] == 'file' and file['name'].endswith('.js'):
                js_code_url = file['download_url']
                yield {
                    'js_code_url': js_code_url,
                }
                self.download_js_file(js_code_url)

        for subdir in data:
            if subdir['type'] == 'dir':
                subdir_url = subdir['url']
                yield scrapy.Request(subdir_url, callback=self.parse_directory)

    def parse(self, response):
        data = json.loads(response.body)
        for file in data:
            if file['type'] == 'file' and file['name'].endswith('.js'):
                js_code_url = file['download_url']
                yield {
                    'js_code_url': js_code_url,
                }
                self.download_js_file(js_code_url)

        for subdir in data:
            if subdir['type'] == 'dir':
                subdir_url = subdir['url']
                yield scrapy.Request(subdir_url, callback=self.parse_directory)

    def download_js_file(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(self.download_dir, url.split('/')[-1])
            with open(filename, 'wb') as file:
                file.write(response.content)
            self.log(f"Downloaded {filename}")
        else:
            self.log(f"Failed to download {url}, status code: {response.status_code}")

# Start the spider
process = CrawlerProcess()
process.crawl(GitHubRepoSpider)
process.start()
