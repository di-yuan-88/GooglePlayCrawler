# -*- coding: utf-8 -*-
# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import time
import scrapy
from scrapy.http import HtmlResponse, Request
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from scrapy.exceptions import IgnoreRequest
from gp.settings import CHROME_PATH, CHROME_DRIVER_PATH
# from gp.logging import scrapyLog
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from scrapy.utils.log import configure_logging

# logger = logging.getLogger('dlMiddleware')

# Disable default Scrapy log settings.
configure_logging(install_root_handler=False)

# Define your logging settings.
log_format = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
log_level = logging.INFO  
log_file = 'D:/Local/MMA/log/gp_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt'

logging.basicConfig(
    format=log_format,
    level=log_level
)

rotating_file_log = TimedRotatingFileHandler(log_file, when = 'H', interval = 3, encoding = 'utf-8')
rotating_file_log.setFormatter(logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S"))
rotating_file_log.setLevel(logging.INFO)

logger = logging.getLogger()
logger.addHandler(rotating_file_log)

# another not working logging trial
# logger_name = 'dlMiddleware'
# logManager = scrapyLog(logger_name)
# logger = logManager.getLogger()

class ChromeDownloaderMiddleware(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        # options = webdriver.FirefoxOptions()
        options.add_argument('--headless') 
        if CHROME_PATH:
            options.binary_location = CHROME_PATH
        if CHROME_DRIVER_PATH:
            self.driver = webdriver.Chrome(chrome_options=options, executable_path=CHROME_DRIVER_PATH)  
            # self.driver = webdriver.Firefox(firefox_options=options, executable_path=CHROME_DRIVER_PATH)
        else:
            self.driver = webdriver.Chrome(chrome_options=options)
            # self.driver = webdriver.Firefox(firefox_options=options) 

    def __del__(self):
        self.driver.close()

    def process_request(self, request, spider):
        try:
            # print('Chrome driver begin with', request.url)
            logger.info('Chrome driver begin for: %s', request.url)

            self.driver.get(request.url)

            appCategory = self.driver.find_elements_by_xpath('//a[@itemprop="genre"]')

            allowed_cat = ['Health & Fitness', 'Medical']

            if len(appCategory) > 0 and appCategory[0].text in allowed_cat:

                try:
                    body = self.driver.page_source
                
                except:
                    logger.info('Something wrong with: %s', request.url)
                    raise IgnoreRequest("Page parse error")

                read_review = self.driver.find_elements_by_xpath('//span[contains(text(), "Read All Reviews")]')

                if len(read_review) == 0:
                    return HtmlResponse(url=request.url, body=body, request=request, encoding='utf-8',
                                    status=200)
                else:
                    read_review_button = read_review[0].find_element_by_xpath('./../..')
                    read_review_button.click()
                    time.sleep(1)

                    try:
                        tmp = self.driver.page_source                 
                    except:
                        logger.info('Something wrong with: %s, return the basic app info.', self.driver.current_url)
                        return HtmlResponse(url=request.url, body=body, request=request, encoding='utf-8',
                                    status=200)
                    
                    body = tmp
                    review_ct = len(self.driver.find_elements_by_xpath('//div[@jsname="fk8dgd"]//div[@class="zc7KVe"]'))

                    n = 0
                    while n <= 20:
                        n += 1
                        # logger.info('n is %d', n)
                        if len(self.driver.find_elements_by_xpath('//span[contains(text(), "Show More")]')) == 0:
                            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(2)

                            if review_ct == len(self.driver.find_elements_by_xpath('//div[@jsname="fk8dgd"]//div[@class="zc7KVe"]')):
                                logger.info('No more reviews to load')
                                break
                            else:    
                                review_ct = len(self.driver.find_elements_by_xpath('//div[@jsname="fk8dgd"]//div[@class="zc7KVe"]'))
                                # logger.info('scroll down, total: %d', review_ct)
                                continue
                                    
                            # except WebDriverException:
                            #     logger.error("Page_source error occurred after %d reviews", review_ct)
                            #     break
                        else:
                            show_more = self.driver.find_elements_by_xpath('//span[contains(text(), "Show More")]')
                            show_more_button = show_more[0].find_element_by_xpath('./../..')
                            try:
                                # show_more_button.click()
                                self.driver.execute_script("arguments[0].click();", show_more_button)
                            except WebDriverException:
                                # print(self.driver.current_url, "cannot load more:", error)
                                logger.info("cannot click show_more for %s", self.driver.current_url)
                                break
                            time.sleep(2)
                            
                            # try:
                            #     tmp = self.driver.page_source
                            review_ct = len(self.driver.find_elements_by_xpath('//div[@jsname="fk8dgd"]//div[@class="zc7KVe"]'))
                            # logger.info('more records loaded: total %d', review_ct)
                            # except WebDriverException:
                            #     logger.error("Page loading error with %d reviews", review_ct)
                            #     break
                        try:
                            body = self.driver.page_source
                        except:
                            logger.error("Page_source error occurred in loop %d for %s" % (n, self.driver.current_url))
                            break
                        
                    logger.info('%d reviews loaded for %s' % (review_ct, self.driver.current_url))
                    return HtmlResponse(url=self.driver.current_url, body=body, request=request, encoding='utf-8', status=200)                    
            else:
                # print ('not_medical')
                logger.info('Not a health or mecical app: %s', request.url)
                raise IgnoreRequest("Not a health or mecical app")
        except TimeoutException:
            return HtmlResponse(url=request.url, request=request, encoding='utf-8', status=500)
            # return HtmlResponse(url=self.driver.current_url, body=self.driver.page_source, request=request, encoding='utf-8', status=200)
        finally:
            logger.info('Chrome driver end: %s', self.driver.current_url)