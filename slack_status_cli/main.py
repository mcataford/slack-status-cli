"""
CLI Slack Status Handling

Provides a shortcut to set Slack statuses from the command-line. Since statuses are often
canned, this tool also facilitates setting up presets that can be quickly invoked.

With custom text:

SLACK_TOKEN=XXX slack-status-cli set --text <text> --icon <icon> --duration <duration_description>

With preset:

SLACK_TOKEN=XXX slack-status-cli set --preset <preset-name> --duration <duration_description>
"""

import typing
import os
import logging
import argparse
import datetime
import collections
import re
import json
import pathlib
import sys

import client as slack_client

# Debug mode modifies the log level used for reporting. If truthy,
# extra information is included in each run to diagnose common
# issues.
DEBUG = bool(os.environ.get("DEBUG", False))

# Logger setup
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
log_handler = logging.StreamHandler()
log_handler.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)
log_handler.setFormatter(logging.Formatter(fmt="%(message)s"))
logger.addHandler(log_handler)

ParsedUserInput = collections.namedtuple(
    "ParsedUserInput", ["text", "icon", "duration", "preset", "quiet"]
)

StatusPreset = collections.namedtuple("StatusPreset", ["text", "icon", "quiet"])
Defaults = collections.namedtuple(
    "Defaults",
    [("icon"), ("duration")],
    defaults=[None, None],
)
Configuration = collections.namedtuple(
    "Configuration",
    [
        ("presets"),
        ("defaults"),
    ],
    defaults=[{}, Defaults()],
)


def parse_input(known_presets: typing.List[str]) -> ParsedUserInput:
    """
    Handles command-line argument parsing and help text display.
    """
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    set_parser = subparsers.add_parser("set", help="Set your Slack status")
    set_parser.add_argument("--text", type=str, help="Status text")
    set_parser.add_argument(
        "--icon",
        type=str,
        default=None,
        help="Status icon (as defined by your workspace) in :icon: format",
    )
    set_parser.add_argument(
        "--duration",
        type=str,
        default=None,
        help="Status duration, formatted as AdBhCm (each segment is optional)",
    )
    set_parser.add_argument(
        "--preset", type=str, default=None, choices=known_presets, help="Preset to use"
    )
    set_parser.add_argument(
        "--quiet", type=bool, default=False, help="Silences notifications"
    )
    args = parser.parse_args()

    return ParsedUserInput(
        text=args.text,
        icon=args.icon,
        duration=args.duration,
        preset=args.preset,
        quiet=args.quiet,
    )


def get_expiration(duration_description: typing.Optional[str] = None) -> int:
    """
    Gets an expiration timestamp based on a duration description string of the
    format <int>d<int>h<int>m.
    """

    if not duration_description:
        return 0

    DURATION_PATTERN = (
        r"^((?P<days>[0-9]+)d)?((?P<hours>[0-9]+)h)?((?P<minutes>[0-9]+)m)?$"
    )

    duration_input = re.match(DURATION_PATTERN, duration_description)
    duration_parts = duration_input.groupdict()

    duration = datetime.timedelta(
        days=int(duration_parts.get("days") or 0),
        minutes=int(duration_parts.get("minutes") or 0),
        hours=int(duration_parts.get("hours") or 0),
    )

    return (datetime.datetime.now() + duration).timestamp()


def load_configuration() -> Configuration:
    """
    Loads from configuration file if present.
    """

    configuration_path = pathlib.Path.home().joinpath(".config", "slack-status-cli")

    if not configuration_path.exists():
        return Configuration()

    with open(configuration_path, "r", encoding="utf-8") as config_file:
        config = config_file.read()

    try:
        parsed_config = json.loads(config)

        logger.debug("Loaded configuration: %s", parsed_config)

        preset_config = parsed_config.get("presets", {})
        defaults_config = parsed_config.get("defaults", {})

        presets = {
            preset_key: StatusPreset(
                text=preset_value["text"], icon=preset_value.get("icon")
            )
            for preset_key, preset_value in preset_config.items()
        }

        defaults = Defaults(
            icon=defaults_config.get("icon"), duration=defaults_config.get("duration")
        )

        return Configuration(presets=presets, defaults=defaults)

    except Exception:
        logger.warning("Invalid configuration found at %s", str(configuration_path))
        return Configuration()


def run():
    try:
        configuration = load_configuration()

        args = parse_input(configuration.presets.keys())

        if args.preset and not args.preset in configuration.presets:
            raise Exception("Unknown preset %s" % args.preset)

        token = os.environ.get("SLACK_TOKEN")

        if not token:
            raise Exception("Slack token not provided.")

        client = slack_client.SlackClient(token=token)

        status_text = args.text
        status_icon = args.icon
        status_expiration = get_expiration(
            args.duration or configuration.defaults.duration
        )
        quiet = args.quiet

        if args.preset:
            preset = configuration.presets[args.preset]
            status_text = preset.text
            status_icon = preset.icon

        client.update_status(
            status_text,
            status_icon or configuration.defaults.icon,
            status_expiration,
        )

        if quiet:
            client.set_do_not_disturb(5)

        new_status = (
            "%s %s" % (status_icon, status_text) if status_icon else status_text
        )
        new_expiry = (
            "(expires %s)"
            % datetime.datetime.fromtimestamp(status_expiration).strftime(
                "%A, %B %d, %H:%M"
            )
            if status_expiration
            else "(no expiration)"
        )
        logger.info("✨ Status set to '%s' %s", new_status, new_expiry)
    except Exception as e:
        logger.error("🔥 Could not set status: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    run()
