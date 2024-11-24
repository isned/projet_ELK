from flask import Flask

def create_app():
    # Créer l'application Flask
    app = Flask(__name__)

    # Configurations
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

    # Enregistrer les blueprints ou routes
    from .routes import main
    app.register_blueprint(main)

    return app
