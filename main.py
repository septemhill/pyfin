from typing import Dict
from time import sleep
import os

from scrap import (
    ib_margin_rate,
    ib_ref_bm_rate,
    ib_spot_cur_comission,
    qqq_holdings,
    voo_holdings,
)
from notify.discord import DiscordNotifier
from interfaces import Notifier, Scraper

import requests

botToken = os.getenv("DISCORD_BOT_TOKEN", "")
clientId = os.getenv("DISCORD_CLIENT_ID", "")
clientSecret = os.getenv("DISCORD_CLIENT_SECRET", "")
guildId = os.getenv("DISCORD_GUILD_ID", "")
notificationChannelId = os.getenv("DISCORD_IB_NOTIFY_CHANNEL_ID", "")


def main():
    headers: Dict[str, str] = {"Authorization": "Bot " + botToken}

    # print(
    #     "https://discord.com/api/oauth2/authorize?client_id="
    #     + clientId
    #     + "&permissions=8&scope=bot%20applications.commands"
    # )

    # rsp = requests.get(
    #     "https://discord.com/api/channels/1444985089191575592", headers=headers
    # )
    # print(rsp.text)

    # headers: Dict[str, str] = {"Authorization": "Bot " + botToken}

    # rsp = requests.get(
    #     "https://discord.com/api/channels/1445226039201497219", headers=headers
    # )
    # print(rsp.text)

    rsp = requests.get(
        f"https://discord.com/api/channels/{notificationChannelId}/webhooks",
        headers=headers,
    )

    notiWebhookUrl = rsp.json()[0]["url"]

    notifier: Notifier = DiscordNotifier(webhook_url=notiWebhookUrl + "?wait=true")

    # notifier.notify("hello")

    scripts: list[Scraper] = [
        #        ib_spot_cur_comission.IBSpotCurrencyCommissionScraper(notifier=notifier),
        ib_margin_rate.IBMarginRateScraper(notifier=notifier),
        ib_ref_bm_rate.IBReferenceBenchmarkRateScraper(notifier=notifier),
        qqq_holdings.QQQHoldingsScraper(notifier=notifier),
        voo_holdings.VOOHoldingsScraper(notifier=notifier),
    ]

    for script in scripts:
        # slow down to avoid triggering rate limit ban
        sleep(3)
        script.scrape()


if __name__ == "__main__":
    main()
