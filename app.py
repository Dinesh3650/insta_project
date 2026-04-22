from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder='.')

POSTS_FILE = 'saved_posts.json'
CATEGORIES_FILE = 'custom_categories.json'

@app.route('/')
def index():
    return send_from_directory('.', 'SheetD4_Manager.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/data', methods=['GET'])
def get_data():
    # Load posts
    posts = []
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            try:
                posts = json.load(f)
            except json.JSONDecodeError:
                posts = []
        
    # Load custom categories
    categories = []
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            try:
                categories = json.load(f)
            except json.JSONDecodeError:
                categories = []

    return jsonify({"posts": posts, "customCategories": categories})

@app.route('/api/update_post', methods=['POST'])
def update_post():
    req_data = request.json
    url = req_data.get('url')
    new_cat = req_data.get('category')
    
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r', encoding='utf-8') as f:
            try:
                posts = json.load(f)
            except json.JSONDecodeError:
                posts = []
            
        updated = False
        for p in posts:
            if p.get('url') == url:
                p['cat'] = new_cat
                updated = True
                break
                
        if updated:
            with open(POSTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=4)
            
    return jsonify({"status": "success"})

@app.route('/api/add_category', methods=['POST'])
def add_category():
    req_data = request.json
    new_cat = req_data.get('category')
    
    categories = []
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            try:
                categories = json.load(f)
            except json.JSONDecodeError:
                categories = []
            
    if new_cat not in categories:
        categories.append(new_cat)
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=4)
            
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
