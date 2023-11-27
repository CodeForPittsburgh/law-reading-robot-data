
class SummarizationException(Exception):
    """
    A custom exception for summarization errors
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
