from time import sleep
from typing import Dict, Any
import os
from dataclasses import dataclass, fields, MISSING

from scrap import (
    ib_margin_rate,
    ib_ref_bm_rate,
    # ib_spot_cur_comission,
    qqq_holdings,
    voo_holdings,
)
from notify.discord import DiscordNotifier
from interfaces import Notifier, Scraper

import requests


@dataclass
class Config:
    """用來存放從環境變數讀取的設定"""

    discord_bot_token: str
    discord_ib_notify_channel_id: str
    discord_client_id: str
    discord_client_secret: str
    discord_guild_id: str
    # optional_field: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        """從環境變數讀取設定，並動態建立 Config 實例"""
        missing_vars: list[str] = []
        config_values: dict[str, Any] = {}
        for field in fields(cls):
            env_var = field.name.upper()
            value = os.getenv(env_var)

            # 如果環境變數不存在
            if value is None:
                # 檢查此欄位是否有預設值 (也就是選填)
                if field.default is MISSING:
                    missing_vars.append(env_var)
            config_values[field.name] = value or field.default
        if missing_vars:
            raise ValueError(f"缺少必要的環境變數，請設定: {', '.join(missing_vars)}")
        return cls(**config_values)


def main():
    config = Config.from_env()
    headers: Dict[str, str] = {"Authorization": "Bot " + config.discord_bot_token}

    rsp = requests.get(
        f"https://discord.com/api/channels/{config.discord_ib_notify_channel_id}/webhooks",
        headers=headers,
    )

    notiWebhookUrl = rsp.json()[0]["url"]

    notifier: Notifier = DiscordNotifier(webhook_url=notiWebhookUrl + "?wait=true")

    scripts: list[Scraper] = [
        #        ib_spot_cur_comission.IBSpotCurrencyCommissionScraper(notifier=notifier),
        ib_margin_rate.IBMarginRateScraper(notifier=notifier),
        ib_ref_bm_rate.IBReferenceBenchmarkRateScraper(notifier=notifier),
        qqq_holdings.QQQHoldingsScraper(notifier=notifier),
        voo_holdings.VOOHoldingsScraper(notifier=notifier),
    ]

    for script in scripts:
        # 減慢請求速度以避免觸發速率限制
        sleep(3)
        script.scrap()


if __name__ == "__main__":
    main()
