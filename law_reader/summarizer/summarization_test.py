import unittest
from unittest.mock import Mock, patch
from law_reader.summarizer.summarization import Summarization

class SummarizationTest(unittest.TestCase):

    def setUp(self):
        self.summarization = Summarization()

    def get_full_text(self,file_name):
        try:
            with open(file_name, "r") as file:
                file_text = file.read()
        except FileNotFoundError:
            print(f"The file '{file_name}' was not found in the current directory.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return file_text


    @patch('summarization.ChatOpenAI', return_value=Mock()) 
    def test_get_summary(self, mock_get_summary):
        file_name = "bill_text.txt"  
        full_text = self.get_full_text(file_name)

        summary = self.summarization.get_summary(full_text)
        print(summary)
        self.assertNotEqual(summary, "")
        #self.assertLessEqual(len(summary), 2300)


if __name__ == "__main__":
    unittest.main()