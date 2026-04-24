import re

def update_html():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Replace the hardcoded posts array with Firebase logic
        new_posts_logic = """let posts = [];
        
        // Listen for posts from Firebase
        db.ref('posts').on('value', (snapshot) => {
            const data = snapshot.val();
            if (data) {
                posts = Array.isArray(data) ? data : Object.values(data);
                // Filter out any null items
                posts = posts.filter(p => p !== null);
            } else {
                posts = [];
            }
            renderPosts();
        });"""

        # Replace `let posts = [...];` safely
        # We find 'let posts = [' and everything until '];' followed by 'function renderPosts()' or just the end of the statement.
        content = re.sub(r'let posts = \[\{.*?\}\];', new_posts_logic, content, flags=re.DOTALL)

        # 2. Update the frontend fetch logic in addPost()
        # We change the URL to the new Render cloud backend, and then push the result to Firebase!
        old_fetch_logic = """
            try {
                const response = await fetch('/api/add_post', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                const result = await response.json();

                if (result.status === 'success') {
                    status.innerText = "✅ Success! Refreshing...";
                    status.style.color = "#4CAF50";
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    status.innerText = "❌ " + (result.message || "Failed");
                    status.style.color = "#f44336";
                }
            } catch (err) {
                status.innerText = "❌ Server not running (app.py)";
                status.style.color = "#f44336";
            }
        }"""

        new_fetch_logic = """
            try {
                // 1. Scrape metadata using Cloud Backend
                // (Using localhost for now until you deploy, but you can change it to your Render URL)
                const BACKEND_URL = 'http://127.0.0.1:5000/api/scrape_post';
                
                const response = await fetch(BACKEND_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                const result = await response.json();

                if (result.status === 'success') {
                    // 2. Save directly to Firebase from the frontend!
                    const newPost = result.post;
                    const newPostRef = db.ref('posts').push();
                    await newPostRef.set(newPost);
                    
                    status.innerText = "✅ Success! Added to Database.";
                    status.style.color = "#4CAF50";
                    setTimeout(() => {
                        status.innerText = "";
                        urlInput.value = "";
                    }, 2000);
                } else {
                    status.innerText = "❌ " + (result.message || "Failed");
                    status.style.color = "#f44336";
                }
            } catch (err) {
                status.innerText = "❌ Backend API error";
                status.style.color = "#f44336";
                console.error(err);
            }
        }"""

        content = content.replace(old_fetch_logic.strip(), new_fetch_logic.strip())

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("Frontend successfully updated to use Firebase!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_html()
