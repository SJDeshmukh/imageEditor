from flask import Flask, request, render_template, redirect, url_for, flash,jsonify
import sqlite3
import os
import random
from flask import send_file
from PIL import Image
import io
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Ensure the database file exists
db_file = 'user_data.db'
print(f"Database file path: {os.path.abspath(db_file)}")

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

# Create table if it doesn't exist
def create_table():
    if not os.path.exists(db_file):  # Check if the file exists before creating
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
        print("Table created successfully!")  # Debugging line
        conn.close()
    else:
        print("Database already exists!")
@app.route('/register', methods=['GET', 'POST'])



def register():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        location = request.form['location']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']

        print(f"Received data: Name={name}, Location={location}, Age={age}, Gender={gender}, Email={email}")  # Debugging line

        # Insert user data into the database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, location, age, gender, email, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, location, age, gender, email, password))
            conn.commit()
            flash('Registration successful!', 'success')  # Flash success message
            print("Data inserted successfully!")  # Debugging line
        except Exception as e:
            flash('Registration failed! Please try again.', 'error')  # Flash error message
            print(f"Error occurred: {e}")  # Debugging line
        finally:
            conn.close()

        # Redirect to registration page to show the message
        return render_template('register.html')

    return render_template('register.html')  # Make sure this file exists in the templates folder

# Success route (optional)
@app.route('/success')
def success():
    return "Registration successful!"

@app.route('/')
def logintopage():
    return render_template('login.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    return render_template('home_page.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/image_resizer')
def image_resizer():
    return render_template('image_resizer.html')


@app.route('/compression_page')
def compression_page():
    return render_template('compression.html')


@app.route('/grayscale')
def grayscale():
    return render_template('grayscale.html')

@app.route('/edge_detection')
def edge_detection():
    return render_template('edge_detection.html')

@app.route('/color_change')
def color_change():
    return render_template('color_change.html')


@app.route('/log_in')
def log_in():
    return render_template('login.html')


@app.route('/watermark')
def watermark():
    return render_template('watermark.html')

@app.route('/convert', methods=['POST'])
def convert_image():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    format = request.form['format']

    # Open the uploaded image
    image = Image.open(file)

    # Ensure 'JPG' is treated as 'JPEG'
    if format.lower() == 'jpg':
        format = 'jpeg'

    # Convert the image to the desired format
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format.upper())
    img_byte_arr.seek(0)

    # Return the converted image as a response
    return send_file(img_byte_arr, mimetype=f'image/{format.lower()}', as_attachment=True, download_name=f'converted_image.{format.lower()}')


@app.route('/compress', methods=['POST'])
def compress_image():
    try:
        print("in the compression process")
        # Validate the request for file and compression level
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        if 'compression_level' not in request.form:
            return jsonify({"error": "Compression level not provided"}), 400

        # Extract the uploaded file and compression level
        file = request.files['file']
        compression_level = int(request.form['compression_level'])

        # Validate the compression level range
        if compression_level < 0 or compression_level > 100:
            return jsonify({"error": "Compression level must be between 0 and 100"}), 400

        # Process the image
        image = Image.open(file)
        output = io.BytesIO()
        image = image.convert("RGB")  # Ensure compatibility with JPEG format
        image.save(output, format="JPEG", quality=compression_level)  # Compress the image
        output.seek(0)
        print("Done conpression")
        # Return the compressed image as a response
        return send_file(output, mimetype='image/jpeg', as_attachment=True, download_name='compressed_image.jpg')

    except Exception as e:
        # Log the error and return a generic error message
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/home', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verify user credentials (This is a simple check; you may want to hash passwords in a real application)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            flash('Login successful!', 'success')  # Flash success message
            return render_template('home_page.html')  # Redirect to home page after successful login
        else:
            flash('Invalid email or password', 'error')  # Flash error message if login fails

    return render_template('login.html')

if __name__ == '__main__':
    create_table()  # Ensure table is created if database does not exist
    CORS(app) 
    app.run(debug=True)
