import scrapy
from gp.items import GPAppsItem, GPReviewItem
# from gp.logging import scrapyLog
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
import re
import datetime
import logging

logger = logging.getLogger('crawler')
# logger_name = 'gp_crawl'
# logManager = scrapyLog(logger_name)
# logger = logManager.getLogger()

class GooglePlayCrawl(CrawlSpider):
    name = 'gp_crawl'
    allowed_domains = ['play.google.com']
    start_urls = [
        'http://play.google.com/',
        'https://play.google.com/store/apps/details?id=com.doctorondemand.android.patient'
    ]

    rules =( 
        Rule(LinkExtractor(allow=("https://play\.google\.com/store/apps/details", )), 
            # process_links=lambda l: l[:10],
            callback = 'parse_app'  
            ,follow = True
            ),
        # Rule(LinkExtractor(allow=('https://play\.google\.com/store/apps/collection', )), follow = True)
    )

    def parse_app(self, response):
        # print('Begin parse ', response.url)
        logger.info('Begin parse %s', response.url)
        # self.logger.info('Begin parse %s', response.url)

        item = GPAppsItem()

        content = response.xpath('//div[@class="LXrl4c"]')

        exception_count = 0

        try:
            item['gp_name'] = content.xpath('//h1[@class="AHFaub"]/span/text()')[0].extract()
        except Exception as error:
            exception_count += 1
            # print('gp_name except = ', error)
            logger.warning('gp_name except = %s', error)
            item['gp_name'] = ''

        try:
            item['gp_url'] = response.xpath('//link[@rel="alternate"][1]/@href').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_url except = ', error)
            logger.warning('gp_url except = %s', error)
            item['gp_url'] = ''

        try:
            item['gp_id'] = response.xpath('//meta[@name="appstore:store_id"]/@content').extract_first().strip()
        except Exception as error:
            exception_count += 1
            # print('gp_id except = ', error)
            logger.warning('gp_id except = %s', error)
            item['gp_id'] = ''       
        try:
            item['gp_intro'] = response.xpath('//meta[@itemprop="description"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_intro except = ', error)
            logger.warning('gp_intro except = %s', error)
            item['gp_intro'] = '' 

        try:
            item['gp_category'] = response.xpath('//a[@itemprop="genre"]/text()').extract_first().strip()
        except Exception as error:
            exception_count += 1
            # print('gp_category except = ', error)
            logger.warning('gp_category except = %s', error)
            item['gp_category'] = '' 

        try:
            item['gp_price'] = response.xpath('//div[@itemprop="offers"]/meta[@itemprop="price"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_price except = ', error)
            logger.warning('gp_price except = %s', error)
            item['gp_price'] = '' 

        try:
            item['gp_rating'] = response.xpath('//div[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_rating except = ', error)
            logger.warning('gp_rating except = %s', error)
            item['gp_rating'] = '' 

        try:
            review_ct = response.xpath('//div[@itemprop="aggregateRating"]/meta[@itemprop="reviewCount"]/@content').extract_first()
            if review_ct is None:
                item['gp_review_ct'] = 0
            else:
                item['gp_review_ct'] = review_ct
        except Exception as error:
            exception_count += 1
            # print('gp_review_ct except = ', error)
            logger.warning('gp_review_ct except = %s', error)
            item['gp_review_ct'] = ''
        
        item['retrieve_date'] = datetime.datetime.now()

        yield item

        review_elems = response.xpath('//div[@jscontroller="H6eOGe"]')
        #//*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div
        # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div
        if len(review_elems) > 0:

            for featured in review_elems:

                review = GPReviewItem()
                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[1]/div[1]/span

                review['appID'] = response.xpath('//meta[@name="appstore:store_id"]/@content').extract_first().strip()

                try:
                    review['review_user'] = featured.xpath('div/div[2]/div[1]/div[1]/span/text()')[0].extract().strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_user exception = ', error)
                    logger.warning('review_user except = %s', error)
                    review['review_user'] = '' 

                try:
                    rating_star = featured.xpath('div/div[2]/div[1]/div[1]/div/span[1]/div/div/@aria-label')[
                        0].extract()
                    rating_star = re.search(r"\d+", rating_star).group(0)
                    review['review_rating'] = rating_star
                except Exception as error:
                    exception_count += 1
                    # print('review_rating exception = ', error)
                    logger.warning('review_rating except = %s', error)
                    review['review_rating'] = '' 
                
                try:
                #//*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[1]/div[1]/div/span[2]
                    review['review_date'] = featured.xpath('div/div[2]/div[1]/div[1]/div/span[2]/text()').extract_first().strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_date exception = ', error)
                    logger.warning('review_date except = %s', error)
                    review['review_date'] = '' 
                
                try:
                    review['review_text'] = featured.xpath('div/div[2]/div[2]/span[1]/text()').extract_first()
                # review_text = "".join(list(review_text)).strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_text exception = ', error)
                    logger.warning('review_text except = %s', error)
                    review['review_text'] = ''

                # full review
                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[2]/span[2]/text()
                # review_text_full = featured.xpath('div/div[2]/div[2]/span[2]/text()').extract_first()
                try:
                    review['review_text_full'] = featured.xpath('div/div[2]/div[2]/span[2]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('review_text_full exception = ', error)
                    logger.warning('review_text_full except = %s', error)
                    review['review_text_full'] = ''

                # dev's response to reviews

                try:
                    review['reply'] = featured.xpath('div/div[2]/div[3]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('reply exception = ', error）
                    logger.warning('reply except = %s', error)
                    review['reply'] = ''

                try:
                    review['reply_date'] = featured.xpath('div/div[2]/div[3]/div[2]/span[2]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('reply_date exception = ', error)
                    logger.warning('reply_date except = %s', error)
                    review['reply_date'] = ''
                
                yield review
        else:
            return

        if exception_count >= 3:
            # print('Total_failure_parse exceptions: ', exception_count)
            logger.warning('Total_failure_parse exceptions with %s is %d', response.url, exception_count)
            return

class GooglePlaySpider(scrapy.Spider):
    name = 'gp'
    allowed_domains = ['play.google.com']
    start_urls = ['https://play.google.com/store/apps/details?id=com.urbandroid.lux'
    ,'https://play.google.com/store/apps/details?id=com.ibuild.ifasting'
    ,'https://play.google.com/store/apps/details?id=com.zodinplex.thunder.sounds.relax.and.sleep'
    ,'https://play.google.com/store/apps/details?id=com.hssn.anatomy'
    ]

    # def __init__(self, *args, **kwargs):
    #     urls = kwargs.pop('urls', [])  # 获取参数
    #     if urls:
    #         self.start_urls = urls.split
    #         print('start urls = ', self.start_urls)

    def parse(self, response):
        print('Begin parse ', response.url)

        logger.info('Begin parse %s', response.url)
        # self.logger.info('Begin parse %s', response.url)

        item = GPAppsItem()

        content = response.xpath('//div[@class="LXrl4c"]')

        exception_count = 0

        try:
            item['gp_name'] = content.xpath('//h1[@class="AHFaub"]/span/text()')[0].extract()
        except Exception as error:
            exception_count += 1
            # print('gp_name except = ', error)
            logger.warning('gp_name except = %s', error)
            item['gp_name'] = ''

        try:
            item['gp_url'] = response.xpath('//link[@rel="alternate"][1]/@href').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_url except = ', error)
            logger.warning('gp_url except = %s', error)
            item['gp_url'] = ''

        try:
            item['gp_id'] = response.xpath('//meta[@name="appstore:store_id"]/@content').extract_first().strip()
        except Exception as error:
            exception_count += 1
            # print('gp_id except = ', error)
            logger.warning('gp_id except = %s', error)
            item['gp_id'] = ''       
        try:
            item['gp_intro'] = response.xpath('//meta[@itemprop="description"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_intro except = ', error)
            logger.warning('gp_intro except = %s', error)
            item['gp_intro'] = '' 

        try:
            item['gp_category'] = response.xpath('//a[@itemprop="genre"]/text()').extract_first().strip()
        except Exception as error:
            exception_count += 1
            # print('gp_category except = ', error)
            logger.warning('gp_category except = %s', error)
            item['gp_category'] = '' 

        try:
            item['gp_price'] = response.xpath('//div[@itemprop="offers"]/meta[@itemprop="price"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_price except = ', error)
            logger.warning('gp_price except = %s', error)
            item['gp_price'] = '' 

        try:
            item['gp_rating'] = response.xpath('//div[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_rating except = ', error)
            logger.warning('gp_rating except = %s', error)
            item['gp_rating'] = '' 

        try:
            review_ct = response.xpath('//div[@itemprop="aggregateRating"]/meta[@itemprop="reviewCount"]/@content').extract_first()
            if review_ct is None:
                item['gp_review_ct'] = 0
            else:
                item['gp_review_ct'] = review_ct
        except Exception as error:
            exception_count += 1
            # print('gp_review_ct except = ', error)
            logger.warning('gp_review_ct except = %s', error)
            item['gp_review_ct'] = ''
        
        item['retrieve_date'] = datetime.datetime.now()

        yield item

        review_elems = response.xpath('//div[@jscontroller="H6eOGe"]')
        #//*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div
        # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div
        if len(review_elems) > 0:

            for featured in review_elems:

                review = GPReviewItem()
                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[1]/div[1]/span

                review['appID'] = response.xpath('//meta[@name="appstore:store_id"]/@content').extract_first().strip()

                try:
                    review['review_user'] = featured.xpath('div/div[2]/div[1]/div[1]/span/text()')[0].extract().strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_user exception = ', error)
                    logger.warning('review_user except = %s', error)
                    review['review_user'] = '' 

                try:
                    rating_star = featured.xpath('div/div[2]/div[1]/div[1]/div/span[1]/div/div/@aria-label')[
                        0].extract()
                    rating_star = re.search(r"\d+", rating_star).group(0)
                    review['review_rating'] = rating_star
                except Exception as error:
                    exception_count += 1
                    # print('review_rating exception = ', error)
                    logger.warning('review_rating except = %s', error)
                    review['review_rating'] = '' 
                
                try:
                #//*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[1]/div[1]/div/span[2]
                    review['review_date'] = featured.xpath('div/div[2]/div[1]/div[1]/div/span[2]/text()').extract_first().strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_date exception = ', error)
                    logger.warning('review_date except = %s', error)
                    review['review_date'] = '' 
                
                try:
                    review['review_text'] = featured.xpath('div/div[2]/div[2]/span[1]/text()').extract_first()
                # review_text = "".join(list(review_text)).strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_text exception = ', error)
                    logger.warning('review_text except = %s', error)
                    review['review_text'] = ''

                # full review
                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[2]/span[2]/text()
                # review_text_full = featured.xpath('div/div[2]/div[2]/span[2]/text()').extract_first()
                try:
                    review['review_text_full'] = featured.xpath('div/div[2]/div[2]/span[2]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('review_text_full exception = ', error)
                    logger.warning('review_text_full except = %s', error)
                    review['review_text_full'] = ''

                # dev's response to reviews

                try:
                    review['reply'] = featured.xpath('div/div[2]/div[3]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('reply exception = ', error）
                    logger.warning('reply except = %s', error)
                    review['reply'] = ''

                try:
                    review['reply_date'] = featured.xpath('div/div[2]/div[3]/div[2]/span[2]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('reply_date exception = ', error)
                    logger.warning('reply_date except = %s', error)
                    review['reply_date'] = ''
                
                yield review
        else:
            return

        if exception_count >= 3:
            print('spider_failure_parse_too_much_exception')
            return

