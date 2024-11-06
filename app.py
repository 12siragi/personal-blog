from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_key"  # For session management

article = {
    'title': 'My First Blog Post',
    'date': datetime.now().strftime('%B %d, %Y'),
    'content': 'This is the content of the first blog post. Welcome to my blog!'
}


# Directory to store article files
ARTICLE_DIR = "articles"
if not os.path.exists(ARTICLE_DIR):
    os.makedirs(ARTICLE_DIR)

# Hardcoded credentials for simplicity
ADMIN_CREDENTIALS = {"username": "admin", "password": "password"}

# Function to load articles from JSON files
def load_articles():
    articles = []
    articles_dir = 'articles'
    for filename in os.listdir(articles_dir):
        if filename.endswith('.json'):
            with open(os.path.join(articles_dir, filename), 'r') as file:
                article_data = json.load(file)
                articles.append(article_data)
    return articles

# Route for Home Page (Guest Section)
@app.route('/')
def home():
    articles = load_articles()  # Get the list of articles
    return render_template("index.html", articles=articles)

# Route for displaying individual article page
@app.route('/article/<article_id>')
def article_page(article_id):
    articles = load_articles()
    # Find the article by matching the article_id with the title
    article = next((art for art in articles if art['title'].replace(' ', '_').lower() == article_id), None)
    if article:
        return render_template('article_page.html', article=article)
    else:
        return f"Article not found", 404

# Route for Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

# Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    articles = load_articles()
    return render_template("dashboard.html", articles=articles)

# Route to Add Article (Admin Section)
@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        article_data = {
            "title": title,
            "content": content,
            "date": request.form['date']
        }
        article_id = title.replace(" ", "_").lower()
        article_path = os.path.join(ARTICLE_DIR, f"{article_id}.json")
        with open(article_path, 'w') as f:
            json.dump(article_data, f)
        return redirect(url_for('dashboard'))
    return render_template("add_article.html")

# Route to Edit Article (Admin Section)
@app.route('/edit_article/<article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    article_path = os.path.join(ARTICLE_DIR, f"{article_id}.json")
    if not os.path.exists(article_path):
        return "Article not found", 404
    
    with open(article_path, 'r') as f:
        article = json.load(f)
    
    if request.method == 'POST':
        article["title"] = request.form['title']
        article["content"] = request.form['content']
        article["date"] = request.form['date']
        # Update the article file with the new content
        with open(article_path, 'w') as f:
            json.dump(article, f)
        return redirect(url_for('dashboard'))
    
    return render_template("edit_article.html", article=article)

# Route to Delete Article (Admin Section)
@app.route('/delete_article/<article_id>', methods=['POST'])
def delete_article(article_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    article_path = os.path.join(ARTICLE_DIR, f"{article_id}.json")
    if os.path.exists(article_path):
        os.remove(article_path)
    return redirect(url_for('dashboard'))

# Route to Logout (Admin Section)
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
