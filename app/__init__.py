import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from .database import db
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configuraion inicial Flask-Limiter (máximo de solicitudes por minuto por IP)
limiter = Limiter(key_func=get_remote_address)  # NO PASAMOS 'app' AQUÍ

# Cargar las variables de entorno
load_dotenv()

# Configuración de MongoDB
mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    # Permitir solicitudes desde el origen de tu frontend (React)
    # CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})
    app.config["CORS_ORIGINS"] = ["http://localhost:5000"]  
    CORS(app)

    # Inicializar Flask-Limiter con la aplicación
    limiter.init_app(app)

    # Configuración de la base de datos
    # Si se borra la DB al reemplazar el nombre en el string usar "_" no "-" porque mongo los trata como char de rest
    app.config["MONGO_URI"] = "mongodb+srv://admin_db:topolino@db-cluster-bp.thr7b8f.mongodb.net/db_bp_products?retryWrites=true&w=majority"
    mongo.init_app(app)

    # Crear rutas a la db en la raíz
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, '..', 'trivia.db')

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, '..', 'trivia.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración de JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # Inicializar extensiones db
    db.init_app(app)

    # Crear la base de datos automáticamente si no existe
    # if not os.path.exists(db_path):
    with app.app_context():
        db.create_all()

    # Inicializar extensiones jwt        
    jwt = JWTManager(app)

    # Manejo de error cuando un token expira
    @jwt.expired_token_loader
    def expired_token_callback(error, response=None):
        return jsonify({
            "code": "401",
            "message": "La sesión ha caducado, por favor inicia sesión nuevamente."
        }), 401

    # Manejo de error cuando no se proporciona un token o es inválido
    @jwt.unauthorized_loader
    def unauthorized_callback(error, response=None):
        return jsonify({
            "code": "401",
            "message": "No se ha proporcionado un token válido o el token ha expirado."
        }), 401

    # Manejo de error cuando el token es inválido
    @jwt.invalid_token_loader
    def invalid_token_callback(error, response=None):
        return jsonify({
            "code": "401",
            "message": "El token es inválido."
        }), 401

    # Registrar Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
