import sqlite3
import json
from cgi import logfp


def insert_post(data, cursor):
    # Connect to the SQLite database

    # Insert into posts table
    post_query = '''
        INSERT OR REPLACE INTO posts (id, url, permalink, ts, nsfw, title, subreddit, is_gallery, path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    print(data)
    path = data.get("path", "")  # Get the path from the data, or default to an empty string if not present
    post_values = (
        data["id"],
        data["url"],
        data["permalink"],
        data["ts"],
        data["nsfw"],
        data["title"],
        data["subreddit"],
        data["is_gallery"],
        path
    )

    cursor.execute(post_query, post_values)

    # Insert into sub_items table
    sub_item_query = '''
        INSERT OR REPLACE INTO sub_items (id, post_id, url, n, path)
        VALUES (?, ?, ?, ?, ?)
    '''
    if "sub_items" in data and len(data["sub_items"]) > 0:  # Check if sub_items exist in the data
        for sub_item in data["sub_items"].values():
            sub_item_values = (
                sub_item["id"],
                data["id"],  # Reference back to the post
                sub_item["url"],
                sub_item["index"],
                sub_item["path"]
            )
            cursor.execute(sub_item_query, sub_item_values)



# main
def main():
    # Load the config
    db_path='/Users/luna/dev/projects_db'
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()



    # Retrieve and insert data into the database
    #...
    file = open('data/save.json').read()
    data = json.loads(file)
    print(f'Loaded {len(data)} posts')

    for key in data:
        insert_post(data[key], cursor)

    # Commit and close connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()