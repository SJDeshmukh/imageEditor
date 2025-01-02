from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to your SQLite database
db_file = 'user_data.db'

def get_db_connection():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

# Generate a unique link ID (could be any random string)
def generate_link_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Generate a unique link for the user
        link_id = generate_link_id()
        return render_template('home.html', link=link_id)  # Pass the link ID to the template
    return render_template('home.html')

@app.route('/post/<link_id>', methods=['GET', 'POST'])
def post_to_link(link_id):
    if request.method == 'POST':
        content = request.form['content']
        
        # Insert the post (review) into the database for the specific link ID
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posts (link_id, content)
            VALUES (?, ?)
        ''', (link_id, content))
        conn.commit()
        conn.close()
        
        flash('Your review has been posted!', 'success')
        return redirect(url_for('view_posts', link_id=link_id))
    
    return render_template('post.html', link_id=link_id)

@app.route('/posts/<link_id>', methods=['GET'])
def view_posts(link_id):
    # Fetch all posts for the given link ID from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE link_id = ?', (link_id,))
    posts = cursor.fetchall()
    conn.close()
    
    return render_template('view_posts.html', link_id=link_id, posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
