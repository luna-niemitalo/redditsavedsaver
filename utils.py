import json
from logger import log


import requests
import mimetypes
from pathlib import Path

def get_gallery(submission):
    """Retrieve gallery items from a Reddit submission."""
    sub_items = {}
    count = 0
    try:
        # Check if the submission contains gallery data
        if "gallery_data" in submission:
            for item in sorted(submission["gallery_data"]['items'], key=lambda x: x['id']):
                count += 1
                media_id = item['media_id']
                meta = submission["media_metadata"][media_id]
                if meta['e'] == 'Image':
                    source = meta['s']
                    url = source['u']
                    parsed_url = url.replace('amp;', '')  # Remove any 'amp;' from the URL
                    sub_item = {
                        "url": parsed_url,
                        "index": count,
                        "id": media_id
                    }
                    sub_items[media_id] = sub_item
    except Exception as e:
        log(f"Error retrieving gallery for submission {submission['id']}: {str(e)}")
    return sub_items

def download_item(item, targetFolder):
    log(f"Downloading {item['id']}")
    try:
        if item["is_gallery"]:
            return handle_gallery_item(item, targetFolder)
        else:
            return handle_normal_item(item, targetFolder)
    except Exception as e:
        log(f"Error downloading {item['id']}: {str(e)}")
        item["has_errors"] = True
        item["errors"] = [str(e)]
        return item

def handle_normal_item(item, targetFolder):
    """Download a normal Reddit item."""
    r = requests.get(item["url"], allow_redirects=True)
    extension = mimetypes.guess_extension(r.headers["content-type"])

    if not extension:
        log("NO EXTENSION DETECTED!!")
        log(r.json())
        item["has_errors"] = True
        return item

    target = Path(targetFolder) / f"{item['id']}{extension}"

    if target.exists():
        item["path"] = target.as_posix()
        log(f"{target.as_posix()} Already exists...")
        return item

    with open(target, 'wb') as file:
        file.write(r.content)

    item["path"] = target.as_posix()
    log(f"{target.as_posix()} Created...")
    return item

def handle_gallery_item(gitem, targetFolder):
    """Download all items in a Reddit gallery."""
    for key in gitem["sub_items"]:
        item = gitem["sub_items"][key]
        url = item["url"]
        r = requests.get(url, allow_redirects=True)
        extension = mimetypes.guess_extension(r.headers["content-type"])

        if not extension:
            log("NO EXTENSION DETECTED!!")
            log(f"Status code: {r.status_code}")
            log(f"Reason: {r.reason}")
            log(f"Url: {r.url}")
            item["has_errors"] = True
            continue

        target = Path(targetFolder) / f"{key}{extension}"

        if target.exists():
            item["path"] = target.as_posix()
            log(f"{target.as_posix()} Already exists...")
            continue

        with open(target, 'wb') as file:
            file.write(r.content)

        item["path"] = target.as_posix()
        log(f"{target.as_posix()} Created...")

    return gitem
