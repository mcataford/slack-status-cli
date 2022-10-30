import urllib.request
import urllib.parse
import typing
import json
import os

import logger as log

logger = log.get_logger(__name__)


class SlackClient:
    _token: str

    def __init__(self, token: str):
        self._token = token

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self._token}",
        }

    def _post(self, url: str, payload):
        request = urllib.request.Request(
            url,
            urllib.parse.urlencode(payload).encode(),
            method="POST",
            headers=self.headers,
        )

        response = urllib.request.urlopen(request)
        response_status = response.status
        response_data = response.read()

        logger.debug("API request: %s", str(payload))
        logger.debug("API response: %s", str(response_data))

        if response_status != 200:
            raise Exception("Failed due to an API error.")

        response_data = json.loads(response_data)

        if not response_data["ok"]:
            raise Exception("Failed due to an API error.")

    def update_status(
        self,
        status: str,
        emoticon: typing.Optional[str] = None,
        expiration: typing.Optional[int] = None,
    ):
        """
        Sets the Slack status of the given user to <status>, optionally with <emoticon> if provided.
        If an expiration is provided, the status is set to expire after this time.

        Reference: https://api.slack.com/methods/users.profile.set
        """
        payload = {
            "profile": {
                "status_text": status,
                "status_emoji": emoticon or "",
                "status_expiration": expiration or 0,
            }
        }

        self._post("https://slack.com/api/users.profile.set", payload)

    def set_do_not_disturb(self, duration_minutes: int):
        """
        Silences notifications, potentially with the specified duration.

        Reference: https://api.slack.com/methods/dnd.setSnooze
        """
        payload = {"num_minutes": duration_minutes}

        self._post("https://slack.com/api/dnd.setSnooze", payload)
