import json
from pathlib import Path
from logger import log

class ConfigManager:
    def __init__(self, config_path: Path):
        """
        Initialize the ConfigManager with the path to the configuration file.

        Parameters:
        - config_path (Path): The path to the configuration file.
        """
        self.config_path = config_path
        self._config = None

    def _load_config(self):
        """Lazy-load the configuration from a file."""
        if self._config is None:
            try:
                with open(self.config_path, "r") as file:
                    self._config = json.load(file)
                log("Configuration loaded successfully.")
            except Exception as e:
                log(f"Error loading config: {str(e)}")
                self._config = {}  # If the file doesn't exist, initialize an empty config.
                self._save_config()

    def _save_config(self):
        """Save the configuration to the file."""
        try:
            with open(self.config_path, "w") as file:
                json.dump(self._config, file, indent=4)
            log("Configuration saved successfully.")
        except Exception as e:
            log(f"Error saving config: {str(e)}")
            raise

    # Individual properties for each config item
    @property
    def username(self):
        self._load_config()
        return self._config.get("username", "")

    @username.setter
    def username(self, value):
        self._load_config()
        self._config["username"] = value
        self._save_config()

    @property
    def password(self):
        self._load_config()
        return self._config.get("password", "")

    @password.setter
    def password(self, value):
        self._load_config()
        self._config["password"] = value
        self._save_config()

    @property
    def user_agent(self):
        self._load_config()
        return self._config.get("User-Agent", "")

    @user_agent.setter
    def user_agent(self, value):
        self._load_config()
        self._config["User-Agent"] = value
        self._save_config()

    @property
    def http_basic_auth1(self):
        self._load_config()
        return self._config.get("HTTPBasicAuth1", "")

    @http_basic_auth1.setter
    def http_basic_auth1(self, value):
        self._load_config()
        self._config["HTTPBasicAuth1"] = value
        self._save_config()

    @property
    def http_basic_auth2(self):
        self._load_config()
        return self._config.get("HTTPBasicAuth2", "")

    @http_basic_auth2.setter
    def http_basic_auth2(self, value):
        self._load_config()
        self._config["HTTPBasicAuth2"] = value
        self._save_config()

    @property
    def count(self):
        self._load_config()
        return self._config.get("count", 5)

    @count.setter
    def count(self, value):
        self._load_config()
        self._config["count"] = value
        self._save_config()

    @property
    def token(self):
        self._load_config()
        return self._config.get("token", "")

    @token.setter
    def token(self, value):
        self._load_config()
        self._config["token"] = value
        self._save_config()

    @property
    def db_path(self):
        self._load_config()
        return self._config.get("db_path", "")

    @db_path.setter
    def db_path(self, value):
        self._load_config()
        self._config["db_path"] = value
        self._save_config()

    @property
    def expiration_ts(self):
        self._load_config()
        return self._config.get("expiration_ts", "")

    @expiration_ts.setter
    def expiration_ts(self, value):
        self._load_config()
        self._config["expiration_ts"] = value
        self._save_config()

    @property
    def target_path(self):
        self._load_config()
        return self._config.get("target_path", "./savedImages")

    @target_path.setter
    def target_path(self, value):
        self._load_config()
        self._config["target_path"] = value
        self._save_config()

    @property
    def debug(self):
        self._load_config()
        return self._config.get("debug", False)

    @debug.setter
    def debug(self, value):
        self._load_config()
        self._config["debug"] = value
        self._save_config()

    @property
    def version(self):
        self._load_config()
        return self._config.get("version", 1)

    @version.setter
    def version(self, value):
        self._load_config()
        self._config["version"] = value
        self._save_config()

    def check_and_upgrade_config(self, version=1):
        """
        Check and upgrade the configuration if necessary.

        Parameters:
        - version (int): The current version of the configuration structure.

        Returns:
        - (bool): Whether the configuration was upgraded.
        """
        self._load_config()
        if "version" not in self._config or self._config["version"] < version:
            log(f"Config version mismatch... Upgrading version {self._config.get('version', 0)} -> {version}")
            self._config["version"] = version
            self._config.setdefault("count", 25)
            self._config.setdefault("debug", False)
            self._save_config()
            return True
        return False

    def __str__(self):
        """Convert the configuration manager to a string for easy printing."""
        self._load_config()
        return json.dumps(self._config, indent=4)
