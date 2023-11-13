from abc import ABC, abstractmethod

class Summarizer(ABC):

    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    def get_summary(self, full_text: str) -> str:
        pass
