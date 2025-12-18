import pandas as pd
from interfaces import Notifier
import requests
import time
from dataclasses import dataclass
from io import StringIO


@dataclass
class SpotCurrencyCommission:
    range: str
    tier: str

    def __str__(self) -> str:
        return f"- Range:`{self.range}`: `{self.tier}`"


class IBSpotCurrencyCommissionScraper:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    def scrap(self):
        response = requests.get(
            "https://www.interactivebrokers.com/en/pricing/commissions-spot-currencies.php"
        )

        title: str = f"{time.strftime('%Y-%m-%d')} [IB] Spot Currency Commissions"
        content: str = time.strftime("%Y-%m-%d")

        tables = pd.read_html(StringIO(response.text))

        comm_table = tables[0]
        comm_table.columns = ["range", "tier"]

        comm_table = comm_table.drop(4)

        commissions: list[SpotCurrencyCommission] = [
            SpotCurrencyCommission(range=row["range"], tier=row["tier"])
            for _, row in comm_table.iterrows()
        ]

        commissions = self.data_cleanup(commissions)

        self.notifier.thread_notify(title, content, commissions)

    def data_cleanup(
        self, data: list[SpotCurrencyCommission]
    ) -> list[SpotCurrencyCommission]:
        cleaned_data: list[SpotCurrencyCommission] = []
        for i, item in enumerate(data):
            new_tier = item.tier
            if i < len(data) - 1:  # Process all but the last item
                # 移除 " 3" 和 " 4"
                new_tier = new_tier.replace(" 3 *", " *").replace(" 4", "")
            else:  # Process the last item
                # 將 Tier I - USD 2.00 Tier II - USD 1.50 ... 拆分為多行
                parts = new_tier.split("  ")
                new_tier = "\n".join(parts)

            cleaned_data.append(SpotCurrencyCommission(range=item.range, tier=new_tier))
        return cleaned_data
