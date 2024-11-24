import os
from flask import render_template
from app import create_app
#from main import main as main_blueprint  # type: ignore # Assurez-vous que le blueprint est bien importé

# Créer l'application Flask via la factory function
app = create_app()

# Définir la clé secrète pour les sessions
app.config['SECRET_KEY'] = os.urandom(24)  # Vous pouvez aussi définir une clé manuellement si vous le souhaitez

# Enregistrer le blueprint
#app.register_blueprint(main_blueprint)

# Route d'index
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    # Lancer l'application Flask en mode debug
    app.run(debug=True, port=5003)
