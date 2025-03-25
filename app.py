from flask import Flask, render_template, request
import psycopg2
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(_name_)

# Database Configuration (PostgreSQL on EC2/RDS)
DB_HOST = "postgres.c78emaw4caq6.ap-south-1.rds.amazonaws.com"  # Update with EC2 or RDS endpoint
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "Thanimamatha"

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=postgres,
        user=postgres,
        password=Thanimamatha 
    )

# Set upload folder
UPLOAD_FOLDER = "/home/ubuntu/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    image = request.files.get("image")  # Image is optional

    if not (name and email):
        return "Name and email are required!", 400

    image_path = None  # Default to None if no image is uploaded

    if image:
        filename = secure_filename(image.filename)
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(local_path)
        image_path = local_path  # Store local path in DB

    # Save data to database with local image path
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, image_url, created_at) VALUES (%s, %s, %s, %s)",
            (name, email, image_path, datetime.utcnow())
        )
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        return f"Error saving to database: {str(e)}", 500

    return render_template('success.html', name=name, image_path=image_path)

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5003)
