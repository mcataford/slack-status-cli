# slack-status-cli
:sparkle: Tooling to set your Slack status on the fly without having to click around

[![CICD](https://github.com/mcataford/slack-status-cli/actions/workflows/main.yml/badge.svg)](https://github.com/mcataford/slack-status-cli/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/mcataford/slack-status-cli/branch/main/graph/badge.svg?token=10VP1ZDBHR)](https://codecov.io/gh/mcataford/slack-status-cli)
[![python-support](https://img.shields.io/badge/python-%5E3.7-brightgreen)]()

## Overview

Clicking around Slack to update statuses is not only annoying, but if you use statuses as part of your remote workflow
to broadcast what you are up to when jumping into new things, you quickly find yourself spending minutes of you day
clicking around and setting the same statuses over and over again since the UI isn't great at remembering them.

Enter `slack-status-cli`. With it, you can set statuses (with or without expiration dates) without leaving the terminal.
More importantly, you can also set presets and defaults to save time on statuses you reuse all the time.

## Configuration

You can use `slack-status-cli` without a configuration file and provide everything via arguments (see `slack-status-cli
-h` for the list of flags you can pass in), or set up a file under `~/.config/slack-status-cli` that follows the format:

```json
{
    "presets": {
        "pairing": { "text": "Pairing", "icon": ":pear:" }
    },
    "defaults": { "duration": "1h", "icon": ":calendar:" }
}
```

`presets` allows you to set up a map of labels (used to select the preset) to values (defining the status text, icon and
duration), `defaults` allows you to set up sane defaults used in all statuses if the specified fields are not provided
(in the above, all statuses would have a duration of one hour if not specified, and a default :calendar: icon -- presets
and/or CLI args will override these defaults if given).

## Installation

You can clone this repository and build from source. This project uses `poetry`, as such `poetry build` will prepare a
Wheel that you can install directly.
