import os
import boto3
import psycopg2
from flask import Flask, request, render_template, redirect, flash

app = Flask(__name__)
app.secret_key = 'secretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure AWS S3
s3 = boto3.client(
    's3',
    aws_access_key_id='YOUR_AWS_ACCESS_KEY',
    aws_secret_access_key='YOUR_AWS_SECRET_KEY',
    region_name='ap-south-1'
)
S3_BUCKET_NAME = 'your-s3-bucket-name'

# Configure Database
conn = psycopg2.connect(
    host='your-db-host',
    database='your-db-name',
    user='your-db-user',
    password='your-db-password'
)
cur = conn.cursor()

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route for Form
@app.route('/')
def index():
    return render_template('index.html')

# Route to Handle Form Submission
@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    photo = request.files['photo']

    if photo:
        photo_filename = photo.filename
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
        photo.save(photo_path)

        # Upload to S3
        try:
            s3.upload_file(photo_path, S3_BUCKET_NAME, photo_filename)
            photo_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{photo_filename}"
            os.remove(photo_path)  # Remove the photo after upload

            # Save to Database
            cur.execute("INSERT INTO users (username, password, email, photo_url) VALUES (%s, %s, %s, %s)",
                        (username, password, email, photo_url))
            conn.commit()
            flash('Data and Photo uploaded successfully!')
        except Exception as e:
            flash(f"Error: {e}")
    else:
        flash('Photo upload failed.')

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

