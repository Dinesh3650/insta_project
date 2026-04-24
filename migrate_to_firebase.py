import json
import re
import urllib.request

def migrate():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'let posts = (\[.*?\]);', content, re.DOTALL)
        if not match:
            print("Could not find 'let posts = [...]' in index.html")
            return
            
        posts_json = match.group(1)
        posts = json.loads(posts_json)
        print(f"Found {len(posts)} posts in index.html.")
        
        url = 'https://insta-manager-d4649-default-rtdb.firebaseio.com/posts.json'
        req = urllib.request.Request(url, data=json.dumps(posts).encode('utf-8'), method='PUT')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req) as response:
            print(f"Successfully uploaded {len(posts)} posts to Firebase! Status: {response.status}")
            
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == '__main__':
    migrate()
