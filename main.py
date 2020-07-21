#!/usr/bin/env python3
import mimetypes

import requests
import requests.auth
import json
import os

token = ""


def main():
    client_auth = requests.auth.HTTPBasicAuth('***REMOVED***', '***REMOVED***')
    post_data = {"grant_type": "password", "username": "***REMOVED***", "password": "***REMOVED***"}
    headers = {"User-Agent": "Test custom user agent by ***REMOVED***"}
    response = requests.post("https://www.reddit.com/api/v1/access_token",
                             auth=client_auth,
                             data=post_data,
                             headers=headers)
    global token
    token = response.json()["access_token"]


def getExample():
    global token
    headers = {"Authorization": "bearer " + token,
               "User-Agent": "Test custom user agent by ***REMOVED***"}
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    print(response)


def getSaved():
    global token
    headers = {"Authorization": "bearer " + token,
               "User-Agent": "Test custom user agent by ***REMOVED***",
               "sort": "new"}
    response = requests.get("https://oauth.reddit.com/user/***REMOVED***/saved", headers=headers)
    return response.json()


def filterSaved(saved_items):
    result = []
    for item in saved_items["data"]["children"]:
        image_obj = {
            "name": item["data"]["name"],
            "url": item["data"]["url"]
        }
        result.append(image_obj)
    return result

class SaveFileManager:
    def __init__(self):
        self.save_object = []
        self.getSaveObj()

    def getSaveObj(self):
        try:
            fp = open("save.json")
            result = fp.read()
            save_data = json.loads(result)
            self.save_object = save_data
            fp.close()
        except:
            print("No file, or empty file")

    def setSaveObj(self):
        fp = open("save.json", "w+")
        json_string = json.dumps(self.save_object)
        fp.write(json_string)
        fp.close()

    def pushArrToSaved(self, filtered_items):
        for item in filtered_items:
            if item not in self.save_object:
                self.save_object.append(item)

    def pushObjToSaved(self, obj):
        if obj not in self.save_object:
            self.save_object.append(obj)

    def getSave(self):
        return self.save_object


def createFileDir():
    # define the name of the directory to be created
    path = "./savedImages"

    # define the access rights
    access_rights = 0o755

    try:
        os.mkdir(path, access_rights)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s" % path)

    try:
        test_file = "./savedImages/verify"
        f = open(test_file, "w+")
        f.close()
        os.remove(test_file)
        return True
    except:
        return False


def downloadItem(item, list):
    if item not in list:
        print("Downloading " + item["name"])
        try:
            r = requests.get(item["url"], allow_redirects=True)
            extension = mimetypes.guess_extension(r.headers["content-type"])
            if not extension:
                print("NO EXTENSION DETECTED!!")
                print(extension)
                print(r)
                extension = ""
            file = open("./savedImages/" + item["name"] + extension, 'wb')
            file.write(r.content)
            file.close()
            print("./savedImages/" + item["name"] + extension + " Created...")
            return item
        except Exception as e:
            print(e)
            print("Error downloading " + item["name"])
            return False


if __name__ == "__main__":
    SFM = SaveFileManager()
    # execute only if run as a script
    if not createFileDir():
        exit(1)
    main()
    # getExample()
    saved_items = getSaved()
    downloaded_items = SFM.getSave()
    filtered_items = filterSaved(saved_items)
    for fitem in filtered_items:
        result = downloadItem(fitem, downloaded_items)
        if result:
            SFM.pushObjToSaved(result)
    # SFM.pushArrToSaved(filtered_items)
    print(SFM.getSave())
    SFM.setSaveObj()

