"""
Fixes the version of pyproject.toml, for use before the package
artifacts are built.
"""

import sys
import toml


def set_version(new_version: str):
    with open("./pyproject.toml", "r", encoding="utf8") as pyproject:
        project_config = toml.loads(pyproject.read())
        project_config["project"]["version"] = new_version

        print("Bumped version to %s" % new_version)

    with open("./pyproject.toml", "w", encoding="utf8") as pyproject:
        toml.dump(project_config, pyproject)


set_version(sys.argv[1])
