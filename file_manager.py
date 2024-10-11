import json
from pathlib import Path
from utils import log

class SaveFileManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.save_object = {}

    def get_save_obj(self):
        """Load saved object from file."""
        try:
            with open(self.file_path) as fp:
                self.save_object = json.load(fp)
        except FileNotFoundError:
            log(f"Save file not found: {self.file_path}")
        return self.save_object

    def set_save_obj(self, save_object=None):
        """Save object to file."""
        with open(self.file_path, 'w+') as fp:
            json.dump(save_object or self.save_object, fp)

def verify_dirs(path):
    """Ensure required directories exist."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        log(f"Failed to create directory: {e}")
        return False

def verify_config(path):
    """Verify config file exists."""
    if path.exists():
        return True
    log(f"Config file missing: {path}")
    return False
