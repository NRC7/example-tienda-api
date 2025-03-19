import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta

# Cargar las variables de entorno
load_dotenv()

# Configuración de Redis para Flask-Limiter
redis_host = os.getenv("REDIS_STORAGE_URI", "memory://")

# Configuración inicial de Flask-Limiter
limiter = Limiter(key_func=get_remote_address, storage_uri=redis_host, strategy="moving-window")

# Configuración de MongoDB
mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    # Configuración de CORS
    CORS(app, supports_credentials=True)

    # Inicializar Flask-Limiter con la aplicación
    limiter.init_app(app)

    # Configuración de la base de datos
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    mongo.init_app(app)

    # Configuración de JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_COOKIE_SECURE"] = os.getenv("FLASK_ENV") == "production"  # True si está en producción
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 15)))
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 60)))

    jwt = JWTManager(app)

    # Manejo del error 429 (Too Many Requests)
    @app.errorhandler(429)
    def ratelimit_error(error):
        return jsonify({"code": "429", "message": "Too many requests, please try again later."}), 429

    # Registrar Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app

# Asegurar que usa el puerto dinámico en Render
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
