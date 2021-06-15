#!/usr/bin/env python3
import mimetypes
import time
import requests
import requests.auth
import json
import os
import sys
import sqlite3
from sqlite3 import Error
from datetime import datetime
from inspect import currentframe, getframeinfo
from pathlib import Path

debug = False

token = ""
config = {}
currentFolder = Path('.')
useTarget = False
targetFolder = Path('.')


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


def getSaved():
    headers = {"Authorization": "bearer " + token,
               "User-Agent": config["User-Agent"]}
    response = requests.get("https://oauth.reddit.com/user/" + config["username"] + "/saved" + "?count="+str(config["count"])+"&sort=new",
                            headers=headers)
    filtered = filterSaved(response.json())
    return filtered


def getAllSaved():
    results = []
    after = ""
    log("Getting all saved items...")
    while after is not None:
        time.sleep(1)
        headers = {"Authorization": "bearer " + token,
                   "User-Agent": config["User-Agent"]}
        response = requests.get(
            "https://oauth.reddit.com/user/" + config["username"] + "/saved" + "?count="+str(config["count"])+"&after=" + after, headers=headers)
        response.json()
        after = response.json()["data"]["after"]
        filtered = filterSaved(response.json())
        for fitem in filtered:
            results.append(fitem)
    return results


def filterSaved(saved_items):
    result = []
    for item in saved_items["data"]["children"]:
        # try:
        # if item["data"]["is_gallery"] == "true":
        # log(get_linenumber() + json.dumps(item))
        # finally:
        image_obj = {
            "id": item["data"]["id"],
            "url": item["data"]["url"],
            "permalink": item["data"]["permalink"],
            "ts": item["data"]["created_utc"],
        }
        result.append(image_obj)
    return result


class SaveFileManager:
    def __init__(self, filePath: Path):
        self.save_object = {}
        self.file_path = filePath
        if debug:
            log(get_linenumber() + "currentFolder: " + currentFolder.as_posix() +
                " | filePath: " + self.file_path.as_posix())

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
            if debug:
                log(get_linenumber() + "'" + self.file_path.as_posix() +
                    "' contents: " + json.dumps(result))
            save_data = json.loads(result)
            self.save_object = save_data
            fp.close()
        except:
            log(get_linenumber() + "No file, or empty file")
        return self.save_object

    def setSaveObj(self):
        fp = open(currentFolder + self.file_path, "w+")
        json_string = json.dumps(self.save_object)
        fp.write(json_string)
        fp.close()

    def pushArrToSaved(self, filtered_items):
        for item in filtered_items:
            self.save_object[item["id"]] = item

    def pushObjToSaved(self, name, obj):
        self.save_object[name] = obj


def verify(folder):
    try:
        test_file = folder + "/savedImages/verify"
        f = open(test_file, "w+")
        f.close()
        os.remove(test_file)
        return True
    except:
        return False


def downloadItem(item, existings={}):
    if useTarget:
        target_folder = targetFolder
    else:
        target_folder = currentFolder

    if item["id"] not in existings:
        log(get_linenumber() + "Downloading " + item["id"])
        try:
            r = requests.get(item["url"], allow_redirects=True)
            extension = mimetypes.guess_extension(r.headers["content-type"])
            if not extension:
                log(get_linenumber() + "NO EXTENSION DETECTED!!")
                log(get_linenumber() + r.json())
                return False
            target = target_folder / "savedImages" / str(item["id"] + extension)
            file = open(target, 'wb')
            file.write(r.content)
            file.close()
            log(target.as_posix() + " Created...")
            return item
        except Exception as e:
            log(str(e))
            log(get_linenumber() + "Error downloading " + item["id"])
            return False


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
        return True
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


def getInitialConfig():
    return """{
  "username": "",
  "password": "",
  "User-Agent": "",
  "HTTPBasicAuth1": "",
  "HTTPBasicAuth2": "",
  "path": ""
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


if __name__ == "__main__":
    vdErr = verifyDirs(currentFolder / 'data')
    vcErr = verifyConfig(currentFolder / 'data' / 'config.json')
    if not vdErr:
        log("VerifyDirs failed...")
        exit()
    if not vcErr:
        log("VerifyConfig failed...")

    log("[" + str(datetime.now()) + "] Running script...")

    confManager = SaveFileManager(Path("./data/config.json"))
    config = confManager.getSaveObj()
    if 'debug' in config:
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
    # getExample()
    if len(sys.argv) >= 2:
        if sys.argv[1] == "1":
            filtered_items = getAllSaved()
        else:
            filtered_items = getSaved()
    else:
        filtered_items = getSaved()

    count = 0
    for fitem in filtered_items:
        result = downloadItem(fitem, downloaded_items)
        if result:
            SFM.pushObjToSaved(result["id"], result)
            count += 1
    SFM.pushArrToSaved(filtered_items)
    SFM.setSaveObj()
    log("Downloaded " + str(count) + " items...")
    print("")
