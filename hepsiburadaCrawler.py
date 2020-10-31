import scrapy
from abc import ABC


def serialize_price(price):
    return float(
        price.replace(',', '.')
    )


def serialize_score(score):
    return float(
        score.replace(',', '.')
    )


class HepsiBuradaBuyboxItem(scrapy.Item):
    name = scrapy.Field()
    seller = scrapy.Field()
    price = scrapy.Field()
    seller_score = scrapy.Field()


class HepsiBuradaSpider(scrapy.Spider, ABC):
    name = "hepsiburada"
    sku = None

    def start_requests(self):
        if self.sku:
            yield scrapy.Request(url='https://www.hepsiburada.com/ara?q=' + self.sku,
                                 callback=HepsiBuradaSpider.search_results)

    @staticmethod
    def search_results(response):
        url = response.xpath('//li[@class="search-item col lg-1 md-1 sm-1  custom-hover not-fashion-flex"]/div')[0].\
            xpath('a/@href').extract()[0]
        url = 'https://www.hepsiburada.com' + url
        yield scrapy.Request(url=url, callback=HepsiBuradaSpider.get_product_details)

    @staticmethod
    def get_product_details(response):
        name = response.xpath('//h1[@class="product-name best-price-trick"]/text()')[0].extract().strip()
        price = response.xpath('//div[@class="extra-discount-price"]/span/text()').extract()[0]
        seller = response.xpath('//div[@class="seller-container"]/span[@class="seller"]/span/a/text()').extract()[0]\
            .strip()
        seller_score = response.xpath('//div[@class="seller-container"]/div[@id="merchantRatingTop"]/'
                                      'div[@id="merchantRatingTopPrice"]/span[2]/text()').extract()[0].strip()
        yield HepsiBuradaBuyboxItem(
            name=name,
            price=serialize_price(price),
            seller=seller,
            seller_score=serialize_score(seller_score) if seller != 'Hepsiburada' else None
        )
