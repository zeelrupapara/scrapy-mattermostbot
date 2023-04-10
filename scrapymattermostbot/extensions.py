import json
from datetime import datetime, timedelta, timezone
import requests
from scrapy import signals
from scrapy.exceptions import NotConfigured


class Mattermost(object):
    def __init__(self, stats, webhook_url):
        self.stats = stats
        self.webhook_url = webhook_url

    @classmethod
    def from_crawler(cls, crawler):
        webhook_url = crawler.settings.get('MATTERMOST_WEBHOOK_URL')
        if not webhook_url:
            raise NotConfigured('MATTERMOST_WEBHOOK_URL is missing')
        extension = cls(crawler.stats, webhook_url)
        crawler.signals.connect(extension.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(extension.spider_closed,
                                signal=signals.spider_closed)
        crawler.signals.connect(extension.spider_error,
                                signal=signals.spider_error)
        return extension

    def process_spider_input(self, response, spider):
        spider.crawler.stats.set_value('custom_stat', 'value')
        # collect scraped items
        spider.item_collector.collect(response, spider)

    def spider_closed(self, spider, reason):
        # get collected items
        items_scraped = self.stats.get_value("item_scraped_count")
        success = self.stats.get_value("downloader/response_status_count/200")
        error = self.stats.get_value("downloader/response_status_count/404")
        unauthorized = self.stats.get_value(
            "downloader/response_status_count/403")
        num_of_request = self.stats.get_value("downloader/request_count")
        num_of_response = self.stats.get_value("downloader/response_count")
        text = f"Collected data by {spider.name}"
        data = {
            "attachments": [
                {
                    "fallback": "spider closed",
                    "color": "#3283a8",
                    "text": text,
                    "author_name": "Scrapy Bot",
                    "author_icon": "https://scrapy.org/favicons/favicon-16x16.png",
                    "author_link": "https://scrapy.org/",
                    "thumb_url": "https://scrapy.org/favicons/favicon-192x192.png",
                    "title": "Spider Closed",
                    "fields": [
                                {
                                    "short": False,
                                    "title": "Reason",
                                    "value": str(reason)
                                },
                        {
                                    "short": False,
                                    "title": "Scraped Items",
                                    "value": ":books: " + str(items_scraped)
                                },
                        {
                                    "short": True,
                                    "title": "Success Response",
                                    "value": ":white_check_mark: " + str(success)
                                },
                        {
                                    "short": True,
                                    "title": "Error Response",
                                    "value": ":octagonal_sign: " + str(error)
                                },
                        {
                                    "short": False,
                                    "title": "Unauthorized Response",
                                    "value": ":alien: " + str(unauthorized)
                                },
                        {
                                    "short": True,
                                    "title": "Number of Request",
                                    "value": str(num_of_request)
                                },
                        {
                                    "short": True,
                                    "title": "Number of Response",
                                    "value": str(num_of_response)
                                }
                    ],
                    "footer": spider.name + " spider",
                    "footer_icon": "https://scrapy.org/favicons/favicon-16x16.png",
                    "ts": ":clock11: " + str(self.stats.get_value("start_time").replace(tzinfo=timezone(timedelta(hours=0))).timestamp()),
                }
            ]
        }
        response = requests.post(self.webhook_url, data=json.dumps(
            data), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            spider.logger.error(f'Mattermost request failed: {response.text}')

    def spider_error(self, failure, response, spider):
        items_scraped = self.stats.get_value("item_scraped_count")
        success = self.stats.get_value("downloader/response_status_count/200")
        error = self.stats.get_value("downloader/response_status_count/404")
        unauthorized = self.stats.get_value(
            "downloader/response_status_count/403")
        num_of_request = self.stats.get_value("downloader/request_count")
        num_of_response = self.stats.get_value("downloader/response_count")
        time = str(datetime.now().timestamp())
        text = f"Collected data by {spider.name}"
        data = {
            "attachments": [
                {
                    "fallback": "spider error",
                    "color": "#f44336",
                    "text": text,
                    "author_name": "Scrapy Bot",
                    "author_icon": "https://scrapy.org/favicons/favicon-16x16.png",
                    "author_link": "https://scrapy.org/",
                    "thumb_url": "https://scrapy.org/favicons/favicon-192x192.png",
                    "title": "Spider Error",
                    "fields": [
                                {
                                    "short": False,
                                    "title": "Error Message",
                                    "value": ":octagonal_sign: " + str(failure.getErrorMessage())
                                },
                        {
                                    "short": False,
                                    "title": "Scraped Items",
                                    "value": ":books: " + str(items_scraped)
                                },
                        {
                                    "short": True,
                                    "title": "Success Response",
                                    "value": ":white_check_mark: " + str(success)
                                },
                        {
                                    "short": True,
                                    "title": "Error Response",
                                    "value": ":octagonal_sign: " + str(error)
                                },
                        {
                                    "short": False,
                                    "title": "Unauthorized Response",
                                    "value": ":alien: " + str(unauthorized)
                                },
                        {
                                    "short": True,
                                    "title": "Number of Request",
                                    "value": str(num_of_request)
                                },
                        {
                                    "short": True,
                                    "title": "Number of Response",
                                    "value": str(num_of_response)
                                }
                    ],
                    "footer": spider.name + " spider",
                    "footer_icon": "https://scrapy.org/favicons/favicon-16x16.png",
                    "ts": ":clock11: " + time,
                }
            ]
        }
        response = requests.post(self.webhook_url, data=json.dumps(
            data), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            spider.logger.error(f'Mattermost request failed: {response.text}')

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        text = f"Spider {spider.name} opened"
        time = str(datetime.now().timestamp())
        data = {
            "attachments": [
                {
                    "fallback": "spider opened",
                    "color": "#008800",
                    "text": text,
                    "author_name": "Scrapy Bot",
                    "author_icon": "https://scrapy.org/favicons/favicon-16x16.png",
                    "author_link": "https://scrapy.org/",
                    "thumb_url": "https://scrapy.org/favicons/favicon-192x192.png",
                    "title": "Spider Opened",
                    "footer": spider.name + " spider",
                    "footer_icon": "https://scrapy.org/favicons/favicon-16x16.png",
                    "ts": ":clock11: " + time
                }
            ]
        }
        # make POST request to Mattermost webhook
        response = requests.post(self.webhook_url, data=json.dumps(
            data), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            spider.logger.error(f'Mattermost request failed: {response.text}')
