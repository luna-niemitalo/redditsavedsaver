#!/usr/bin/env python3
import requests
import requests.auth

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
    print(response.json()["access_token"])
    token = response.json()["access_token"]


def getExample():
    global token
    headers = {"Authorization": "bearer " + token,
              "User-Agent": "Test custom user agent by ***REMOVED***"}
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    print(response.json())

def getSaved():
    global token
    headers = {"Authorization": "bearer " + token,
              "User-Agent": "Test custom user agent by ***REMOVED***",
               "sort": "new"}
    response = requests.get("https://oauth.reddit.com/user/***REMOVED***/saved", headers=headers)
    print(response.json())
    return response.json()

def filterSaved(saved_items):
    result = []
    for item in saved_items["data"]["children"]:
        image_obj = {
            "name": item["data"]["name"],
            "url": item["data"]["url"]
        }
        result.append(image_obj)
    print(len(result))
    print(result)
    return result

def getSaveFile():
    try:
        f = open("save.json", "w+")
    except:
        print("An exception occurred")
        exit(1)
    return f


if __name__ == "__main__":
    # execute only if run as a script
    main()
    # getExample()
    # saved_items = getSaved()
    # filtered_items = filterSaved(saved_items)
    savefile = getSaveFile()
    savefile.write("Hello world")
    with savefile as fp:
        for line in fp:
            print(line)

    savefile.close()
