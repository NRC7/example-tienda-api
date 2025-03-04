from flask import Blueprint, request, jsonify, make_response
from .crud import (
    get_users, update_user, delete_user, register_user, get_user_by_username, get_user_by_id,
    get_products_from_mongo, deactivate_product, update_product, get_product_by_sku,
    create_product, get_products_by_category, get_products_by_subCategory,
    get_banner_images_from_mongo
)
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest, NotFound
from sqlalchemy.exc import IntegrityError
from middlewares.middlewares import jwt_required_middleware
from app import mongo, limiter
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
    return jsonify({"code": "400", "message": f"Database integrity error: {str(e)}"}), 400

@main.errorhandler(HTTPException)
def handle_http_error(e):
    return jsonify({"code": e.code, "message": e.description}), e.code

@main.errorhandler(Exception)
def handle_generic_error(e):
    return jsonify({"code": "500", "message": f"Internal server error: {str(e)}"}), 500


# Endpoint para obtener todos los productos
@main.route('/products', methods=['GET'])
# @limiter.limit("2 per minute")  
# @cross_origin(origins="http://localhost:3000")
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


# Endpoint para obtener todos los productos de una categoria
@main.route('/products/<string:product_category>', methods=['GET'])
# @cross_origin(origins="http://localhost:3000")
def get_products_by_category_route(product_category):
    try:
        # Delegar la consulta a MongoDB
        product_list = get_products_by_category(mongo, product_category)
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


# Endpoint para obtener todos los productos de una subCategoria
@main.route('/products/<string:product_category>/<string:product_subCategory>', methods=['GET'])
# @cross_origin(origins="http://localhost:3000")
def get_products_by_subCategory_route(product_category, product_subCategory):
    try:
        # Delegar la consulta a MongoDB
        product_list = get_products_by_subCategory(mongo, product_category, product_subCategory)
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


# Obtener un producto por su SKU
@main.route('/products/bysku/<string:product_sku>', methods=['GET'])
def get_product_by_sku_route(product_sku: str):
    try:
        product = get_product_by_sku(mongo, str(product_sku))
        if not product:
            raise NotFound("Producto no encontrado")

        return jsonify({"code": "200", "message": "Producto obtenido exitosamente", "data": product}), 200
    except NotFound as e:
        return handle_not_found_error(e)
    except Exception as e:
        return handle_generic_error(e)


# Obtener listado de imagenes
@main.route('/banner_images', methods=['GET'])
# @cross_origin(origins="http://localhost:3000")
def get_banner_images_route():
    try:
        # Delegar la consulta a MongoDB
        banner_images_list = get_banner_images_from_mongo(mongo)
        return jsonify({    
            "code": "200",
            "len": len(banner_images_list),
            "message": "Imagenes obtenidas exitosamente",
            "data": banner_images_list
        }), 200

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": f"Error al obtener imagenes: {str(e)}"
        }), 500


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
@main.route('/products/<string:product_sku>', methods=['PUT'])
@jwt_required_middleware(role="admin")
def update_product_route(product_sku):
    try:
        update_data = request.get_json()
        if not update_data:
            raise BadRequest("Datos de actualización no proporcionados")

        updated_product = update_product(mongo, product_sku, update_data)
        if not updated_product:
            raise NotFound("Producto no encontrado")

        return jsonify({"code": "200", "message": "Producto actualizado exitosamente", "data": updated_product}), 200
    except BadRequest as e:
        return handle_bad_request_error(e)
    except NotFound as e:
        return handle_not_found_error(e)
    except Exception as e:
        return handle_generic_error(e)


# Desactivar un producto
@main.route('/products/<string:product_sku>', methods=['DELETE'])
#@jwt_required_middleware(role="admin")
def deactivate_product_route(product_sku):
    try:
        deactivated = deactivate_product(mongo, product_sku)
        if not deactivated:
            raise NotFound("Producto no encontrado")

        return jsonify({"code": "200", "message": "Producto desactivado exitosamente"}), 200
    except NotFound as e:
        return handle_not_found_error(e)
    except Exception as e:
        return handle_generic_error(e)





## RUTAS PARA USER ##
# Endpoint para registrar usuarios
@main.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('user_name')
        email = data.get('email')
        #password = data.get('password')
        hashed_password = generate_password_hash(data.get('password')) 
        role = 'user'

        if not all([name, email, hashed_password]):
            return jsonify({"code": "400", "message": "Missing required fields"}), 400

        user = register_user(mongo, name, email, hashed_password, role)
        
        return jsonify({"code": "201", "message": f"User registered: {user.get('userName')}"}), 201
    except IntegrityError as e:
        return handle_integrity_error(e)

# Endpoint para login
@main.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        userName = data.get('user_name')
        password = data.get('password')

        if not all([userName, password]):
            return jsonify({"code": "400", "message": "Invalid credentials"}), 400

        user = get_user_by_username(mongo, userName)
        if not isinstance(user, dict) or not user or not check_password_hash(user.get('password'), password):
            return jsonify({"code": "401", "message": "Invalid credentials"}), 401  
        
        access_token = create_access_token(identity=str(user.get('_id')), fresh=True)
        refresh_token = create_refresh_token(identity=str(user.get('_id')))

        response = make_response(
            jsonify({
                "code": "200",
                "message": "Login successful",
                "access_token": access_token
            }),
            200
        )

        response.set_cookie(
            'refresh_token_cookie', 
            refresh_token, 
            httponly=True, 
            secure=False,  # Si https True
            samesite='Lax',
            max_age=1800  # Duración de la cookie (0.5 horas, por ejemplo)
        )

        return response
    except Exception as e:
        return handle_generic_error(e)

@main.route("/refresh", methods=["POST"])
@jwt_required_middleware(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        new_access_token = create_access_token(identity=identity, fresh=True)
        return jsonify({
                    "code": "200",
                    "message": "Refresh successful",
                    "access_token": new_access_token
                })
    except Exception as e:
        return handle_generic_error(e)   


# Endpoint para obtener lista de usuarios
@main.route('/users', methods=['GET'])
@jwt_required_middleware(role="admin")
def get_users_route():
    try:
        users = [user for batch in get_users(batch_size=100) for user in batch]
        data = [{"id": user.id, "name": user.name, "email": user.email, "role": user.role} for user in users]
        return jsonify({"code": "200", "message": "Users retrieved successfully.", "data": data}), 200
    except Exception as e:
        return handle_generic_error(e)


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



