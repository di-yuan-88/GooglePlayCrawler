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
        'https://play.google.com/store/apps/category/MEDICAL',
        'https://play.google.com/store/apps/category/HEALTH_AND_FITNESS',
        'https://play.google.com/store/apps/details?id=com.theinnerhour.b2b',
        'https://play.google.com/store/apps/details?id=com.goodrx'
    ]

    rules =( 
        Rule(LinkExtractor(allow=("https://play\.google\.com/store/apps/details", )), 
            # process_links=lambda l: l[:2],
            callback = 'parse_app'  
            , follow = True
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
            logger.warning('gp_name exception = %s', error)
            item['gp_name'] = ''

        try:
            item['gp_url'] = response.xpath('//link[@rel="alternate"][1]/@href').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_url except = ', error)
            logger.warning('gp_url exception = %s', error)
            item['gp_url'] = ''

        try:
            item['gp_id'] = response.xpath('//meta[@name="appstore:store_id"]/@content').extract_first().strip()
        except Exception as error:
            exception_count += 1
            # print('gp_id except = ', error)
            logger.warning('gp_id exception = %s', error)
            item['gp_id'] = ''       
        try:
            item['gp_intro'] = response.xpath('//meta[@itemprop="description"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_intro except = ', error)
            logger.warning('gp_intro exception = %s', error)
            item['gp_intro'] = '' 

        try:
            item['gp_category'] = response.xpath('//a[@itemprop="genre"]/text()').extract_first().strip()
        except Exception as error:
            exception_count += 1
            # print('gp_category except = ', error)
            logger.warning('gp_category exception = %s', error)
            item['gp_category'] = '' 

        try:
            item['gp_price'] = response.xpath('//div[@itemprop="offers"]/meta[@itemprop="price"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_price except = ', error)
            logger.warning('gp_price exception = %s', error)
            item['gp_price'] = '' 

        try:
            item['gp_rating'] = response.xpath('//div[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_rating except = ', error)
            logger.warning('gp_rating exception = %s', error)
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
            logger.warning('gp_review_ct exception = %s', error)
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
                    logger.warning('review_user exception = %s', error)
                    review['review_user'] = '' 

                try:
                    rating_star = featured.xpath('div/div[2]/div[1]/div[1]/div/span[1]/div/div/@aria-label')[
                        0].extract()
                    rating_star = re.search(r"\d+", rating_star).group(0)
                    review['review_rating'] = rating_star
                except Exception as error:
                    exception_count += 1
                    # print('review_rating exception = ', error)
                    logger.warning('review_rating exception = %s', error)
                    review['review_rating'] = '' 
                
                try:
                #//*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[1]/div[1]/div/span[2]
                    review['review_date'] = featured.xpath('div/div[2]/div[1]/div[1]/div/span[2]/text()').extract_first().strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_date exception = ', error)
                    logger.warning('review_date exception = %s', error)
                    review['review_date'] = '' 
                
                try:
                    review['review_text'] = featured.xpath('div/div[2]/div[2]/span[1]/text()').extract_first()
                # review_text = "".join(list(review_text)).strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_text exception = ', error)
                    logger.warning('review_text exception = %s', error)
                    review['review_text'] = ''

                # full review
                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[2]/span[2]/text()
                # review_text_full = featured.xpath('div/div[2]/div[2]/span[2]/text()').extract_first()
                try:
                    review['review_text_full'] = featured.xpath('div/div[2]/div[2]/span[2]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('review_text_full exception = ', error)
                    logger.warning('review_text_full exception = %s', error)
                    review['review_text_full'] = ''

                # how many user find it helpfull
                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[5]
                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[5]/div/div[2]/div[1]/div[2]/div/span/div/content/span/div
                # aria-label="Number of times this review was rated helpful"


                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/div[1]/div[2]/div/span/div/content/span/div
                try:
                    review['helpfulness'] = featured.xpath('div/div[2]/div[1]/div[2]/div/span/div/content/span/div/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('review_text_full exception = ', error)
                    logger.warning('review_helpfulness exception = %s', error)
                    review['helpfulness'] = ''

                # dev's response to reviews

                try:
                    review['reply'] = featured.xpath('div/div[2]/div[3]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('reply exception = ', error）
                    logger.warning('reply exception = %s', error)
                    review['reply'] = ''

                try:
                    review['reply_date'] = featured.xpath('div/div[2]/div[3]/div[2]/span[2]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('reply_date exception = ', error)
                    logger.warning('reply_date exception = %s', error)
                    review['reply_date'] = ''
                
                review['retrv_date'] = datetime.datetime.now()

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
    ,'https://play.google.com/store/apps/details?id=com.hssn.anatomy'
    ,'https://play.google.com/store/apps/details?id=ai.kanghealth'
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
            logger.warning('gp_name exception = %s', error)
            item['gp_name'] = ''

        try:
            item['gp_url'] = response.xpath('//link[@rel="alternate"][1]/@href').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_url except = ', error)
            logger.warning('gp_url exception = %s', error)
            item['gp_url'] = ''

        try:
            item['gp_id'] = response.xpath('//meta[@name="appstore:store_id"]/@content').extract_first().strip()
        except Exception as error:
            exception_count += 1
            # print('gp_id except = ', error)
            logger.warning('gp_id exception = %s', error)
            item['gp_id'] = ''       
        try:
            item['gp_intro'] = response.xpath('//meta[@itemprop="description"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_intro except = ', error)
            logger.warning('gp_intro exception = %s', error)
            item['gp_intro'] = '' 

        try:
            item['gp_category'] = response.xpath('//a[@itemprop="genre"]/text()').extract_first().strip()
        except Exception as error:
            exception_count += 1
            # print('gp_category except = ', error)
            logger.warning('gp_category exception = %s', error)
            item['gp_category'] = '' 

        try:
            item['gp_price'] = response.xpath('//div[@itemprop="offers"]/meta[@itemprop="price"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_price except = ', error)
            logger.warning('gp_price exception = %s', error)
            item['gp_price'] = '' 

        try:
            item['gp_rating'] = response.xpath('//div[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content').extract_first()
        except Exception as error:
            exception_count += 1
            # print('gp_rating except = ', error)
            logger.warning('gp_rating exception = %s', error)
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
            logger.warning('gp_review_ct exception = %s', error)
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
                    logger.warning('review_user exception = %s', error)
                    review['review_user'] = '' 

                try:
                    rating_star = featured.xpath('div/div[2]/div[1]/div[1]/div/span[1]/div/div/@aria-label')[
                        0].extract()
                    rating_star = re.search(r"\d+", rating_star).group(0)
                    review['review_rating'] = rating_star
                except Exception as error:
                    exception_count += 1
                    # print('review_rating exception = ', error)
                    logger.warning('review_rating exception = %s', error)
                    review['review_rating'] = '' 
                
                try:
                #//*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[1]/div[1]/div/span[2]
                    review['review_date'] = featured.xpath('div/div[2]/div[1]/div[1]/div/span[2]/text()').extract_first().strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_date exception = ', error)
                    logger.warning('review_date exception = %s', error)
                    review['review_date'] = '' 
                
                try:
                    review['review_text'] = featured.xpath('div/div[2]/div[2]/span[1]/text()').extract_first()
                # review_text = "".join(list(review_text)).strip()
                except Exception as error:
                    exception_count += 1
                    # print('review_text exception = ', error)
                    logger.warning('review_text exception = %s', error)
                    review['review_text'] = ''

                # full review
                # //*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[14]/div/div[2]/div[2]/span[2]/text()
                # review_text_full = featured.xpath('div/div[2]/div[2]/span[2]/text()').extract_first()
                try:
                    review['review_text_full'] = featured.xpath('div/div[2]/div[2]/span[2]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('review_text_full exception = ', error)
                    logger.warning('review_text_full exception = %s', error)
                    review['review_text_full'] = ''

                try:
                    review['helpfulness'] = featured.xpath('div/div[2]/div[1]/div[2]/div/span/div/content/span/div/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('review_text_full exception = ', error)
                    logger.warning('review_helpfulness exception = %s', error)
                    review['helpfulness'] = ''

                try:
                    review['reply'] = featured.xpath('div/div[2]/div[3]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('reply exception = ', error）
                    logger.warning('reply exception = %s', error)
                    review['reply'] = ''

                try:
                    review['reply_date'] = featured.xpath('div/div[2]/div[3]/div[2]/span[2]/text()').extract_first()
                except Exception as error:
                    exception_count += 1
                    # print('reply_date exception = ', error)
                    logger.warning('reply_date exception = %s', error)
                    review['reply_date'] = ''
                
                review['retrv_date'] = datetime.datetime.now()
                yield review
        else:
            return

        if exception_count >= 3:
            logger.warning('Total_failure_parse exceptions with %s is %d', response.url, exception_count)
            return

