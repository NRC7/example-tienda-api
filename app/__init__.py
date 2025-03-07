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

# Conectar con Redis
redis_host = os.getenv("REDIS_STORAGE_URI") if os.getenv("FLASK_ENV") == "production" else "memory://"
# redis_client = redis.Redis(host="redis", port=6379, db=0)

# Configuraion inicial Flask-Limiter (máximo de solicitudes por minuto por IP)
# Usa la IP del cliente para rate limiting,
# Indica que se usará Redis como backend
# print(os.getenv("REDIS_STORAGE_URI"))redis_host
limiter = Limiter(key_func=get_remote_address, storage_uri=redis_host,  strategy="moving-window",)

# Configuración de MongoDB
mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    # Permitir solicitudes desde el origen de tu frontend (React)
    # CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})
    if os.getenv("FLASK_ENV") == "development":
        app.config["CORS_ORIGINS"] = ["http://localhost:5000", "http://localhost:3000", "http://172.18.0.2:5000/"]  
        CORS(app)

    # Inicializar Flask-Limiter con la aplicación
    limiter.init_app(app)

    # Configuración de la base de datos
    # Si se borra la DB al reemplazar el nombre en el string usar "_" no "-" porque mongo los trata como char de rest
    #app.config["MONGO_URI"] = "mongodb+srv://admin_db:topolino@db-cluster-bp.thr7b8f.mongodb.net/db_bp_products?retryWrites=true&w=majority"
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    mongo.init_app(app)

    # Configuración de JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_COOKIE_SECURE"] = False  # Cambiar a True en producción si usas HTTPS
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False # Desactivar CSRF para tokens JWT
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(minutes=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES")))

    # Inicializar extensiones jwt        
    jwt = JWTManager(app)

    # Configura un manejador para el error 429 (Too Many Requests)
    @app.errorhandler(429)
    def ratelimit_error(error):
        return jsonify({"code": "429","message": "Too many requests, please try again later."}), 429

    # Registrar Blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
