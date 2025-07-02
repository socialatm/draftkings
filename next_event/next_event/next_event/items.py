# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class NextEventItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    bout_number = scrapy.Field()
    fighter_1 = scrapy.Field()
    fighter_2 = scrapy.Field()
    date = scrapy.Field()
    bout = scrapy.Field()
    location = scrapy.Field()
    event_name = scrapy.Field()
    
