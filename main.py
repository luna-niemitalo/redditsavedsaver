import sys
from pathlib import Path
from api_manager import authenticate
from file_manager import SaveFileManager, verify_dirs, verify_config
from download_manager import download_saved_items
from utils import log, check_version, load_config

current_folder = Path('.')

def main():
    # Load the configuration
    config_path = current_folder / 'data' / 'config.json'
    config = load_config(config_path)

    # Verify and set up directories
    if not verify_dirs(current_folder / 'data'):
        log("Directory verification failed, exiting...")
        sys.exit(1)

    if not verify_config(config_path):
        log("Config verification failed, exiting...")
        sys.exit(1)

    # Authenticate and get the access token
    token = authenticate(config)

    # Load saved items and proceed to download them
    save_manager = SaveFileManager(current_folder / 'data' / 'save.json')
    downloaded_items = save_manager.get_save_obj()

    # Download the saved Reddit posts
    download_saved_items(token, config, downloaded_items, save_manager)

if __name__ == "__main__":
    main()
