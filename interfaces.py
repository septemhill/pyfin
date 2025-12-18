from typing import Protocol
from typing import Any


class Scraper(Protocol):
    def scrap(self): ...


class Notifier(Protocol):
    def notify(self, title: str, content: str, message: str): ...
    def thread_notify(self, title: str, content: str, thread_messages: list[Any]): ...
