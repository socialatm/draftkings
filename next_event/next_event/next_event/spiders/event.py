import scrapy
from next_event.util import *
from next_event.items import NextEventItem

class EventSpider(scrapy.Spider):
    name = "event"
    allowed_domains = ["ufcstats.com"]
    start_urls = ["http://ufcstats.com/statistics/events/upcoming?page=all"]

    custom_settings = {
        "FEEDS": {
            "next_event.csv": {"format": "csv", "overwrite": True},
        },
    }

    def parse(self, response):
        # Get the link for the first upcoming event.
        # The selector targets the first event link from the table of upcoming events.
        future_event_link = response.css(
            "tr.b-statistics__table-row a.b-link::attr(href)"
        ).get()
        if future_event_link:
            yield response.follow(future_event_link, self.parse_future_events)

    def parse_future_events(self, response):
        # Get links to all the matchups in the event.
        future_matchups = response.css("tr.b-fight-details__table-row::attr(data-link)").getall()
        
        # Scrape event-level details once to avoid redundant requests.
        event_details_raw = normalize_results(
            response.css("li.b-list__box-list-item::text").getall()
        )
        event_name_raw = normalize_results(
            response.css("h2.b-content__title span.b-content__title-highlight::text").getall()
        )

        event_context = {
            "date": parse_date(event_details_raw[0]) if event_details_raw else None,
            "location": event_details_raw[1] if len(event_details_raw) > 1 else None,
            "event_name": event_name_raw[0] if event_name_raw else "Unknown Event",
        }

        # Iterate through matchups to preserve order and pass the bout number.
        for i, matchup_url in enumerate(future_matchups, start=1):
            yield response.follow(
                matchup_url,
                self.parse_future_matchups,
                cb_kwargs={"event_context": event_context, "bout_number": i},
            )

    def parse_future_matchups(self, response, event_context, bout_number):
        fighter_names = normalize_results(
            response.css("a.b-fight-details__table-header-link::text").getall()
        )

        # Add checks to prevent IndexError if fighter names are not found
        fighter_1 = fighter_names[0] if fighter_names else "N/A"
        fighter_2 = fighter_names[1] if len(fighter_names) > 1 else "N/A"
        bout = normalize_results(
            response.css("i.b-fight-details__fight-title::text").getall()
        )[0]

        # BUG FIX: Use the imported NextEventItem, not FutureFightItem
        item = NextEventItem()
        item["bout_number"] = bout_number
        item["fighter_1"] = fighter_1
        item["fighter_2"] = fighter_2
        item["date"] = event_context.get("date")
        item["bout"] = bout
        item["location"] = event_context.get("location")
        item["event_name"] = event_context.get("event_name")
        yield item
