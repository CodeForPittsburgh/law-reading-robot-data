"""
RSS Data Feed Manager.
"""

from typing import Any
import feedparser
import time


class RssFeedManager:
    """
    Class for interacting with a Data Feed.
    """

    url: str
    timeout: int
    feed_cache: list[dict]
    last_updated: int

    def __init__(self, url: str, **kwargs):
        """
        Constructor for the Rss Feed Manager.
        :param url: Url to the Rss Feed

        :keyword timeout: Timout in minutes for caching the feed. defaulted to 5
        """

        self.url = url
        self.timeout = kwargs.get('timeout', 5)
        self.feed_cache = []
        self.last_updated = 0

    def get_entries(self) -> list[dict]:
        """
        Retrieves the Entries from the RSS Feed as a collection of Dictionaries.
        :return: List of Dictionaries.
        """
        current_time = time.time()
        if self.last_updated + self.timeout <= current_time:
            self.__load_feed__()
        return self.feed_cache

    def refresh_feed(self) -> None:
        """
        Refreshes the Cache of entries from the Rss Feed ignoring the timeout.
        :return: None
        """
        self.__load_feed__()

    def __load_feed__(self) -> None:
        """
        Loads the items from the Feed to the Cache.
        :return:
        """

        feed = feedparser.parse(self.url)
        self.feed_cache = feed.entries
        self.last_updated = int(time.time())


def get_data_from_rss_feeds() -> Any:  # TODO: Determine the return type
    """
    Gets the data from the RSS feeds
    :return: Raw data from the RSS feeds, in a format that can be processed
    """
    raise NotImplementedError


def process_raw_rss_feed_data(raw_data: Any) -> Any:  # TODO: Determine the return type and type of raw_data
    """
    Processes the raw data from the RSS feeds, extracting relevant information from the raw data.
    :param raw_data:
    :return: Unknown. Possibly list of dictionaries with keys being the sub-item names and values being the values for
    each sub-item (e.g., like description)
    """
    raise NotImplementedError


def write_processed_rss_feed_data_to_csv(processed_data: Any) -> None:  # TODO: Determine the type of processed_data
    """
    Writes the processed data to a CSV file, with the name of the CSV file being the name of the RSS feed as well as the
    date the data was retrieved.
    :param processed_data: 
    :return: None
    """
    raise NotImplementedError


if __name__ == "__main__":
    raw_data = get_data_from_rss_feeds()
    processed_data = process_raw_rss_feed_data(raw_data)
    write_processed_rss_feed_data_to_csv(processed_data)
