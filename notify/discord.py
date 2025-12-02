import requests
from typing import Any, Dict
from time import sleep


class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def notify(self, title: str, content: str, message: str):
        # 將 payload 定義為一個變數並提供明確的類型提示
        # 以解決 Pylance 的 "partially unknown" 錯誤
        payload: Dict[str, Any] = {
            "content": content,
            # "embeds": [
            #     {
            #         "title": "Hello, Embed!",
            #         "description": "This is an embedded message.",
            #     }
            # ],
            "thread_name": title,
        }

        rsp = requests.post(self.webhook_url, json=payload)

        thread_id = rsp.json()["id"]

        rsp = requests.post(
            self.webhook_url + "&thread_id=" + thread_id,
            json={"content": message},
        )

        print(f"discord notify: {rsp.text}")

    def thread_notify(self, title: str, content: str, thread_messages: list[Any]):
        payload: Dict[str, Any] = {
            "content": content,
            "thread_name": title,
        }

        topicResposne = requests.post(self.webhook_url, json=payload)
        thread_id = topicResposne.json()["id"]

        for message in thread_messages:
            threadResponse = requests.post(
                self.webhook_url + "&thread_id=" + thread_id,
                json={"content": str(message)},
            )
            # slow down to avoid triggering rate limit ban
            sleep(2)

            print(f"discord notify: {threadResponse.text}")
