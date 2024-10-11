import json
from pathlib import Path
import requests
from utils import log
import mimetypes
from api_manager import fetch_saved_items

def get_gallery(submission):
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
        log("getGallery Exception: " + submission['id'])
    return subItems

def filter_saved(saved_items):
    result = []
    for item in saved_items["data"]["children"]:
        try:
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
                image_obj["sub_items"] = get_gallery(item["data"])

            result.append(image_obj)
        except Exception as e:
            log("FilterSaved Exception: " + str(json.dumps(e)))
            log("    Item: " + item)

    return result

def download_saved_items(token, config, existing_items, save_manager):
    """Download Reddit saved items."""
    after = ""
    while after is not None:
        saved_items = fetch_saved_items(token, config, after)
        if saved_items is None:
            break

        filtered_items = filter_saved(saved_items)
        for item in filtered_items:
            download_item(item, config)

        # Update 'after' token for pagination
        after = None#saved_items['data'].get('after')

    save_manager.set_save_obj(existing_items)

def download_item(item, config):
    """Download individual item based on type."""
    folder = Path(config["target_path"])
    folder.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(item["url"], allow_redirects=True)
        extension = mimetypes.guess_extension(response.headers["content-type"])
        if extension:
            file_path = folder / f"{item['id']}{extension}"
            with open(file_path, 'wb') as file:
                file.write(response.content)
            log(f"Downloaded: {file_path}")
        else:
            log(f"No extension for item {item['id']}")
    except Exception as e:
        log(f"Failed to download {item['id']}: {e}")
