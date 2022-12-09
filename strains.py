
import scrapy
from datetime import datetime
import time


class GoldSpider(scrapy.Spider):
    name = 'strains'
    allowed_domains = ['https://consumer-api.leafly.com']
    url = 'https://consumer-api.leafly.com/api/strain_playlists/v2'
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f'GetStrains/logs/{today}.log'
    custom_settings = {'LOG_LEVEL': 'INFO', 'LOG_FILE': log_file}

    def start_requests(self):
        utc_time = datetime.utcnow()
        crawl_ts = int(time.time())
        crawl_dt = timestamp_to_string(crawl_ts)
        yield scrapy.Request(
                url=self.url,  
                headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
                },
                callback=self.parse,
                meta = {
                    'crawl_ts': crawl_ts,
                    'crawl_dt' : crawl_dt,
                    'utc_time': utc_time  
                }
        )

    def parse(self, response):
        utc_time = response.meta['utc_time']
        crawl_ts = response.meta['crawl_ts']
        crawl_dt = response.meta['crawl_dt']
        json_response = json.loads(response.text)
        data = json_response.get('data')
        for record in data:
            yield {
                'buyingPrice': record['buyingPrice'],
                'sellingPrice': record['sellingPrice'],
                'goldCode': record['code'],
                'sellChange': record['sellChange'],
                'sellChangePercent': record['sellChangePercent'],
                'buyChange': record['buyChange'],
                'buyChangePercent': record['buyChangePercent'],
                'lastUpdate': timestamp_to_string(int(string_to_timestamp(record['dateTime']))),
                'lastUpdateTimeStamp': int(string_to_timestamp(record['dateTime'])),
                'crawlDate': crawl_dt,
                'crawlTimeStamp': crawl_ts
            }
