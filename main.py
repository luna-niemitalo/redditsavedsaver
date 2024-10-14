import json

from save_manager import SaveFileManager
from reddit_downloader import RedditDownloader
from config_manager import ConfigManager
from logger import log
from pathlib import Path
from datetime import datetime
from utils import download_item

def main():
    # Load the config
    config_path = Path("./data/config.json")
    config_manager = ConfigManager(config_path)

    debug = config_manager.debug

    if debug:
        log("Debug: " + str(config_manager))
    # Check and upgrade the config if needed
    needs_upgrade = config_manager.check_and_upgrade_config()

    # Setup the save file manager
    save_manager = SaveFileManager(Path(config_manager.db_path))
    downloaded_items = save_manager.getSaveObj()

    if debug:
        log(downloaded_items)
    # Initialize Reddit downloader
    reddit_downloader = RedditDownloader(config_manager, downloaded_items)

    # Log script start
    log(f"[{str(datetime.now())}] Running script...")
    # Start downloading
    for filtered_items in reddit_downloader.get_saved_generator():
        if debug:
            log(f"Processing {filtered_items} items...")
        for item in filtered_items:
            if debug:
                log(f"Downloading item: {item}")  # Log the item ID for debugging
            if download_item(item, config_manager.target_path):
                if debug:
                    log(f"Download successful for {item['id']}")
                save_manager.pushObjToSaved(item["id"], item)
                save_manager.setSaveObj()  # Save after each successful download

if __name__ == "__main__":
    main()
