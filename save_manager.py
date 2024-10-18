import base64
import sqlite3
import json
import threading  # Import the threading module
from doctest import debug
from pathlib import Path
from db_import import insert_post
from logger import log


def load_image(path):
    with open(path, 'rb') as f:
        return f.read()


class SaveFileManager:
    _instance = None
    _lock = threading.Lock()  # Create a lock for synchronized access
    _subreddit_cache = None  # To store cached subreddits

    def __new__(cls, db_path: Path):
        if cls._instance is None:
            cls._instance = super(SaveFileManager, cls).__new__(cls)
            cls._instance.__initialized = False
            cls._instance._connect_db(db_path)
        return cls._instance

    def _connect_db(self, db_path):
        """Connect to the SQLite database."""
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)  # Allow connections from different threads
        self._create_tables()
        self.__initialized = True

    def _create_tables(self):
        """Create necessary tables for save objects and sub-items."""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    url TEXT,
                    permalink TEXT,
                    ts REAL,
                    nsfw BOOLEAN,
                    title TEXT,
                    subreddit TEXT,
                    is_gallery BOOLEAN
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sub_items (
                    id TEXT PRIMARY KEY,
                    post_id TEXT,
                    url TEXT,
                    n INTEGER,
                    path TEXT,
                    FOREIGN KEY (post_id) REFERENCES posts(id)
                )
            ''')

            self.conn.commit()
        except Exception as e:
            log(f"Error creating tables: {str(e)}")


    def get_image_path(self, db_id, gallery_index=None):
        cursor = self.conn.cursor()
        print(db_id)
        if gallery_index == 0 or gallery_index is None:
            # Not a gallery
            query = f'SELECT path FROM posts WHERE id ="{db_id}"'

            with self.conn:
                result = cursor.execute(query)
            path = result.fetchone()[0]
            print(path)
            return path
        else:
            # Gallery
            query = f'SELECT path FROM sub_items WHERE post_id = "{db_id}" AND n = {gallery_index}'

            with self.conn:
                result = cursor.execute(query)
            path = result.fetchone()[0]
            return path

    def load_image(self, db_id, gallery_index=None):
        path = self.get_image_path(db_id, gallery_index)
        return load_image(path)



    def get_posts(self, count=25, after=None, nsfw=None, subreddit=None, saved=None, seen=None):
        log(locals().values())
        """Retrieve posts from the database with optional filters."""
        query = "SELECT id, is_gallery, nsfw, permalink, saved, seen, subreddit, title, ts, url, path FROM posts"
        filters = []
        params = []  # This will hold the values to bind to the placeholders

        if nsfw is not None:
            filters.append("nsfw = ?")
            params.append(nsfw)

        if subreddit is not None:
            filters.append("subreddit = ?")
            params.append(subreddit)

        if saved is not None:
            filters.append("saved = ?")
            params.append(saved)

        if seen is not None:
            filters.append("seen = ?")
            params.append(seen)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY ts LIMIT ?"
        params.append(count)  # Append count to the params

        if after:
            query += " AND ts > (SELECT ts FROM posts WHERE id = ?)"
            params.append(after)  # Append after to the params

        if debug:
            log(f"Query: {query}, Params: {params}")
        with self.conn:
            cursor = self.conn.cursor()  # Get a new cursor
            result = cursor.execute(query, params)  # Execute with the params list
        posts = [dict(zip([column[0] for column in cursor.description], row)) for row in result.fetchall()]
        for obj in posts:
            # Check if the key 'path' exists
            if 'path' in obj and obj['path'] is not None and obj['path']!= '':
                # Remove the 'path' key and replace it with 'has_image: 1'
                obj.pop('path')  # Remove the 'path' key
                obj['has_image'] = 1  # Add 'has_image' key
        return posts

    def get_subreddit_options(self):
        cursor = self.conn.cursor()  # Get a new cursor
        """Fetch distinct subreddit options and cache them."""
        # Check if cache is available
        if SaveFileManager._subreddit_cache is not None:
            return SaveFileManager._subreddit_cache

        # Query the database for distinct subreddits
        query = "SELECT DISTINCT subreddit FROM posts"
        cursor.execute(query)
        subreddits = [row[0] for row in cursor.fetchall()]

        # Cache the result
        SaveFileManager._subreddit_cache = subreddits

        return subreddits

    def pushObjToSaved(self, name, obj):
        """Use the insert_post function to insert a post and its sub-items into the database."""
        with self._lock:  # Lock the section for thread-safe writing
            try:
                cursor = self.conn.cursor()  # Get a new cursor
                insert_post(obj, cursor)  # Use the insert_post function to handle object insertion
                self.conn.commit()
            except Exception as e:
                log(f"Error inserting/updating post in database: {str(e)}")

    def getSaveObj(self):
        cursor = self.conn.cursor()  # Get a new cursor
        """Return a list of keys (post IDs) from the saved objects."""
        try:
            cursor.execute('SELECT id FROM posts')
            rows = cursor.fetchall()
            return [row[0] for row in rows]  # Return only the keys (post IDs)
        except Exception as e:
            log(f"Error retrieving saved objects: {str(e)}")
            return []

    def setSaveObj(self):
        """Commit changes to the database (if necessary)."""
        with self._lock:
            try:
                self.conn.commit()
            except Exception as e:
                log(f"Error committing changes to database: {str(e)}")

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
