from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
import sqlite3
import os
import io
from PIL import Image
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database file
db_file = 'user_data.db'

# Database connection
def get_db_connection():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

# Create database table
def create_table():
    if not os.path.exists(db_file):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                location TEXT,
                age INTEGER,
                gender TEXT,
                email TEXT,
                password TEXT
            )
        ''')
        conn.commit()
        conn.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('log_in'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def require_login():
    open_routes = ['log_in', 'register', 'static']  # Routes accessible without login
    if 'logged_in' not in session or not session['logged_in']:
        if request.endpoint not in open_routes and request.endpoint is not None:
            flash('You must log in to access this page.', 'error')
            return redirect(url_for('log_in'))

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, location, age, gender, email, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, location, age, gender, email, password))
            conn.commit()
            flash('Registration successful!', 'success')
        except Exception as e:
            flash('Registration failed! Please try again.', 'error')
        finally:
            conn.close()

        return redirect(url_for('log_in'))

    return render_template('register.html')

@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['logged_in'] = True
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('log_in'))

@app.route('/home')
@login_required
def home():
    return render_template('home_page.html')

@app.route('/services')
@login_required
def services():
    return render_template('services.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('home_page.html')

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/image_resizer')
@login_required
def image_resizer():
    return render_template('image_resizer.html')

@app.route('/compression_page')
@login_required
def compression_page():
    return render_template('compression.html')

@app.route('/grayscale')
@login_required
def grayscale():
    return render_template('grayscale.html')

@app.route('/edge_detection')
@login_required
def edge_detection():
    return render_template('edge_detection.html')

@app.route('/color_change')
@login_required
def color_change():
    return render_template('color_change.html')

@app.route('/watermark')
@login_required
def watermark():
    return render_template('watermark.html')

@app.route('/convert', methods=['POST'])
@login_required
def convert_image():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    format = request.form['format']

    image = Image.open(file)
    if format.lower() == 'jpg':
        format = 'jpeg'

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format.upper())
    img_byte_arr.seek(0)

    return send_file(img_byte_arr, mimetype=f'image/{format.lower()}', as_attachment=True, download_name=f'converted_image.{format.lower()}')

@app.route('/compress', methods=['POST'])
@login_required
def compress_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        if 'compression_level' not in request.form:
            return jsonify({"error": "Compression level not provided"}), 400

        file = request.files['file']
        compression_level = int(request.form['compression_level'])

        if compression_level < 0 or compression_level > 100:
            return jsonify({"error": "Compression level must be between 0 and 100"}), 400

        image = Image.open(file)
        output = io.BytesIO()
        image = image.convert("RGB")
        image.save(output, format="JPEG", quality=compression_level)
        output.seek(0)

        return send_file(output, mimetype='image/jpeg', as_attachment=True, download_name='compressed_image.jpg')
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# App entry point
if __name__ == '__main__':
    create_table()
    CORS(app)
    app.run(debug=True)
