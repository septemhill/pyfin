from interfaces import Notifier
import requests
import time
import json
from dataclasses import dataclass


@dataclass
class ReferenceBenchmarkRate:
    updated: str
    value: float
    id: str

    def __str__(self) -> str:
        return (
            f"- Currency:`{self.id}`: `{self.value}%`, Last updated: `{self.updated}`"
        )


class IBReferenceBenchmarkRateScraper:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    def scrape(self):
        response = requests.get(
            "https://www.interactivebrokers.com/webrest/interests/benchmarks/llc",
        )

        # print(response.text)
        # message = f"--- IB Margin Rates ---\n{margin_table.to_string()}"

        title: str = f"{time.strftime('%Y-%m-%d')} [IB] Reference Benchmark Rates"
        content: str = time.strftime("%Y-%m-%d")

        data = json.loads(response.text)
        rates: list[ReferenceBenchmarkRate] = [
            ReferenceBenchmarkRate(**rate) for rate in data
        ]

        self.notifier.thread_notify(title, content, rates)
