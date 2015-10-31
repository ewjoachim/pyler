import json
import os

from .utils import AutomaticMixin


class Config(AutomaticMixin):

    @property
    def config_file(self):
        return os.environ.get("PYLER_CONF", ".pyler.conf")

    def get_config(self):
        try:
            with open(self.config_file, "r") as handler:
                if not handler.read():
                    raise ValueError()
                handler.seek(0)
                config = json.load(handler)
        except (IOError, ValueError):
            config = self.get_default_config()
            self.save_config(config)

        return config

    def get_default_config(self):
        return {
            "credentials": {
                "username": None,
                "password": None,
            },
            "session": None,
        }

    def write_elements(self, **kwargs):
        config = self.get_config()
        config.update(kwargs)
        self.save_config(config)

    def save_config(self, config):
        with open(self.config_file, "w") as handler:
            json.dump(config, handler)

    def get_or_ask_for_credentials(self):
        config = self.get_config()
        credentials = config["credentials"]
        order = ["username", "password"]

        if all(credentials.values()):
            return credentials

        for key in order:
            if not credentials[key]:
                credentials[key] = self.input("Project Euler {key} ?".format(key=key))

        self.write_elements(credentials=credentials)

        return credentials
