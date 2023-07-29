"""
Unit Tests for the RSS Data Manager.
"""

from src.web_scraper.rss import RssFeedManager
from assertpy import assert_that

TEST_RSS_FILE = './tests/test_files/bills.xml'


def test_get_entries():
    """
    Tests retrieving the items to a dictionary.
    """

    manager = RssFeedManager(TEST_RSS_FILE)

    items = manager.get_entries()
    assert_that(items).is_not_empty()
    assert_that(manager.last_updated).is_not_zero()


def test_refresh_feed():
    """
    Tests refreshing the items in the Cache.
    """

    manager = RssFeedManager(TEST_RSS_FILE)
    items = manager.get_entries()
    assert_that(items).is_not_empty()

    last_updated = manager.last_updated
    manager.refresh_feed()
    assert_that(manager.last_updated).is_greater_than(last_updated)


def test_get_entries_cache():
    """
    Tests that the items are retrieved from the cache.
    """

    manager = RssFeedManager(TEST_RSS_FILE)
    items = manager.get_entries()
    assert_that(items).is_not_empty()

    last_updated = manager.last_updated
    cache_items = manager.get_entries()
    assert_that(cache_items).is_not_empty().is_equal_to(items)
    assert_that(manager.last_updated).is_equal_to(last_updated)
