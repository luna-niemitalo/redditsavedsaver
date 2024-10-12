import json
from pathlib import Path
from logger import log

class SaveFileManager:
    def __init__(self, file_path: Path):
        self.save_object = {}
        self.file_path = file_path
        self.load_file()

    def load_file(self):
        """Load the save object from the file path."""
        try:
            with open(self.file_path, "r") as fp:
                self.save_object = json.load(fp)
        except Exception as e:
            log(f"Error loading save file: {str(e)}")

    def getSaveObj(self):
        """Return the saved object."""
        return self.save_object

    def setSaveObj(self):
        """Save the current state of the save object to the file."""
        try:
            with open(self.file_path, "w+") as fp:
                json.dump(self.save_object, fp, indent=4)
        except Exception as e:
            log(f"Error saving object: {str(e)}")

    def pushObjToSaved(self, name, obj):
        """Push an item to the saved object."""
        self.save_object[name] = obj
