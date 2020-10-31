# server.py
import json

from klein import route, run
from scrapy import signals
from scrapy.crawler import CrawlerRunner

from hepsiburadaCrawler import HepsiBuradaSpider


class MyCrawlerRunner(CrawlerRunner):
    """
    Crawler object that collects items and returns output after finishing crawl.
    """

    def __init__(self, settings=None):
        super().__init__(settings=None)
        self.items = []

    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        # keep all items scraped

        # create crawler (Same as in base CrawlerProcess)
        crawler = self.create_crawler(crawler_or_spidercls)

        # handle each item scraped
        crawler.signals.connect(self.item_scraped, signals.item_scraped)

        # create Twisted.Deferred launching crawl
        dfd = self._crawl(crawler, *args, **kwargs)

        # add callback - when crawl is done cal return_items
        dfd.addCallback(self.return_items)
        return dfd

    def item_scraped(self, item, response, spider):
        self.items.append(item)

    def return_items(self, result):
        return self.items


def return_spider_output(output):
    """
    :param output: items scraped by CrawlerRunner
    :return: json with list of items
    """
    return json.dumps([dict(item) for item in output])


@route('/hepsiburada/<sku>')
def schedule(request, sku):
    request.setHeader('Content-Type', 'application/json')
    runner = MyCrawlerRunner()
    deferred = runner.crawl(HepsiBuradaSpider, sku=sku)
    deferred.addCallback(return_spider_output)
    return deferred


run("0.0.0.0", 8080)

