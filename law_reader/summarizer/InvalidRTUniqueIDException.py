
class InvalidRTUniqueIDException(Exception):
    """
    A custom exception for invalid rt_unique_id values
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
