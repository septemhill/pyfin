from interfaces import Notifier
import requests
import time
import json
from dataclasses import dataclass


@dataclass
class Holding:
    ticker: str
    percentWeight: float

    def __str__(self) -> str:
        return f"- Ticker:`{self.ticker}`: `{self.percentWeight}%`"


class VOOHoldingsScraper:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    def scrape(self):
        response = requests.get(
            "https://investor.vanguard.com/vmf/api/VOO/portfolio-holding/stock.json",
        )

        title: str = f"{time.strftime('%Y-%m-%d')} [Ticker] VOO Holdings"
        content: str = time.strftime("%Y-%m-%d")

        data = json.loads(response.text)

        holdings_data = data.get("fund", {}).get("entity", [])

        holdings: list[Holding] = [
            Holding(
                ticker=rate["ticker"],
                percentWeight=rate["percentWeight"],
            )
            for rate in holdings_data
        ]

        # print(holdings)

        self.notifier.thread_notify(title, content, holdings)
