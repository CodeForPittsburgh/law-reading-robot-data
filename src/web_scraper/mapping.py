"""
Factory that converts the RSS Elements into a Common Bill Data Elements.
"""


class MappingFactory:
    """
    Mapping Factory for converting items.
    """

    @staticmethod
    def map_bill(rss_entry: dict) -> dict | None:
        """
        Returns the RSS Entry as a Dictionary of a Bill.
        :param rss_entry: RSS Entry Item
        :return: Dictionary
        """
        if rss_entry:
            return {
                'title': rss_entry.get('title'),
                'description': rss_entry.get('description', ''),
                'html_link': rss_entry.get('link', ''),
                'pdf_link': rss_entry.get('link', '').replace('txtType=HTM', 'txtType=PDF'),
                'doc_link': rss_entry.get('link', '').replace('txtType=HTM', 'txtType=DOC'),
                'primary_sponsors': rss_entry.get('parss_primesponsor', ''),
                'co_sponsors': rss_entry.get('parss_cosponsors'),
                'last_action': rss_entry.get('parss_lastaction', ''),
                'enacted': rss_entry.get('parss_enacted', 'NO'),
                'passed_house': rss_entry.get('parss_passedhouse', 'NO'),
                'passed_senate': rss_entry.get('parss_passedsenate', 'NO'),
                'published_date': rss_entry.get('published', ''),
                'id': rss_entry.get('id', '')

            }
        return None
