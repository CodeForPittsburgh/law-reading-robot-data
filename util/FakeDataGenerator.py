import random
import uuid
from datetime import datetime

from db_interfaces.PostgresDBInterface import PostgresDBInterface
from law_reader import BillIdentifier, Revision
from lorem_text import lorem

from util.load_environment import load_environment


class FakeDataGenerator:
    """
    This class is used to generate fake data for testing purposes
    """

    def __init__(self):
        self.db_interface = PostgresDBInterface()


    def generate_fake_data(self, num_entries: int):
        """
        Generates a list of fake data for testing purposes
        Populates the REVISION, BILL, REVISION_TEXT, and SUMMARY tables with fake data
        :param num_entries: The number of entries to generate
        """
        while num_entries > 0:
            # Generate a fake bill identifier
            bill_identifier = self.generate_fake_bill_id()
            # Randomly determine the number of revisions for the bill to generate (1 to 3)
            num_revisions = random.randint(1, 3)
            # Generate a fake bill and revisions
            for i in range(num_revisions):
                revision = self.generate_fake_revision(bill_identifier)
                # Insert the fake bill and revision into the database
                self.db_interface.add_revision(
                    bill_identifier=BillIdentifier(revision.revision_guid),
                    revision=revision
                )
                # Upload bill text for the revision
                self.db_interface.upload_bill_text(
                    full_text=lorem.paragraphs(3),
                    revision_guid=revision.revision_guid
                )
                # Summarize the bill text
                summary = lorem.paragraph()
                # Upload the summary
                self.db_interface.upload_summary(
                    revision_guid=revision.revision_guid,
                    summary_text=summary
                )
                num_entries -= 1



    @staticmethod
    def generate_fake_bill_id() -> str:
        """
        Generates a fake bill identifier for testing purposes
        :return: A BillIdentifier
        """
        # Randomly generated year
        year = random.randint(2000, 2021)
        # Generate either 0 (regular session) or 1 (special session)
        session_type = random.choice([0, 1])
        # Generate either "H" (House) or "S" (Senate)
        chamber = random.choice(["H", "S"])
        # Randomly generated bill number
        bill_number = random.randint(1, 9999)
        # Compose
        bill_str = f"{year}{session_type}{chamber}B{bill_number}"
        return bill_str

    @staticmethod
    def generate_fake_revision(bill_str: str) -> Revision:
        """
        Generates a fake revision for testing purposes
        :param bill_identifier: The BillIdentifier of the bill to which the revision belongs
        :return: A Revision
        """
        # Randomly generated printer number
        printer_number = random.randint(1, 9999)
        # Combine with bill_str
        bill_identifier = BillIdentifier(f"{bill_str}P{printer_number}")

        # Randomly generated full text link
        full_text_link = f"https://www.fakeurl.com/{str(uuid.uuid4())}"
        # Randomly generated publication date
        publication_date = datetime.now().strftime("%Y-%m-%d")
        # Randomly generated description
        description = lorem.paragraph()
        # Create and return the Revision object
        return Revision(
            revision_guid=bill_identifier.revision_guid,
            printer_no=str(printer_number),
            full_text_link=full_text_link,
            publication_date=publication_date,
            description=description
        )



if __name__ == "__main__":
    load_environment("development")

    generator = FakeDataGenerator()
    generator.generate_fake_data(100)
    print("Fake data generation complete")
