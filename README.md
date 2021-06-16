# Reddit saved saver

This is my dinky script to use reddit api to scan my saved posts, and ACTUALLY save them to my webserver.

## Features
* Scan latest saved items from reddit user account.
* Download images from the posts
* Save some metadata from images
  * Title
  * Permalink
  * Image URL
  * nsfw status
  * is it gallery
    * Gallery items
    * Gallery items URL
    * Gallery items order
  * Subreddit it was from
  * Post timestamp
  * ID
  
  And sometimes, if you somehow manage to use the update funktion, and something is deleted, it will save
  * that item was deleted, meaning that it is unique
  * IF it has errors while downloading some data


* Wait 1 second between requests to reddit, simpy to keep good distance between rate limits and the script (in normal use you will only make ~1 request every hour or so)
While setting up, you will make ~50 requests to reddit API and ~1000 to image servers 


## Usage
1. Clone repo
2. run main.py manually to create required directories, and required files (Config)
3. Go to '<repo>/data/config.json' and fill in your config
  * Example config
  ```json
  {
  "username": "<Reddit username>",
  "password": "<Reddit password>",
  "User-Agent": "Example custom user agent for <Reddit username>",
  "count": 25,
  "HTTPBasicAuth1": "",
  "HTTPBasicAuth2": "",
  "target_path": "",
  "debug": "False",
  "version": 1
}
```
  * Yes, it needs reddit username, and password in plain text, so make sure your server is secure :) If you can make it not need it, feel free to make a PR
  * You need to go to https://www.reddit.com/prefs/apps and create a new personal use script app to get HTTPBasicAuth1 and HTTPBasicAuth2 
    * HTTPBasicAuth1 = Script "id"
    * HTTPBasicAuth2 = Scripts secret
  * Target path is where you want to save images, you can set this to anything, 
  but you need to make sure that the script can write there (For me it is symlinked to a network drive for SPAACE)
  * Debug enable / disable debug logging, not always usefull, but sometimes, also this might be very verbose, recommended to leave disabled on a server
  * Version, i will manually update this in the script when needed, don't touch this, this should make it possible to update data and config without data loss in the future
  
  4. Run the script again manually with python main.py 1 to get as much of your saved history as possible (At maxium ~40 pages, so around 1000 items) 
  5. Create a magical schedule / chron job to run the script however often you want, I recommend hourly
  
