import unittest

from law_reader.common import BillIdentifier, LegislativeChamber


class BillIdentifierTest(unittest.TestCase):

    def test_guid_parse(self):
        bill = BillIdentifier("20230HB1449P1633")
        self.assertEqual(bill.legislative_session, "2023")
        self.assertEqual(bill.session_type, "0")
        self.assertEqual(bill.chamber, LegislativeChamber.HOUSE.value)
        self.assertEqual(bill.bill_number, "1449")
        self.assertEqual(bill.printer_number, "1633")


if __name__ == '__main__':
    unittest.main()
