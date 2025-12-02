from interfaces import Notifier
from io import StringIO
from dataclasses import dataclass
from typing import List
import requests
import pandas as pd
import time


@dataclass
class MarginRate:
    tier: str
    pro_rate: str
    lite_rate: str


@dataclass
class GroupedMarginRate:
    currency: str
    tiers: List[MarginRate]

    def __str__(self) -> str:
        tier_details = "\n".join(
            [
                f"- Tier: `{t.tier}`, Pro Rate: `{t.pro_rate}`, Lite Rate: `{t.lite_rate}`"
                for t in self.tiers
            ]
        )
        return f"**{self.currency}**\n{tier_details}"


class IBMarginRateScraper:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    def scrape(self):
        response = requests.get(
            "https://www.interactivebrokers.com/en/trading/margin-rates.php",
        )

        tables = pd.read_html(StringIO(response.text))

        margin_table = tables[1]

        # 重新命名欄位，使其更簡潔易用
        margin_table.columns = [
            "currency",
            "tier",
            "pro_rate",
            "lite_rate",
        ]

        # 使用前一个有效值填充 currency 列中的 NaN 值
        margin_table["currency"] = margin_table["currency"].ffill()

        rates: List[GroupedMarginRate] = []
        # 按 'currency' 分組
        for currency, group in margin_table.groupby("currency"):
            # 為每個分組建立 TierInfo 列表
            tiers_list = [
                MarginRate(
                    tier=row["tier"],
                    pro_rate=row["pro_rate"],
                    lite_rate=row["lite_rate"],
                )
                for _, row in group.iterrows()
            ]
            # 建立 GroupedMarginRate 物件
            rates.append(GroupedMarginRate(currency=currency, tiers=tiers_list))

        title: str = f"{time.strftime('%Y-%m-%d')} [IB] Margin Rates"
        content: str = time.strftime("%Y-%m-%d")

        self.notifier.thread_notify(title, content, rates)
