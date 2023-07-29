"""
Tests for the Bill Factory.
"""

from src.web_scraper.mapping import MappingFactory
from src.web_scraper.rss import RssFeedManager
from assertpy import assert_that

TEST_BILL_RSS_ITEM = './tests/test_files/bill_item.xml'


def test_map_bill():
    """
    Tests converting a Bill RSS Entry to the desired dictionary.
    """

    manager = RssFeedManager(TEST_BILL_RSS_ITEM)
    items = manager.get_entries()

    assert_that(items).is_not_empty()

    item = items[0]
    assert_that(MappingFactory.map_bill(item)).is_not_empty() \
        .contains_entry({'title': "House Bill 1515 Printer's Number 1718"}) \
        .contains_entry({'html_link': 'https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=HTM&sessYr=2023&sessInd=0&billBody=H&billTyp=B&billNbr=1515&pn=1718'}) \
        .contains_entry({'pdf_link': 'https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=PDF&sessYr=2023&sessInd=0&billBody=H&billTyp=B&billNbr=1515&pn=1718'}) \
        .contains_entry({'doc_link': 'https://www.legis.state.pa.us/cfdocs/legis/PN/Public/btCheck.cfm?txtType=DOC&sessYr=2023&sessInd=0&billBody=H&billTyp=B&billNbr=1515&pn=1718'}) \
        .contains_entry({'description': 'An Act amending Title 61 (Prisons and Parole) of the Pennsylvania Consolidated Statutes'}) \
        .contains_entry({'primary_sponsors': 'Representative MADDEN'}) \
        .contains_entry({'co_sponsors': 'SCHLOSSBERG, BRENNAN'}) \
        .contains_entry({'last_action': 'Referred to JUDICIARY, July 27, 2023'}) \
        .contains_entry({'enacted': 'NO'}) \
        .contains_entry({'passed_house': 'YES'}) \
        .contains_entry({'passed_senate': 'NO'}) \
        .contains_entry({'published_date': 'Thu, 27 Jul 2023 11:47:01 GMT'}) \
        .contains_entry({'id': '20230HB1515P1718'})


def test_map_bill_empty():
    """
    Tests sending an empty item to the mapping function.
    """

    assert_that(MappingFactory.map_bill({})).is_none()