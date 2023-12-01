from abc import ABC, abstractmethod

from law_reader.common.RevisionSummaryInfo import RevisionSummaryInfo


class DBInterface(ABC):
    """
    Interface for database classes.
    This is created to ensure that all database classes have the same methods, and to enhance unit testing.
    As well as to guide the implementation or replacement of the database classes.
    This class is meant to be inherited by other classes.
    All methods in this class are meant to be overridden.
    """

    def __init__(self):
        pass

    @abstractmethod
    def download_bill_text(self, revison_internal_id: int) -> str:
        """
        Downloads the full text of a bill from the database
        :param revison_internal_id: the unique id of the bill
        :return: the full text of the bill
        """
        pass

    def upload_summary(self, revision_info: RevisionSummaryInfo, summary_text: str):
        """
        Uploads a summary to the database, linking it to the appropriate entry in the "Revisions" table
        :param revision_info: the unique id of the bill
        :param summary_text: the text of the summary
        """
        pass

    def get_revisions_without_summaries(self) -> list[RevisionSummaryInfo]:
        """
        Gets the unique ids of all bills without summaries
        :return: a list of unique ids of bills without summaries
        """
        pass