import os
from flask import Blueprint, request, jsonify, make_response
from .crud import (
    get_users, update_user, delete_user, register_user, get_user_by_email, update_order_status,
    get_products_from_mongo, deactivate_product, update_product, get_product_by_sku, get_categories_from_mongo,
    create_product, get_products_by_category, get_products_by_subCategory, get_user_by_id,
    get_banner_images_from_mongo, create_checkout, get_orders_from_mongo, get_orders_by_user, update_user
)
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from middlewares.middlewares import jwt_required_middleware
from app import mongo, limiter
from handlers.error_handler import ErrorHandler
from datetime import datetime


main = Blueprint('main', __name__)


## RUTAS APP ##

# Endpoint para obtener todos los productos
@main.route('/api/v1/products', methods=['GET'])
@limiter.limit("5 per minute")  
def get_products():
    try:
        product_list = get_products_from_mongo(mongo)
        return jsonify({
            "code": "200",
            "len": len(product_list),
            "message": "Fetch products successfully",
            "data": product_list
        }), 200
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error fetching products r: {str(e)}")

# Obtener listado de imagenes
@main.route('/api/v1/banner_images', methods=['GET'])
@limiter.limit("5 per minute")  
def get_banner_images_route():
    try:
        banner_images_list = get_banner_images_from_mongo(mongo)
        return jsonify({    
            "code": "200",
            "len": len(banner_images_list),
            "message": "Fetch images successfully",
            "data": banner_images_list
        }), 200
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error fetching images r: {str(e)}")

@main.route('/api/v1/categories', methods=['GET'])
@limiter.limit("5 per minute")  
def get_categories():
    try:
        categories = get_categories_from_mongo(mongo)
        return jsonify({
            "code": "200",
            "len": len(categories),
            "message": "Fetch categories successfully",
            "data": categories
        }), 200
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error fetching products r: {str(e)}")

# Endpoint para registrar usuarios
@main.route('/api/v1/register', methods=['POST'])
@limiter.limit("2 per minute")  
def register():
    try:
        data = request.get_json()
        name = data.get('user_name')
        email = data.get('email')
        address = data.get('address')
        dateOfBirth = data.get('dateOfBirth')
        hashed_info = generate_password_hash(data.get('info')) 
        role = 'user'

        if not all([name, email, address, dateOfBirth, hashed_info]):
            return ErrorHandler.bad_request_error("Missing required fields r")
        
        existingUser = get_user_by_email(mongo, email)
        if existingUser: 
            return ErrorHandler.not_acceptable_error("Email already exist r")    
        print(f'data: {data}')
        user = register_user(mongo, name, email, address, dateOfBirth, hashed_info, role)

        return jsonify({"code": "201", "message": f"User registered successfully: {user.get('userName')}"}), 201
    except Exception as e:
        return ErrorHandler.internal_server_error(f"error when registering user r: {str(e)}")

# Endpoint para login
@main.route('/api/v1/login', methods=['POST'])
@limiter.limit("3 per 2 minute") 
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        info = data.get('info')

        if not all([email, info]):
            return ErrorHandler.bad_request_error("Missing required credentials r")

        user = get_user_by_email(mongo, email)

        if not isinstance(user, dict) or not user: 
            return ErrorHandler.not_found_error("User does not exist r")
        
        if not check_password_hash(user.get('password'), info):
            return ErrorHandler.invalid_credentials_error("r")
        
        user.pop('password', None)

        access_token = create_access_token(identity=str(user.get('_id')), fresh=True)
        refresh_token = create_refresh_token(identity=str(user.get('_id')))

        response = make_response(
            jsonify({
                "code": "200",
                "message": "Login successful",
                "access_token": access_token,
                "data": {
                    "_id": user.get('_id'),
                    "email": user.get('email'),
                    "userName": user.get('userName'),
                    "address": user.get('address'),
                    "dateOfBirth": user.get('dateOfBirth')
                }
            }),
            200
        )

        response.set_cookie(
            'refresh_token_cookie', 
            refresh_token, 
            httponly=True, 
            secure=os.getenv("COOKIE_SECURE"),  # Si https True
            samesite='Lax',
            max_age=86400  # Duración de la cookie (0.5 horas, por ejemplo)
        )

        return response
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error during authentication r: {str(e)}")

@main.route("/api/v1/logout", methods=["POST"])
@jwt_required_middleware(location=['headers'])
def logout():
    try:
        response = make_response(
                jsonify({
                    "code": "200",
                    "message": "Logout successful"
                }),
                200
            )
        response.set_cookie(
            "refresh_token_cookie", 
            "",  # Dejar la cookie vacía
            httponly=True, 
            secure=os.getenv("COOKIE_SECURE"),  # Si usas HTTPS
            samesite="Lax", 
            max_age=0  # Expirar la cookie inmediatamente
        )
        return response
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error procesing logout r: {str(e)}")

# Endpoint para generar nuevo token de acceso
@main.route("/api/v1/refresh", methods=["POST"])
@limiter.limit("2 per 5 minute")  
@jwt_required_middleware(refresh=True, location=['cookies'])
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
        return ErrorHandler.internal_server_error(f"Error when refresing r: {str(e)}")
    
# Actualizar un usuario
@main.route('/api/v1/user/edit', methods=['PUT'])
@limiter.limit("2 per 5 minute")  
@jwt_required_middleware(location=['headers'], role="user")
def update_user_route():
    try:
        update_data = request.get_json()
        if not update_data:
            return ErrorHandler.bad_request_error("Missing fields r")
        
        if get_jwt_identity() != str(update_data.get("_id")):
            return ErrorHandler.conflict_error("Identities do not match r")
        
        updated_user = update_user(mongo, update_data)
        
        if not updated_user:
            return ErrorHandler.not_found_error("User not found r")

        return jsonify({"code": "201", "message": "User updated successfully", "data": updated_user}), 201
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error during updating user r: {str(e)}")
    
# Actualizar un data de un user
@main.route('/api/v1/user/data', methods=['PUT'])
@limiter.limit("2 per 5 minute")  
@jwt_required_middleware(location=['headers'], role="user")
def update_user_data_route():
    try:
        update_data = request.get_json()
        if not update_data:
            return ErrorHandler.bad_request_error("Missing fields r")
        
        if get_jwt_identity() != str(update_data.get("_id")):
            return ErrorHandler.conflict_error("Identities do not match r")
        
        hashed_info = generate_password_hash(update_data.get('info')) 

        update_data.pop('info', None)
        update_data["password"] = hashed_info
        
        updated_user = update_user(mongo, update_data)

        if not updated_user:
            return ErrorHandler.not_found_error("User not found r") 

        return jsonify({"code": "201", "message": "User data updated successfully", "data": "ok"}), 201
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error during updating user data r: {str(e)}")    
    
# Endpoint para obtener lista de usuarios
# @main.route('/users', methods=['GET'])
# @limiter.limit("2 per minute") 
# @jwt_required_middleware(role="admin")
# @jwt_required_middleware(location=['headers'])
# def get_users_route():
#     try:
#         user_list = get_users(mongo)
#         return jsonify({
#             "code": "200",
#             "len": len(user_list),
#             "message": "Fetch users successfully",
#             "data": user_list
#         }), 200

#     except Exception as e:
#         return ErrorHandler.internal_server_error(f"Error fetching users r: {str(e)}")

# Endpoint para procesar el checkout
@main.route('/api/v1/checkout', methods=['POST'])
@limiter.limit("2 per minute") 
@jwt_required_middleware(location=['headers'], role="user")
def checkout():
    try:
        checkout_data = request.get_json()

        if not checkout_data:
            return ErrorHandler.bad_request_error("Missing mandatory fields r")

        if not get_user_by_id(mongo, get_jwt_identity()):
            return ErrorHandler.not_found_error("User not found r")

        checkout_data["trxDate"] = datetime.today()
        checkout_data["status"] = "pending"
        checkout_data["lastStatusModificationDate"] = datetime.today()
        print(f'trxDate {checkout_data.get("trxDate")}')
        print(f'lastStatusModificationDate {checkout_data.get("lastStatusModificationDate")}')
        new_checkout = create_checkout(mongo, checkout_data)
        print(f'new_trxDate {new_checkout.get("trxDate")}')
        print(f'new_lastStatusModificationDate {new_checkout.get("lastStatusModificationDate")}')
        return jsonify({"code": "201", "message": "Order created successfully", "data": new_checkout}), 201
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error procesing order r: {str(e)}")
    
# Actualizar estado del pedido
# @main.route('/order/status/edit', methods=['PUT'])
# @limiter.limit("2 per 5 minute")  
# @jwt_required_middleware(location=['headers'])
# def update_order_status_route():
#     try:
#         update_data = request.get_json()
#         if not update_data:
#             return ErrorHandler.bad_request_error("Missing fields r")
        
#         updated_order = update_order_status(mongo, update_data)
#         if not updated_order:
#             return ErrorHandler.not_found_error("Updated order not found r")
#         elif not hasattr(updated_order, 'code'):
#             # print(updated_order)
#             code = updated_order["code"]
#             message = updated_order["message"]
#             return ErrorHandler.bad_request_error(f"{code} {message} r")

#         return jsonify({"code": "200", "message": "Order status updated successfully", "data": updated_order}), 200
#     except Exception as e:
#         return ErrorHandler.internal_server_error(f"Error during updating order status r: {str(e)}")    
    
@main.route('/api/v1/orders/user', methods=['GET'])
@limiter.limit("2 per minute") 
@jwt_required_middleware(location=['headers'])
def get_orders_by_user_route():
    try:
        identity = get_jwt_identity()
        orders = get_orders_by_user(mongo, identity)
        return jsonify({    
            "code": "200",
            "len": len(orders),
            "message": "Fetching orders successfully",
            "data": orders
        }), 200
    except Exception as e:
        return ErrorHandler.internal_server_error(f"Error fetching orders r: {str(e)}")

# import requests
# @main.route("/server-ip", methods=["GET"])
# def get_server_ip():
#     try:
#         ip = requests.get("https://ifconfig.me").text
#         return jsonify({"server_ip": ip})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

## RUTAS ADMIN ##

# # Endpoint para obtener todos los productos de una categoria
# @main.route('/products/<string:product_category>', methods=['GET'])
# @limiter.limit("2 per minute") 
# def get_products_by_category_route(product_category):
#     try:
#         # Delegar la consulta a MongoDB
#         product_list = get_products_by_category(mongo, product_category)
#         return jsonify({
#             "code": "200",
#             "len": len(product_list),
#             "message": "Productos obtenidos exitosamente",
#             "data": product_list
#         }), 200

#     except Exception as e:
#         return jsonify({
#             "code": "500",
#             "message": f"Error al obtener productos: {str(e)} r"
#         }), 500    

# # Endpoint para obtener todos los productos de una subCategoria
# @main.route('/products/<string:product_category>/<string:product_subCategory>', methods=['GET'])
# @limiter.limit("2 per minute") 
# def get_products_by_subCategory_route(product_category, product_subCategory):
#     try:
#         # Delegar la consulta a MongoDB
#         product_list = get_products_by_subCategory(mongo, product_category, product_subCategory)
#         return jsonify({
#             "code": "200",
#             "len": len(product_list),
#             "message": "Productos obtenidos exitosamente",
#             "data": product_list
#         }), 200

#     except Exception as e:
#         return jsonify({
#             "code": "500",
#             "message": f"Error al obtener productos: {str(e)} r"
#         }), 500        

# # Obtener un producto por su SKU
# @main.route('/products/bysku/<string:product_sku>', methods=['GET'])
# @limiter.limit("2 per minute") 
# def get_product_by_sku_route(product_sku: str):
#     try:
#         product = get_product_by_sku(mongo, str(product_sku))
#         if not product:
#             raise NotFound("Producto no encontrado")

#         return jsonify({"code": "200", "message": "Producto obtenido exitosamente", "data": product}), 200
#     except NotFound as e:
#         return handle_not_found_error(e)
#     except Exception as e:
#         return handle_generic_error(e)

# # Crear un nuevo producto
# @main.route('/products', methods=['POST'])
# @limiter.limit("2 per minute") 
# @jwt_required_middleware(role="admin")
# def create_product_route():
#     try:
#         product_data = request.get_json()
#         if not product_data:
#             raise BadRequest("Datos del producto no proporcionados")

#         new_product = create_product(mongo, product_data)
#         return jsonify({"code": "201", "message": "Producto creado exitosamente", "data": new_product}), 201
#     except BadRequest as e:
#         return handle_bad_request_error(e)
#     except Exception as e:
#         return handle_generic_error(e)

# # Actualizar un producto
# @main.route('/products/<string:product_sku>', methods=['PUT'])
# @limiter.limit("2 per minute") 
# @jwt_required_middleware(role="admin")
# def update_product_route(product_sku):
#     try:
#         update_data = request.get_json()
#         if not update_data:
#             raise BadRequest("Datos de actualización no proporcionados")

#         updated_product = update_product(mongo, product_sku, update_data)
#         if not updated_product:
#             raise NotFound("Producto no encontrado")

#         return jsonify({"code": "200", "message": "Producto actualizado exitosamente", "data": updated_product}), 200
#     except BadRequest as e:
#         return handle_bad_request_error(e)
#     except NotFound as e:
#         return handle_not_found_error(e)
#     except Exception as e:
#         return handle_generic_error(e)

# # Desactivar un producto
# @main.route('/products/<string:product_sku>', methods=['DELETE'])
# @limiter.limit("2 per minute") 
# @jwt_required_middleware(role="admin")
# def deactivate_product_route(product_sku):
#     try:
#         deactivated = deactivate_product(mongo, product_sku)
#         if not deactivated:
#             raise NotFound("Producto no encontrado")

#         return jsonify({"code": "200", "message": "Producto desactivado exitosamente"}), 200
#     except NotFound as e:
#         return handle_not_found_error(e)
#     except Exception as e:
#         return handle_generic_error(e)

# # Endpoint para borrar un usuario
# @main.route('/users/<int:user_id>', methods=['DELETE'])
# @limiter.limit("2 per minute") 
# @jwt_required_middleware(role="admin")
# def delete_user_route(user_id):
#     if not delete_user(user_id):

#         return jsonify({"code": "404", "message": "Usuario no encontrado r"}), 404
    
#     return jsonify({"code": "200", "message": "Usuario eliminado exitosamente"}), 200

# @main.route('/orders', methods=['GET'])
# @limiter.limit("2 per minute") 
# @jwt_required_middleware(location=['headers'], role="admin")
# def get_orders():
#     try:
#         orders = get_orders_from_mongo(mongo)
#         return jsonify({    
#             "code": "200",
#             "len": len(orders),
#             "message": "Orders obtenidas exitosamente",
#             "data": orders
#         }), 200
#     except Exception as e:
#         return handle_generic_error(e)