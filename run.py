from flask import redirect, render_template, request, url_for
from app import create_app
import os

# Create the Flask app via the factory function
app = create_app()

# Define the secret key for sessions
app.config['SECRET_KEY'] = os.urandom(24)

# Register blueprint (if using blueprints)
# app.register_blueprint(main_blueprint)

@app.route('/')
def index():
    return render_template('index.html', title='Accueil')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        # Handle the uploaded file
        return redirect(url_for('upload'))  # Redirect back to the upload page after upload
    return render_template('upload.html', title='Upload')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/action')
def action():
    return render_template('action.html', title='Actions')

if __name__ == "__main__":
    # Run the Flask application in debug mode
    app.run(debug=True, port=5003)
