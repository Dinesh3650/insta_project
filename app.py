from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import instaloader
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def scrape_with_meta_tags(url):
    """Fallback 2: Scrape public meta tags using advanced headers"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    }
    try:
        # Extract shortcode to build a direct media link for the thumbnail
        shortcode_match = re.search(r'/(p|reel|tv)/([^/?#&]+)', url)
        shortcode = shortcode_match.group(2) if shortcode_match else None
        
        # TRICK: Direct media link for thumbnail
        direct_thumb = f"https://www.instagram.com/p/{shortcode}/media/?size=l" if shortcode else None

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            og_description = soup.find("meta", property="og:description")
            og_image = soup.find("meta", property="og:image")
            
            return {
                "url": url,
                "thumb": direct_thumb or (og_image["content"] if og_image else ""),
                "text": og_description["content"] if og_description else "Instagram Post",
                "cat": "Other"
            }
        elif direct_thumb:
            # Even if the page is blocked, the direct media link often works!
            return {
                "url": url,
                "thumb": direct_thumb,
                "text": "Instagram Post (Caption Blocked)",
                "cat": "Other"
            }
    except Exception as e:
        print(f"Fallback error: {e}")
    return None

@app.route('/api/scrape_post', methods=['POST'])
def scrape_post():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    try:
        # 1. Try with Instaloader first (best quality)
        L = instaloader.Instaloader()
        shortcode_match = re.search(r'/(p|reel|tv)/([^/?#&]+)', url)
        if shortcode_match:
            shortcode = shortcode_match.group(2)
            try:
                # Set a shorter timeout for Instaloader to fail fast if blocked
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                return jsonify({"status": "success", "post": {
                    "url": url,
                    "thumb": post.url,
                    "text": post.caption or "",
                    "cat": "Other"
                }})
            except Exception:
                pass # Continue to fallback

        # 2. Advanced Fallback
        fallback_post = scrape_with_meta_tags(url)
        if fallback_post:
            return jsonify({"status": "success", "post": fallback_post})
        
        return jsonify({"status": "error", "message": "Instagram is heavily blocking requests right now. Try again later."}), 403

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home():
    return "Instagram Scraper API is running!"

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
