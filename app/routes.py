from flask import Blueprint, render_template, request, redirect, url_for, flash
import os

main = Blueprint('main', __name__)

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@main.route("/")
def home():
    return render_template("index.html", title="Bienvenue sur ELK")


'''@main.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("Aucun fichier sélectionné", "danger")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("Aucun fichier sélectionné", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            flash(f"Fichier '{filename}' uploadé avec succès !", "success")
            return redirect(url_for('main.home'))

    return render_template("upload.html", title="Uploader un fichier")'''

@main.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("Aucun fichier sélectionné", "danger")
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash("Aucun fichier sélectionné", "danger")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            flash(f"Fichier '{filename}' uploadé avec succès !", "success")
            # Redirection vers la page dashboard
            return redirect(url_for('main.dashboard'))

    return render_template("upload.html", title="Uploader un fichier")




@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')