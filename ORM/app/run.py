# Inicializar o app flask posteriomente
from flask import Flask
from routes import routes
from flask_cors import CORS

app = Flask(__name__, template_folder="views", static_folder="views/static")
app.register_blueprint(routes)

CORS(app) 

if __name__ == "__main__":
    app.run(debug=True)

