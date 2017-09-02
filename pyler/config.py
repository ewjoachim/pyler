import json
import os

from . import utils


class Config():

    def __getitem__(self, name):
        try:
            return self.get_config()[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        return self.write_elements(**{name: value})

    @property
    def config_file(self):
        def ok_path(path):
            return path and os.path.exists(path)

        return next(filter(ok_path, [
            os.environ.get("PYLER_CONF"),
            os.path.expanduser(os.path.join("~", ".pyler.conf")),
            ".pyler.conf",
        ]), ".pyler.conf")

    def get_config(self):
        try:
            with open(self.config_file, "r") as handler:
                config = json.load(handler)
        except (IOError, ValueError):
            config = {}

        return config

    def write_elements(self, **kwargs):
        config = self.get_config()
        config.update(kwargs)
        self.save_config(config)

    def save_config(self, config):
        with open(self.config_file, "w") as handler:
            json.dump(config, handler)

    def get_or_ask_for_credentials(self):
        credentials = self["credentials"] or {}
        order = ["username", "password"]

        if credentials and all(credentials.get(key) for key in order):
            return credentials

        for key in order:
            if not credentials.get(key):
                credentials[key] = utils.user_input(
                    "Project Euler {key}? ".format(key=key))

        self["credentials"] = credentials

        return credentials
