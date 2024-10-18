from flask import Flask, request, jsonify
from pathlib import Path
from config_manager import ConfigManager
from save_manager import SaveFileManager, load_image


class PostAPI:
    def __init__(self):
        config_path = Path("./data/config.json")
        config_manager = ConfigManager(config_path)

        # Initialize SaveFileManager
        save_manager = SaveFileManager(config_manager.db_path)

        self.save_manager = save_manager

        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/posts', methods=['GET'])
        def get_posts_endpoint():
            # Extract parameters from the request
            count = request.args.get('count', default=25, type=int)
            after = request.args.get('after', default=None, type=str)
            nsfw = request.args.get('nsfw', default=None, type=lambda x: (x.lower() == 'true'))
            subreddit = request.args.get('subreddit', default=None, type=str)
            saved = request.args.get('saved', default=None, type=lambda x: (x.lower() == 'true'))
            seen = request.args.get('seen', default=None, type=lambda x: (x.lower() == 'true'))

            posts = self.save_manager.get_posts(count, after, nsfw, subreddit, saved, seen)

            # Set response headers
            response_headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
            # Set response status code
            response = jsonify(posts)
            response.status_code = 200
            response.headers.extend(response_headers)
            return response

        @self.app.route('/subreddits', methods=['GET'])
        def get_subreddits_endpoint():
            subreddits = self.save_manager.get_subreddit_options()
            # Set response headers
            response_headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
            # Set response status code
            response = jsonify(subreddits)
            response.status_code = 200
            response.headers.extend(response_headers)
            return response

        @self.app.route('/test', methods=['GET'])
        def test_endpoint():
            paths = self.save_manager.get_paths(['1aey96v', '1b6j5gs', '1bhafod'])
            asdf = paths #self.save_manager.load_images(paths)

            response_headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
            # Set response status code
            response = jsonify(asdf)
            response.status_code = 200
            response.headers.extend(response_headers)
            return response

        @self.app.route('/images', methods=['GET'])
        def get_images_endpoint():
            db_id = request.args.get('id', default=None, type=str)
            gallery_index = request.args.get('gallery_index', default=None, type=int)
            if db_id is None:
                return jsonify({"error": "Missing db_id parameter"}), 400
            result = self.save_manager.load_image(db_id, gallery_index)
            #json headers
            response_headers = {
                'Content-Type': 'image/jpeg',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
            # Set response status code
            response = self.app.make_response(result)
            response.status_code = 200
            response.headers.extend(response_headers)
            return response






    def run(self):
        self.app.run(debug=True)

def main():
    api = PostAPI()
    api.run()

if __name__ == '__main__':
    main()
