from scrapy.crawler import CrawlerProcess
from scrapy import Spider, Request


class testCrawl(Spider):
    name = "test"
    url = "https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2020_E486&Option=1"

    def start_requests(self):
        yield Request(url=self.url, callback=self.parse_profile)

    def parse_profile(self, response):
        profile = {}
        outer_table = response.css("table.horseProfile table.table_eng_text")
        for inner_table in outer_table:
            for row in inner_table.css("tr"):
                key = row.css("td:first-child::text").get()
                value = row.css("td:last-child")

                if value.css("*") and value.xpath(".//select"):
                    value = value.xpath(".//select/option/text()").getall()
                elif value.css("*") and value.xpath(".//a"):
                    value = [
                        {
                            "text": a.xpath(".//text()").get().strip(),
                            "url": a.xpath("@href").get(),
                        }
                        for a in value.xpath(".//a")
                    ]
                else:
                    # Default case: get all text content, including nested elements
                    value = value.xpath(".//text()").get()

                profile[key] = value

        yield profile


process = CrawlerProcess()
process.crawl(testCrawl)
process.start()
