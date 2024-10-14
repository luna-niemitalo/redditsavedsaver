import sqlite3
import json
from pathlib import Path
from db_import import insert_post
from logger import log

class SaveFileManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connect_db()
        self._create_tables()

    def _connect_db(self):
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def _create_tables(self):
        """Create necessary tables for save objects and sub-items."""
        try:
            # Create the posts and sub_items tables (from the previous insert_post function)
            self.cursor.execute('''
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

            self.cursor.execute('''
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


    def getSaveObj(self):
        """Return a list of keys (post IDs) from the saved objects."""
        try:
            self.cursor.execute('SELECT id FROM posts')
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]  # Return only the keys (post IDs)
        except Exception as e:
            log(f"Error retrieving saved objects: {str(e)}")
            return []

    def setSaveObj(self):
        """Commit changes to the database (if necessary)."""
        try:
            self.conn.commit()
        except Exception as e:
            log(f"Error committing changes to database: {str(e)}")

    def pushObjToSaved(self, name, obj):
        """Use the insert_post function to insert a post and its sub-items into the database."""
        try:
            insert_post(obj, self.cursor)  # Use the insert_post function to handle object insertion
            self.conn.commit()
        except Exception as e:
            log(f"Error inserting/updating post in database: {str(e)}")

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


