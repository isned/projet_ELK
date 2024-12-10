

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os
import csv

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Define expected headers
EXPECTED_HEADERS_LIST = [
    ["Index", "Customer Id", "First Name", "Last Name", "Company", "City", "Country", "Phone 1", "Phone 2", "Email", "Subscription Date", "Website"],
    ["Order ID", "Product", "Quantity Ordered", "Price Each", "Order Date", "Purchase Address"]
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_csv(file):
    """Validate the structure of a CSV file."""
    try:
        file.seek(0)
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        headers = next(reader, None)
        if headers is None:
            return False, "The CSV file is empty."
        if headers not in EXPECTED_HEADERS_LIST:
            return False, "Invalid file !"
        return True, None
    except Exception as e:
        return False, "Invalid file !"


@main.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            return jsonify({"success": False, "message": "No files selected."}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"success": False, "message": "No files selected."}), 400

        if file and allowed_file(file.filename):
            valid, error = validate_csv(file)
            if not valid:
                return jsonify({"success": False, "message": error}), 400

            # Save file if valid
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.seek(0)
            file.save(filepath)

            return jsonify({"success": True, "message": f"File '{filename}' uploaded and validated successfully!"}), 200

    return render_template("upload.html", title="Upload a file")


@main.route("/")
def home():
    return render_template("index.html", title="Welcome ")
@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title="Dashboard")

