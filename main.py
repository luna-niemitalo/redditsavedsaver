#!/usr/bin/env python3
import mimetypes
import time
import requests
import requests.auth
import json
import os
import sys
import sqlite3
import random
from sqlite3 import Error
from datetime import datetime
from inspect import currentframe, getframeinfo
from pathlib import Path

debug = False
version = 1
needsUpgrade = False
token = ""
config = {}
currentFolder = Path('.')
customAfter = False
useTarget = False
targetFolder = Path('.')
after = ""
getMultiple = False


def get_linenumber():
    cf = currentframe()
    return "Line: " + str(cf.f_back.f_lineno) + " "


def log(string):
    file = open(currentFolder / 'data'/'log.txt', "a+")
    file.write(string + "\n")
    file.close()


def main():
    client_auth = requests.auth.HTTPBasicAuth(
        config["HTTPBasicAuth1"], config["HTTPBasicAuth2"])
    post_data = {"grant_type": "password",
                 "username": config["username"], "password": config["password"]}
    headers = {"User-Agent": config["User-Agent"]}
    response = requests.post("https://www.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             data=post_data,
                             headers=headers)
    global token
    token = response.json()["access_token"]


def getExample():
    headers = {"Authorization": "bearer " + token,
               "User-Agent": config["User-Agent"]}
    response = requests.get(
        "https://oauth.reddit.com/api/v1/me", headers=headers)
    print(response)


def getSavedGenerator():
    global after
    while after is not None:
        headers = {"Authorization": "bearer " + token, "User-Agent": config["User-Agent"]}
        request = "https://oauth.reddit.com/user/"
        request += config["username"]
        request += "/saved?count="
        request += str(config["count"])
        if after is not None:
            request += str("&after=" + after)
        request += "&sort=new"
        response = requests.get(request, headers=headers)
        json = response.json()
        filtered = filterSaved(json)
        if getMultiple:
            after = json["data"]["after"]
            yield filtered
        else:
            if customAfter:
                print(json["data"]["after"])
            after = None
            yield filtered

def filterSaved(saved_items):
    result = []
    for item in saved_items["data"]["children"]:
        #if debug:
            #log(get_linenumber() + json.dumps(item))
        image_obj = {
            "id": item["data"]["id"],
            "url": item["data"]["url"],
            "permalink": item["data"]["permalink"],
            "ts": item["data"]["created_utc"],
            "nsfw": item["data"]["over_18"],
            "title": item["data"]["title"],
            "subreddit": item["data"]["subreddit"],

        }
        image_obj["is_gallery"] = False
        if "is_gallery" in item["data"]:
            image_obj["url"] = ""
            image_obj["is_gallery"] = True


            image_obj["sub_items"] = getGallery(item["data"])

        result.append(image_obj)
    return result

def getGallery(submission):
    subItems = {}
    count = 0
    try:
        for item in sorted(submission["gallery_data"]['items'], key=lambda x: x['id']):
            count += 1
            media_id = item['media_id']
            meta = submission["media_metadata"][media_id]
            if meta['e'] == 'Image':
                source = meta['s']
                url = source['u']
                parsed_url = url.replace('amp;', '')
                subItem = {}
                subItem["url"] = parsed_url
                subItem["index"] = count
                subItem["id"] = media_id
                subItems[media_id] = subItem
    except:
        log(get_linenumber() + "Error downloading gallery" + submission['id'])
    return subItems

# Manager for file operations, openin, reading, writing and closing files.
class SaveFileManager:
    # Initialize save object into memory as empty,
    # and save filep path to the save file manager
    def __init__(self, filePath: Path):
        self.save_object = {}
        self.file_path = filePath
        if debug:
            log(get_linenumber() + "currentFolder: " + currentFolder.as_posix() +
                " | filePath: " + self.file_path.as_posix())

    # Load file to the initialized object from the file path
    def getSaveObj(self):
        try:
            path = currentFolder / self.file_path
            if debug:
                log(get_linenumber() + "currentFolder: " + currentFolder.as_posix() +
                    " | filePath: " + self.file_path.as_posix())
                if path.is_file():
                    log(get_linenumber() + "'" +
                        self.file_path.as_posix() + "' is a file")
                else:
                    log(get_linenumber() + "'" +
                        self.file_path.as_posix() + "' is not a file")
            fp = open(currentFolder / self.file_path)
            result = fp.read()
            save_data = json.loads(result)
            self.save_object = save_data
            fp.close()
        except Exception as e:
            log(get_linenumber() + "No file, or empty file: " + str(e))
        return self.save_object

    # Save the save object to the file path
    def setSaveObj(self, save_object = None):
        fp = open(currentFolder / self.file_path, "w+")
        if save_object is None:
            json_string = json.dumps(self.save_object)
        else:
            json_string = json.dumps(save_object)
        fp.write(json_string)
        fp.close()

    # Push array of items to the save object
    def pushArrToSaved(self, filtered_items):
        for item in filtered_items:
            self.save_object[item["id"]] = item

    #Push item to the save object
    def pushObjToSaved(self, name, obj):
        self.save_object[name] = obj


def verify(folder: Path):
    try:
        test_file = folder / "verify"
        f = open(test_file, "w+")
        f.close()
        os.remove(test_file)
        return True
    except Exception as e:
        log(get_linenumber() + "Failed to write to test file in " + folder.as_posix())
        log(get_linenumber() + "Error: " + str(e))
        return False


def downloadItem(item, existings={}):
    global targetFolder
    if useTarget:
        targetFolder = targetFolder
    else:
        targetFolder = currentFolder

    if item["id"] not in existings:
        if debug:
            log(get_linenumber() + "Not in existing, trying to download...")
        log(get_linenumber() + "Downloading " + item["id"])
        try:
            if item["is_gallery"]:
                return handleGalleryItem(item)
            else:
                return handleNormalItem(item)
        except Exception as e:
            log(get_linenumber() + "Error downloading " + item["id"] + ": " + str(e))
            item["has_errors"] = True
            item["errors"] = [str(e)]
            return item
    else:
        if needsUpgrade:
            if debug:
                log(get_linenumber() + "Allready downloaded, but needs upgrade, upgrading " + item["id"] + "...")
            if item["is_gallery"]:
                return upgradeGallery(item)
            else:
                return upgradeNormalItem(item)

def fillDataWithoutExtension(item):
    item["has_errors"] = True
    path = targetFolder / "savedImages"
    for image in path.iterdir():
        if item["id"] in image.name:
            target = path / image.name
            if target.is_file():
                if debug:
                    log(get_linenumber() + "Setting path to: " + target.as_posix())
                item["path"] = target.as_posix()

def upgradeNormalItem(item):
    extension = ""
    r = requests.get(item["url"], allow_redirects=True)
    if (r.status_code != 200):
        log(get_linenumber() + "Error downloading " + item["id"])
        log(get_linenumber() + "Status Code: " + str(r.status_code))
        log(get_linenumber() + "Message: " + r.reason)
        item["deleted_source"] = True
        fillDataWithoutExtension(item)
    else:
        extension = mimetypes.guess_extension(r.headers["content-type"])
        if not extension:
            fillDataWithoutExtension(item)
        else:
            target = targetFolder / "savedImages" / str(item["id"] + str(extension))
            if debug:
                log(get_linenumber() + "Setting path to: " + target.as_posix())
            item["path"] = target.as_posix()
            if not target.is_file():
                file = open(target, 'wb')
                file.write(r.content)
                file.close()
                log(target.as_posix() + " Created while upgrading...")
    return item


def handleNormalItem(item):
    r = requests.get(item["url"], allow_redirects=True)
    extension = mimetypes.guess_extension(r.headers["content-type"])
    if not extension:
        log(get_linenumber() + "NO EXTENSION DETECTED!!")
        log(get_linenumber() + r.json())
        item["has_errors"] = True
        return item
    target = targetFolder / "savedImages" / str(item["id"] + extension)
    if target.exists():
        item["path"] = target.as_posix()
        log(target.as_posix() + " Already exists...")
        return item
    file = open(target, 'wb')
    file.write(r.content)
    file.close()
    log(target.as_posix() + " Created...")
    return item

def upgradeGallery(gitem):
    if "sub_items" not in gitem:
        log(get_linenumber() + "Gallery deleted, nothing to do...")
        gitem["deleted_source"] = True
        gitem["has_errors"] = True
        return gitem
    for key in gitem["sub_items"]:
        item = gitem["sub_items"][key]
        url = item["url"]
        r = requests.get(url, allow_redirects=True)
        if r.status_code != 200:
            item["has_errors"] = True
            item["deleted_source"] = True
            continue

        extension = mimetypes.guess_extension(r.headers["content-type"])
        if not extension:
            item["has_errors"] = True
            continue

        target = targetFolder / "savedImages" / str(key + extension)
        file = open(target, 'wb')
        file.write(r.content)
        file.close()
        item["path"] = target.as_posix()
        log(target.as_posix() + " Gallery updated...")

    return gitem

def handleGalleryItem(gitem):
    for key in gitem["sub_items"]:
        item = gitem["sub_items"][key]
        url = item["url"]
        r = requests.get(url, allow_redirects=True)
        extension = mimetypes.guess_extension(r.headers["content-type"])
        if not extension:
            log(get_linenumber() + "NO EXTENSION DETECTED!!")
            log(get_linenumber() + "Status code: " + str(r.status_code))
            log(get_linenumber() + "Reason: " + str(r.reason))
            log(get_linenumber() + "Url: " + str(r.url))
            item["has_errors"] = True
            continue
        target = targetFolder / "savedImages" / str(key + extension)
        file = open(target, 'wb')
        file.write(r.content)
        file.close()
        item["path"] = target.as_posix()
        log(target.as_posix() + " Created...")
    return gitem

def createPath(path: Path):
    # define the access rights
    access_rights = 0o755

    try:
        os.makedirs(path, access_rights)
    except OSError:

        log(get_linenumber() + "Creation of the directory %s failed" %
            path.as_posix())
        return False
    else:
        log(get_linenumber() + "Successfully created the directory %s" %
            path.as_posix())
        if verifyDirs(path, True):
            return True
        else:
            return False


def verifyDirs(path: Path, recursing: bool = False):
    verifyPath = path
    # If file exists, return true
    if verifyPath.is_dir():
        if debug:
            log(get_linenumber() + "Target folder " + path.as_posix() + " exists")
        return verify(path)
    # If path exists but is not dir return false
    elif verifyPath.exists():
        log("Target " + path.name + " exists but is not a directory")
        return False
    # If not, try to create it, and try to verify again
    else:
        # If we are not recursing try to create a file, and try to verify it
        if not recursing:
            return createPath(path)
        # If we are recusing and it's still not a file, just return falce because we are failing at creation
        else:
            log(get_linenumber() + "Recursion error, creating file probably failed...")
            return False


def verifyFile(path: Path, recursing=False):
    if (path.is_file()):
        return True
    elif recursing:
        return False
    else:
        open(path, "w+").close()
        return verifyFile(path, True)


def verifyConfig(path: Path, recursing=False):
    configDefault = path.parents[0] / "config_default.json"

    if (configDefault.is_file()):
        return True
    if (path.is_file()):
        return True
    elif recursing:
        return False
    else:
        file = open(path, "w+")
        file.write(getInitialConfig())
        file.close()
        path.rename(configDefault)
        return verifyConfig(path, True)


# Get initial configuration
def getInitialConfig():
    return """{
	"username": "<username>",
	"password": "CorrectHorseBatteryStaple",
	"User-Agent": "Example user agent by <username>",
	"HTTPBasicAuth1": "",
	"HTTPBasicAuth2": "",
	"path": "",
	"count": 25,
	"debug": false,
    "version": 1
}"""


def getTarget():
    global useTarget
    global targetFolder
    if 'target_path' not in config:
        return "Config has no parameter 'target_path'"
    if debug:
        log(get_linenumber() + 'target_path is "' +
            str(config["target_path"]) + '"')
    if not config["target_path"]:
        return "Target path is empty, not using target path"
    targetFolder = Path(config["target_path"])
    if not targetFolder.is_dir():
        return "Target path not a directory"
    if debug:
        log(get_linenumber() + "target_path is a directory")
        log(get_linenumber() + "Use target = true")
    useTarget = True
    return ""

def getUpgradeConfig():
    log(get_linenumber() + "Upgrading configuration...")
    initialConfig = getInitialConfig()
    inConfObj = json.loads(initialConfig)
    for key in inConfObj:
        if key not in config:
            config[key] = inConfObj[key]

def checkVersion():
    global needsUpgrade
    if "version" not in config or config["version"] < version:
        confVersion = 0
        if "version" in config:
            confVersion = config["version"]
        log(get_linenumber() + "Version mismatch... Upgrading file versions... " + str(confVersion) + " --> " + str(version))
        log(get_linenumber() + "Expect bugs or data loss")
        needsUpgrade = True

if __name__ == "__main__":
    # Verify that data directory exists
    vdErr = verifyDirs(currentFolder / 'data')
    # Verify that config file exists and if not, create it
    vcErr = verifyConfig(currentFolder / 'data' / 'config.json')

    # If data dir does not exist,
    # or config file does not exist or can not be created,
    # exit, because this is a fatal error
    if not vdErr:
        log("VerifyDirs failed...")
        exit()
    if not vcErr:
        log("VerifyConfig failed...")
        exit()

    log("[" + str(datetime.now()) + "] Running script...")

    confManager = SaveFileManager(Path("./data/config.json"))
    config = confManager.getSaveObj()
    checkVersion()
    if needsUpgrade:
        getMultiple = True
        getUpgradeConfig()
        confManager.setSaveObj(config)


    if 'debug' in config and config['debug'] == True:
        debug = True
        log(get_linenumber() + "Debug enabled: " + str(debug))

    tarErr = getTarget()
    if tarErr and debug:
        log(get_linenumber() + tarErr)
    verifyFile(Path("./data/save.json"))
    SFM = SaveFileManager(Path("./data/save.json"))
    downloaded_items = SFM.getSaveObj()
    verifyDirs(targetFolder / "savedImages")

    main()
    count = 0
    if len(sys.argv) >= 2:
        if debug:
            log(get_linenumber() + "More than 1 argv")
        if sys.argv[1] == "1":
            log(get_linenumber() + "Getting multiple...")
            getMultiple = True
        elif sys.argv[1] == '2':
            print("customAfter")
            customAfter = True
            after = sys.argv[2]
        else:
            log(get_linenumber() + "Invalid parameter: " + sys.argv[1])

    loop = 0
    for filtered_items in getSavedGenerator():
        if debug:
            loop += 1
            log(get_linenumber() + "Page: " + str(loop))
        for fitem in filtered_items:
            result = downloadItem(fitem, downloaded_items)
            if result:
                SFM.pushObjToSaved(result["id"], result)
                count += 1
        SFM.setSaveObj()
        time.sleep(1)
    log("Downloaded " + str(count) + " items...")
