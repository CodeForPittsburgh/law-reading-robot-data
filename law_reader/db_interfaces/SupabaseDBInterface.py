import os

from postgrest.types import CountMethod
from supabase import Client, create_client

from law_reader import BillIdentifier, Revision
from law_reader.common.RevisionSummaryInfo import RevisionSummaryInfo
from law_reader.db_interfaces.DBInterface import DBInterface
from law_reader.summarizer.InvalidRTUniqueIDException import InvalidRTUniqueIDException


class SupabaseDBInterface(DBInterface):

    """
    Interface for Supabase database classes.
    """
    def __init__(self, debug=False):
        super().__init__()
        # if debug flag is set, pull data from .env file
        # In production, the environment variables will be set in the github actions workflow
        sb_api_url = os.environ.get("SUPABASE_API_URL")  # github actions secret management
        sb_api_key = os.environ.get("SUPABASE_API_KEY")  # github actions secret management

        self.supabase_connection: Client = create_client(sb_api_url, sb_api_key)

    # region Basic database operations
    def insert(self, table, row_column_dict: dict, return_column: str = ""):
        """
        Inserts a row into the given table
        :param table: The name of the table to insert into
        :param row_column_dict: A dictionary containing the column names and values
        :param return_column: The column to return
        :return: The id of the return column, or None
        """
        api_response = self.supabase_connection.table(table).insert(row_column_dict).execute()
        if return_column != "":
            return api_response.data[0][return_column]

    def simple_select(self, table, columns: list[str], where_conditions: dict = None) -> list[dict[str, any]]:
        """
        Selects rows from the given table and returns them
        :param table: The name of the table to select from
        :param columns: A list of column names to select
        :param where_conditions: A dictionary defining the WHERE conditions (column: value)
        :return: The selected rows, as a list of dictionaries (column: value)
        """
        statement = self.supabase_connection.table(table).select(*columns)
        if where_conditions is not None:
            for column in where_conditions:
                statement = statement.eq(column, where_conditions[column])
        api_response = statement.execute()
        return api_response.data
    #endregion

    #region Intermediate Database Operations

    def row_exists(self, table: str, where_conditions: dict) -> bool:
        """
        Checks if a row exists in the given table
        :param table: The name of the table to check
        :param where_conditions: A dictionary defining the WHERE conditions (column: value)
        :return: True if a row exists, False if not
        """
        statement = self.supabase_connection.table(table).select("*", count=CountMethod.exact)
        for column in where_conditions:
            statement = statement.eq(column, where_conditions[column])
        api_response = statement.execute()
        return api_response.count > 0

    #endregion

    #region summarize_etl
    def download_bill_text(self, revison_internal_id: str) -> str:
        """
        Downloads the full text of a bill from Supabase, using the rt_unique_id
        Raises an InvalidRTUniqueIDException if the bill cannot be found
         or if multiple bills are found with the given rt_unique_id
        :param revison_internal_id: the unique id of the bill in the Revision_Text table
        :return: the full text of the bill
        """
        api_response = self.supabase_connection.table("Revision_Text").select("full_text").eq("rt_unique_id",
                                                                                              revison_internal_id).execute()
        if len(api_response.data) == 0:
            raise InvalidRTUniqueIDException(f"Could not find bill with rt_unique_id {revison_internal_id}")
        elif len(api_response.data) > 1:
            raise InvalidRTUniqueIDException(f"Found multiple bills with rt_unique_id {revison_internal_id}")
        text = api_response.data[0]["full_text"]
        if text is None or text == "":
            raise InvalidRTUniqueIDException(f"Bill with rt_unique_id {revison_internal_id} has no text")
        return text

    def upload_summary(self, revision_info: RevisionSummaryInfo, summary_text: str):
        """
        Uploads a summary to Supabase, linking it to the appropriate entry in the "Revisions" table
        :param revision_info: a RevisionSummaryInfo object containing information about the revision
        :param summary_text: the text of the summary
        """
        # Insert summary into Summaries table and retrieve the summary_id of the new entry
        api_response = self.supabase_connection.table("Summaries").insert(
            {"summary_text": summary_text,
             "revision_internal_id": revision_info.revision_internal_id}). \
            execute()
        summary_id = api_response.data[0]["summary_id"]
        # Update relevant entry in Revisions table (found with revision guid) with summary_id of new entry in Summaries table
        self.supabase_connection.table("Revisions"). \
            update({"active_summary_id": summary_id}). \
            eq("revision_guid", revision_info.revision_guid). \
            execute()

    def get_revisions_without_summaries(self) -> list[RevisionSummaryInfo]:
        """
        Gets the unique ids of all bills without summaries
        :return: a list of unique ids of bills without summaries
        """
        api_response = self.supabase_connection.table("Revisions").select("revision_guid", "rt_unique_id", "revision_internal_id", count=CountMethod.exact).\
            is_("active_summary_id", "NULL").\
            execute()
        return [RevisionSummaryInfo(revision["revision_guid"], revision["rt_unique_id"], revision["revision_internal_id"]) for revision in api_response.data]

    #endregion

    #region rss_etl
    def create_and_attempt_to_insert_bill(self, bill_identifier: BillIdentifier) -> bool:
        pass

    def create_and_attempt_to_insert_revision(self, revision_rss_feed_entry, bill_identifier: BillIdentifier) -> bool:
        pass

    def get_bill_internal_id(self, bill_identifier: BillIdentifier) -> str:
        pass

    #endregion

    # region docx_etl
    def get_revisions_without_bill_text(self) -> list[Revision]:
        """
        Gets the unique ids of all bills without bill text
        :return: a list of unique ids of bills without bill text
        """
        result = self.supabase_connection.table("Revisions").select("*").filter("rt_unique_id", "is", "null").execute()
        results = []
        for record in result.data:
            r = Revision(
                revision_guid=record["revision_guid"],
                full_text_link=record["full_text_link"],
            )
            results.append(r)
        return results

    def upload_bill_text(self, full_text: str, revision_guid: str):
        """
        Uploads the law text from a .docx file to Supabase's "Revision_Text" table,
        linking it to the appropriate entry in the "Revisions" table
        :param full_text: full text of the bill revision
        :param revision_guid: guid of the bill revision
        """
        # Insert full text as entry in Revision_Text table, retrieving the rt_unique_id of the new entry
        response = self.supabase_connection.table('Revision_Text').insert({"full_text": full_text}).execute()
        rt_unique_id = response.data[0]["rt_unique_id"]
        # Update relevant entry in Revisions table (found with revision guid) with rt_unique_id of  new entry in Revision_Text table
        self.supabase_connection.table('Revisions').update({"rt_unique_id": rt_unique_id}).eq("revision_guid", revision_guid).execute()

    # endregion
