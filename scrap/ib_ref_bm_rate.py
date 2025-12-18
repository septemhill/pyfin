from interfaces import Notifier
import requests
import time
import json
from dataclasses import dataclass
from quickchart import QuickChart


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

    def scrap(self):
        response = requests.get(
            "https://www.interactivebrokers.com/webrest/interests/benchmarks/llc",
        )

        title: str = f"{time.strftime('%Y-%m-%d')} [IB] Reference Benchmark Rates"
        content: str = time.strftime("%Y-%m-%d")

        data = json.loads(response.text)
        rates: list[ReferenceBenchmarkRate] = [
            ReferenceBenchmarkRate(**rate) for rate in data
        ]

        currencies = [r.id for r in rates]
        bm_rates = [r.value for r in rates]
        print(bm_rates)

        qc = QuickChart()
        qc.width = 1600
        qc.height = 800

        qc.config = f"""{{
          type: 'bar',
          data: {{
            labels: {currencies},
            datasets: [
              {{
                label: 'Benchmark Rates',
                data: {bm_rates},
              }}
            ],
          }},
          options: {{
            scales: {{
              yAxes: [{{
                ticks: {{
                  callback: (val) => {{
                    return val.toLocaleString() + '%';
                  }},
                }}
              }}]
            }}
          }},
        }}"""

        self.notifier.notify(title, content, qc.get_url())
