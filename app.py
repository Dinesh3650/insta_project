from flask import Flask, request, jsonify, send_from_directory
import json
import os
import re

app = Flask(__name__, static_folder='.')

POSTS_FILE = 'saved_posts.json'
HTML_FILE = 'index.html'

def rebuild_html(posts):
    """Updates the hardcoded posts array in index.html"""
    if not os.path.exists(HTML_FILE):
        return False
    
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple regex to find let posts = [...];
    # This works even if the array is on one massive line
    new_data_js = f"let posts = {json.dumps(posts)};"
    
    # Replace the existing posts declaration
    updated_content = re.sub(r'let posts = \[.*?\];', new_data_js, content, flags=re.DOTALL)
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    return True

@app.route('/')
def index():
    return send_from_directory('.', HTML_FILE)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/add_post', methods=['POST'])
def add_post():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    try:
        # 1. Fetch metadata using instaloader
        # We use a temporary instance to avoid login issues for public posts
        import instaloader
        L = instaloader.Instaloader()
        
        # Extract shortcode from URL
        # URL format: https://www.instagram.com/p/SHORTCODE/
        shortcode_match = re.search(r'/p/([^/?#&]+)', url)
        if not shortcode_match:
            return jsonify({"status": "error", "message": "Invalid Instagram URL"}), 400
        
        shortcode = shortcode_match.group(1)
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        new_post = {
            "url": url,
            "thumb": post.url, # Instaloader provides the display URL (image)
            "text": post.caption or "",
            "cat": "Other" # Default category
        }

        # 2. Save to saved_posts.json
        posts = []
        if os.path.exists(POSTS_FILE):
            with open(POSTS_FILE, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        
        # Check if already exists
        if any(p['url'] == url for p in posts):
             return jsonify({"status": "error", "message": "Post already exists"}), 400

        posts.insert(0, new_post) # Add to start

        with open(POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=4)

        # 3. Update index.html
        rebuild_html(posts)

        return jsonify({"status": "success", "post": new_post})

    except ImportError:
        return jsonify({"status": "error", "message": "instaloader not installed. Run 'pip install instaloader'"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    posts = []
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    return jsonify({"posts": posts})

if __name__ == '__main__':
    print("Dashboard Server started at http://localhost:5000")
    app.run(debug=True, port=5000)
