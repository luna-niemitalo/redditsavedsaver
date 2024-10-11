import json
from log_manager import log


def load_config(config_path):
    """Load configuration from file."""
    with open(config_path) as file:
        return json.load(file)

def check_version(config, current_version):
    """Check if configuration needs upgrade."""
    if config.get('version', 0) < current_version:
        log(f"Upgrading config file version {config['version']} to {current_version}")
        config['version'] = current_version
