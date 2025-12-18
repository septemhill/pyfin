from quickchart import QuickChart
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

    def scrap(self):
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
                percentWeight=float(rate["percentWeight"]),
            )
            for rate in holdings_data
        ]

        newHoldings = self.data_filter(holdings)

        companies = [h.ticker for h in newHoldings]
        percents = [h.percentWeight for h in newHoldings]

        qc = QuickChart()
        qc.width = 1600
        qc.height = 1200
        qc.config = f"""{{
            type: 'doughnut',
            data: {{
                labels: {companies},
                datasets: [
                    {{
                        backgroundColor: [
                            "#a6cee3",
                            "#1f78b4",
                            "#b2df8a",
                            "#33a02c",
                            "#fb9a99",
                            "#e31a1c",
                            "#fdbf6f",
                            "#ff7f00",
                            "#cab2d6",
                            "#6a3d9a",
                            "#ffff99",
                            "#b15928",
                        ],
                        data: {percents}
                    }}
                ]
            }},
            options: {{
                plugins: {{
                    colorschemes: {{scheme: 'brewer.Paired12'}},
                    legend: true,
                    doughnutlabel: {{
                        labels: [
                            [{{
                                font: {{
                                    size: 5
                                }}
                            }}]
                        ]
                    }}
                }}
            }}
        }}"""

        self.notifier.notify(title, content, qc.get_url())

    def data_filter(
        self, holdings: list[Holding], percent_threshold: float = 40.0
    ) -> list[Holding]:
        # 根據 percentWeight 降序排序
        sorted_holdings = sorted(holdings, key=lambda h: h.percentWeight, reverse=True)

        new_holdings: list[Holding] = []
        cumulative_percent = 0.0
        other_holdings: list[Holding] = []

        for holding in sorted_holdings:
            if cumulative_percent < percent_threshold:
                new_holdings.append(holding)
                cumulative_percent += holding.percentWeight
            else:
                other_holdings.append(holding)

        other_weight = sum(h.percentWeight for h in other_holdings)
        new_holdings.append(Holding(ticker="Other", percentWeight=other_weight))

        return new_holdings
