from flask import Blueprint, request, jsonify
from .crud import (
    get_users, update_user, delete_user, register_user, get_user_by_email,
    get_products_from_mongo, delete_product, update_product, get_product_by_id,
    create_product
)
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, NotFound
from app.models import User
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from middlewares.middlewares import jwt_required_middleware
import re
from app import mongo
from flask_cors import cross_origin
from pymongo.errors import PyMongoError
from http.client import HTTPException


main = Blueprint('main', __name__)


# Handlers para errores
@main.errorhandler(BadRequest)
def handle_bad_request_error(e):
    return jsonify({"code": "500", "message": f"BadRequest: {str(e)}"}), 500

@main.app_errorhandler(Exception)
def handle_generic_error(e):
    return jsonify({"code": "500", "message": f"Error interno del servidor: {str(e)}"}), 500

@main.app_errorhandler(PyMongoError)
def handle_pymongo_error(e):
    return jsonify({"code": "500", "message": f"Error de base de datos: {str(e)}"}), 500

@main.app_errorhandler(404)
def handle_not_found_error(e):
    return jsonify({"code": "404", "message": "Recurso no encontrado"}), 404

@main.errorhandler(IntegrityError)
def handle_integrity_error(e):
    return jsonify({"code": "400", "message": "Database integrity error."}), 400

@main.errorhandler(HTTPException)
def handle_http_error(e):
    return jsonify({"code": e.code, "message": e.description}), e.code

@main.errorhandler(Exception)
def handle_generic_error(e):
    return jsonify({"code": "500", "message": f"Internal server error: {str(e)}"}), 500


# Endpoint para obtener todos los productos
@main.route('/products', methods=['GET'])
@cross_origin(origins="http://localhost:3000")
def get_products():
    try:
        # Delegar la consulta a MongoDB
        product_list = get_products_from_mongo(mongo)
        return jsonify({
            "code": "200",
            "len": len(product_list),
            "message": "Productos obtenidos exitosamente",
            "data": product_list
        }), 200

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": f"Error al obtener productos: {str(e)}"
        }), 500


# Obtener un producto por su ID
@main.route('/products/<string:product_id>', methods=['GET'])
def get_product_route(product_id):
    try:
        product = get_product_by_id(mongo, product_id)
        if not product:
            raise NotFound("Producto no encontrado")

        return jsonify({"code": "200", "message": "Producto obtenido exitosamente", "data": product}), 200
    except NotFound as e:
        return handle_not_found_error(e)
    except Exception as e:
        return handle_generic_error(e)


# Crear un nuevo producto
@main.route('/products', methods=['POST'])
@jwt_required_middleware(role="admin")
def create_product_route():
    try:
        product_data = request.get_json()
        if not product_data:
            raise BadRequest("Datos del producto no proporcionados")

        new_product = create_product(mongo, product_data)
        return jsonify({"code": "201", "message": "Producto creado exitosamente", "data": new_product}), 201
    except BadRequest as e:
        return handle_bad_request_error(e)
    except Exception as e:
        return handle_generic_error(e)


# Actualizar un producto
@main.route('/products/<string:product_id>', methods=['PUT'])
@jwt_required_middleware(role="admin")
def update_product_route(product_id):
    try:
        update_data = request.get_json()
        if not update_data:
            raise BadRequest("Datos de actualización no proporcionados")

        updated_product = update_product(mongo, product_id, update_data)
        if not updated_product:
            raise NotFound("Producto no encontrado")

        return jsonify({"code": "200", "message": "Producto actualizado exitosamente", "data": updated_product}), 200
    except BadRequest as e:
        return handle_bad_request_error(e)
    except NotFound as e:
        return handle_not_found_error(e)
    except Exception as e:
        return handle_generic_error(e)


# Eliminar un producto
@main.route('/products/<string:product_id>', methods=['DELETE'])
@jwt_required_middleware(role="admin")
def delete_product_route(product_id):
    try:
        deleted = delete_product(mongo, product_id)
        if not deleted:
            raise NotFound("Producto no encontrado")

        return jsonify({"code": "200", "message": "Producto eliminado exitosamente"}), 200
    except NotFound as e:
        return handle_not_found_error(e)
    except Exception as e:
        return handle_generic_error(e)
    

# Endpoint para registrar usuarios
@main.route('/register', methods=['POST'])
def register():
    try:
        # Intentar crear un nuevo usuario
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'jugador')  # Por defecto, todos son jugadores

        # Verificar que todos los campos estén presentes
        if not name or not email or not password:
            return jsonify({
                "code": "400",
                "message": "Faltan datos obligatorios: nombre, correo o contraseña"
            }), 400
        
        # Validar formato del correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({
                "code": "400",
                "message": "El correo electrónico no es válido"
            }), 400

        # Validar que el rol sea válido
        if role not in ['admin', 'jugador']:
            return jsonify({
                "code": "400",
                "message": "El rol debe ser 'admin' o 'jugador'"
            }), 400
        
        # Verificar si el correo electrónico ya está registrado
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                "code": "400",
                "message": "El correo electrónico ya está registrado"
            }), 400

        # Registrar usuario en la base de datos
        user = register_user(name, email, generate_password_hash(password), role)

        return jsonify({"code": "201", "message": "Usuario registrado", "user": {"id": user.id, "name": user.name, "role": user.role}}), 201

    except IntegrityError as e:
        # Si hay un error de integridad (como clave duplicada)
        return jsonify({
            "code": "400",
            "message": "El usuario ya existe"
        }), 400

    except Exception as e:
        # Manejo de otros errores internos
        return jsonify({
            "code": "500",
            "message": f"Faltan datos necesarios {e}"
        }), 500
    

# Endpoint para login
@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validar que el correo y la contraseña estén presentes
    if not email or not password:
        return jsonify({"code": "400", "message": "Correo y contraseña son requeridos"}), 400

    # Validar formato del correo electrónico
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"code": "400", "message": "El correo electrónico no es válido"}), 400

    # Buscar al usuario por email
    user = get_user_by_email(email)
    
    # Si no se encuentra el usuario o la contraseña es incorrecta
    if not user or not check_password_hash(user.password, password):
        return jsonify({"code": "401", "message": "Credenciales inválidas"}), 401

    # Crear el token de acceso con identidad como el ID del usuario (convertido a string)
    access_token = create_access_token(
        identity=str(user.id),  # Asegurarse de que identity sea una cadena
        expires_delta=timedelta(minutes=30)  # El token expirará en 1 minuto
    )

    return jsonify({
        "code": "200",
        "message": "Login exitoso",
        "token": access_token
    }), 200


# Endpoint para obtener lista de usuarios
@main.route('/users', methods=['GET'])
@jwt_required_middleware(role="admin")
def get_users_route():
    users = get_users()
    return jsonify({
        "code": "200",
        "message": "Usuarios recuperados exitosamente",
        "data": [
            {"id": user.id, "name": user.name, "email": user.email, "rol": user.role} for user in users
        ]
    }), 200


# Endpoint para actualizar un usuario
@main.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required_middleware(role="admin")
def update_user_route(user_id):

    data = request.get_json()

    updated_user = update_user(user_id, data)

    if not updated_user:
        return jsonify({
            "code": "404",
            "message": "Usuario no encontrado"
    }), 404

    return jsonify({
        "code": "200",
        "message": "Usuario actualizado exitosamente",
        "data": {
            "id": updated_user.id,
            "name": updated_user.name,
            "email": updated_user.email,
            "role": updated_user.role
        }
    }), 200


# Endpoint para borrar un usuario
@main.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required_middleware(role="admin")
def delete_user_route(user_id):
    if not delete_user(user_id):

        return jsonify({"code": "404", "message": "Usuario no encontrado"}), 404
    
    return jsonify({"code": "200", "message": "Usuario eliminado exitosamente"}), 200



