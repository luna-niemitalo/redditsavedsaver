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

token = ""
currentFolder = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
useTarget = False
targetFolder = ""


def get_linenumber():
    cf = currentframe()
    return "Line: " + str(cf.f_back.f_lineno) + " "


def log(string):
    file = open(currentFolder + "/data/log.txt", "a+")
    file.write(string + "\n")
    file.close()


def main(config):
    client_auth = requests.auth.HTTPBasicAuth(config["HTTPBasicAuth1"], config["HTTPBasicAuth2"])
    post_data = {"grant_type": "password", "username": config["username"], "password": config["password"]}
    headers = {"User-Agent": config["User-Agent"]}
    response = requests.post("https://www.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             data=post_data,
                             headers=headers)
    global token
    token = response.json()["access_token"]


def getExample():
    headers = {"Authorization": "bearer " + token,
               "User-Agent": "Test custom user agent by ***REMOVED***"}
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    print(response)


def getSaved():
    headers = {"Authorization": "bearer " + token,
               "User-Agent": "Test custom user agent by ***REMOVED***"}
    response = requests.get("https://oauth.reddit.com/user/***REMOVED***/saved" + "?count=25&sort=new",
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
                   "User-Agent": "Test custom user agent by ***REMOVED***"}
        response = requests.get("https://oauth.reddit.com/user/***REMOVED***/saved" + "?count=25&after=" + after, headers=headers)
        response.json()
        after = response.json()["data"]["after"]
        filtered = filterSaved(response.json())
        for fitem in filtered:
            results.append(fitem)
    return results

def filterSaved(saved_items):
    result = []
    for item in saved_items["data"]["children"]:
        #try: 
            #if item["data"]["is_gallery"] == "true":
                #log(get_linenumber() + json.dumps(item))
        #finally:
        image_obj = {
            "id": item["data"]["id"],
            "url": item["data"]["url"],
            "permalink": item["data"]["permalink"],
            "ts": item["data"]["created_utc"],
        }
        result.append(image_obj)
    return result

class SaveFileManager:
    def __init__(self, filePath):
        self.save_object = {}
        self.file_path = filePath

    def getSaveObj(self):
        try:
            fp = open(currentFolder + self.file_path)
            result = fp.read()
            save_data = json.loads(result)
            self.save_object = save_data
            fp.close()
        except:
            print("No file, or empty file")
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


def createFileDirs(config):
    if useTarget:
        target_folder = targetFolder
    else:
        target_folder = currentFolder
    if verify(target_folder):
        return True

    # define the name of the directory to be created,
    path = target_folder + "/savedImages"
    path2 = currentFolder + "/data"

    # define the access rights
    access_rights = 0o755

    try:
        os.makedirs(path, access_rights)
    except OSError:

        log(get_linenumber() + "Creation of the directory %s failed" % path)
        return False
    else:
        log(get_linenumber() + "Successfully created the directory %s" % path)
        if not verify(target_folder):
            return False

    try:
        os.mkdir(path2, access_rights)
    except OSError:
        log(get_linenumber() + "Creation of the directory %s failed" % path2)
    else:
        log(get_linenumber() + "Successfully created the directory %s" % path2)

    if verify(target_folder):
        return True
    return False


def downloadItem(item, existings={}):
    if useTarget:
        target_folder = targetFolder
    else:
        target_folder = currentFolder

    if item["id"] not in existings:
        log("Downloading " + item["id"])
        try:
            r = requests.get(item["url"], allow_redirects=True)
            extension = mimetypes.guess_extension(r.headers["content-type"])
            if not extension:
                log(get_linenumber() + "NO EXTENSION DETECTED!!")
                log(get_linenumber() + r.json())
                return False
            file = open(target_folder + "/savedImages/" + item["id"] + extension, 'wb')
            file.write(r.content)
            file.close()
            log(target_folder + "/savedImages/" + item["id"] + extension + " Created...")
            return item
        except Exception as e:
            log(str(e))
            log(get_linenumber() + "Error downloading " + item["id"])
            return False

def firstRun(SFM):
    try:
        open(currentFolder + "/data/verify").close()
    except:
        open(currentFolder + "/data/verify", "x")


if __name__ == "__main__":
    log("[" + str(datetime.now()) + "] Running script...")
    SFM = SaveFileManager("/data/save.json")
    downloaded_items = SFM.getSaveObj()
    confManager = SaveFileManager("/data/config.json")
    config = confManager.getSaveObj()
    if 'path' in config:
        if config["path"].endswith('/'):
            config["path"] = config["path"][:-1]

        if config["path"]:
            useTarget = True
            targetFolder = config["path"]

    # execute only if run as a script
    if not createFileDirs(config):
        exit(1)
    main(config)
    firstRun(SFM)
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
