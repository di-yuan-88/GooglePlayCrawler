# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class GPAppsItem(scrapy.Item):

    gp_name = scrapy.Field()  # App name
    gp_url = scrapy.Field()  # App URL
    gp_id = scrapy.Field()
    gp_intro = scrapy.Field()
    gp_category = scrapy.Field()
    gp_price = scrapy.Field()
    gp_rating = scrapy.Field()  
    gp_review_ct = scrapy.Field() 
    retrieve_date = scrapy.Field()


class GPReviewItem(scrapy.Item):

    appID = scrapy.Field()
    review_user = scrapy.Field()  
    review_date = scrapy.Field()
    review_text = scrapy.Field()
    review_text_full = scrapy.Field()
    review_rating = scrapy.Field()
    helpfulness = scrapy.Field()
    reply = scrapy.Field()
    reply_date = scrapy.Field()
    retrv_date = scrapy.Field()

    # def __str__(self):
    #     return ""

    # def __repr__(self):
    #     """only print out attr1 after exiting the Pipeline"""
    #     return repr({"attr1": self.attr1})
