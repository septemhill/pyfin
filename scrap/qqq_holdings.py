from interfaces import Notifier
import requests
import time
import json
from dataclasses import dataclass


@dataclass
class Holding:
    ticker: str
    percentageOfTotalNetAssets: float

    def __str__(self) -> str:
        return f"- Ticker:`{self.ticker}`: `{self.percentageOfTotalNetAssets}%`"


class QQQHoldingsScraper:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    def scrap(self):
        response = requests.get(
            "https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/QQQ/holdings/fund?idType=ticker&interval=monthly&productType=ETF",
        )

        title: str = f"{time.strftime('%Y-%m-%d')} [Ticker] QQQ Holdings"
        content: str = time.strftime("%Y-%m-%d")

        data = json.loads(response.text)

        holdings_data = data.get("holdings", [])

        holdings: list[Holding] = [
            Holding(
                ticker=rate["ticker"],
                percentageOfTotalNetAssets=rate["percentageOfTotalNetAssets"],
            )
            for rate in holdings_data
        ]

        self.notifier.thread_notify(title, content, holdings)
