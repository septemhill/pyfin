from typing import Dict
from requests import Response
import requests
import json


class DiscordBot:
    def __init__(self, host: str, token: str, guild_id: str):
        self.host = host
        self.token = token
        self.guild_id = guild_id

    def __send_request(self, url: str) -> Response:
        headers: Dict[str, str] = {"Authorization": "Bot " + self.token}
        return requests.get(url, headers=headers)

    def getGuild(self):
        rsp = self.__send_request(self.host + "/guilds/" + self.guild_id)
        print(json.dumps(rsp.json()))
        return

    def getGuildChannels(self):
        rsp = self.__send_request(self.host + "/guilds/" + self.guild_id + "/channels")
        print(json.dumps(rsp.json()))
        return
