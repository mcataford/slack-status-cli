import unittest.mock
import urllib.parse
import os
import sys
import typing

import slack_status_cli.main


class MockResponse(typing.NamedTuple):
    """
    Stand-in for http.client.HTTPResponse.
    """

    status: int
    response_text: str

    def read(self):
        return self.response_text


def test_errors_if_no_slack_token_provided(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["slack-status-cli", "set", "--text", "test"])

    with unittest.mock.patch("sys.exit", autospec=True) as mock_exit:
        slack_status_cli.main.run()

    mock_exit.assert_called_with(1)


def test_sends_request_to_slack_api_on_success(
    slack_api_token, monkeypatch, snapshot, tmp_path
):
    env = os.environ.copy()
    env["SLACK_TOKEN"] = slack_api_token

    mock_response = MockResponse(status=200, response_text='{ "ok": true }')

    monkeypatch.setenv("SLACK_TOKEN", slack_api_token)
    monkeypatch.setattr(sys, "argv", ["slack-status-cli", "set", "--text", "test"])

    with unittest.mock.patch(
        "urllib.request.urlopen",
        autospec=True,
        return_value=mock_response,
    ) as mock_request, unittest.mock.patch(
        "pathlib.Path.home", autospec=True, return_value=tmp_path
    ):
        slack_status_cli.main.run()

    request = mock_request.call_args_list[0][0][0]

    assert request.get_full_url() == "https://slack.com/api/users.profile.set"
    assert request.get_method() == "POST"
    assert request.get_header("Authorization") == "Bearer %s" % slack_api_token

    request_body = urllib.parse.parse_qs(request.data.decode())

    assert request_body == snapshot
