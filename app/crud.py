from .services import (serialize_mongo_document, validate_product_data,
    validate_user_data, validate_update_order_status_data,
    validate_checkout_data, validate_and_filter_update_data)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from handlers.mongo_error_handler import ErrorHandlerMongo
from datetime import datetime

## CRUD APP ##

# Obtener productos
def get_products_from_mongo(mongo: PyMongo):
    products = mongo.db.products.find({"isActive": "true"})
    return [
        {
            "_id": str(product["_id"]),
            "sku": product.get("sku"),
            "name": product.get("name"),
            "category": product.get("category"),
            "normalPrice": product.get("normalPrice"),
            "rating": product.get("rating"),
            "dealPrice": product.get("dealPrice"),
            "discountPercentage": product.get("discountPercentage"),
            "imageResources": product.get("imageResources"),
            "subCategory": product.get("subCategory"),
            "description": product.get("description"),
            "freeShiping": product.get("freeShiping"),
            "isActive": product.get("isActive"),
            "uploadDateTime": product.get("uploadDateTime")
        }
        for product in products
    ]

# Obtener imagenes del banner
def get_banner_images_from_mongo(mongo: PyMongo):
    banner_images = mongo.db.bannerImages.find()
    return [
        {
            "name": image.get("name"),
            "imageResources": image.get("imageResources")
        }
        for image in banner_images
    ]

# Obtener categorias drawer
def get_categories_from_mongo(mongo: PyMongo):
    categories = mongo.db.categories.find()
    return [
        {
            "_id": str(category["_id"]),
            "name": category.get("name"),
            "subcategories": category.get("subcategories")
        }
        for category in categories
    ]

# Crear pedido
def create_checkout(mongo: PyMongo, checkout_data: dict):
    try:
        checkout_data["trxDate"] = datetime.now()
        checkout_data["status"] = "pending"
        checkout_data["lastStatusModificationDate"] = datetime.now()

        # Validar que todos los campos obligatorios estén presentes
        validate_checkout_data(checkout_data)

        result = mongo.db.orders.insert_one(checkout_data)

        # Obtener y serializar el documento recién creado
        return serialize_mongo_document(
            mongo.db.orders.find_one({"_id": result.inserted_id})
        )
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)
    
# Actualizar status del pedido
def update_order_status(mongo: PyMongo, update_data: dict):
    try:
        validation = validate_update_order_status_data(update_data)
        if validation:
            return validation.get_json()
        order_id = update_data.get("order_id")
        found_order = mongo.db.orders.find_one({"_id": ObjectId(order_id)})
        if not found_order:
            return None
        found_order["status"] = update_data.get("update_status")
        found_order["deliveryDate"] = update_data.get("delivery_date")
        found_order["lastStatusModificationDate"] = datetime.now()
        result = mongo.db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": found_order})
        if result.modified_count > 0:
            return serialize_mongo_document(
                mongo.db.orders.find_one({"_id": ObjectId(order_id)})
            )
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)    

# Obtener todos los pedidos de un user
def get_orders_by_user(mongo: PyMongo, id: str):
    user = get_user_by_id(mongo, id)
    orders = mongo.db.orders.find({"user": user.get("_id")})
    return [
        {
            "_id": str(order.get("_id")),
            "address": order.get("address"),
            "deliveryDate": str(order.get("deliveryDate")),
            "email": order.get("email"),
            "couponFactor": order.get("couponFactor"),
            "couponAmount": order.get("couponAmount"),
            "paymentMethod": order.get("paymentMethod"),
            "cartProducts": [
                {**product, "_id": str(product["_id"])}
                for product in order.get("cartProducts", [])
            ],
            "subTotalAmount": order.get("subTotalAmount"),
            "shippingCost": order.get("shippingCost"),
            "totalAmount": order.get("totalAmount"),
            "totalWithDiscountAmount": order.get("totalWithDiscountAmount"),
            "trxDate": str(order.get("trxDate")),
            "user": order.get("user"),
            "status": order.get("status"),
            "lastStatusModificationDate": order.get("lastStatusModificationDate")
        }
        for order in orders
    ]

# Obteners todos los pedidos
def get_orders_from_mongo(mongo: PyMongo):
    orders = mongo.db.orders.find()
    return [
        {
            "address": order.get("address"),
            "deliveryDate": order.get("deliveryDate"),
            "email": order.get("email"),
            "couponFactor": order.get("couponFactor"),
            "couponAmount": order.get("couponAmount"),
            "paymentMethod": order.get("paymentMethod"),
            "cartProducts": [
                {**product, "_id": str(product["_id"])}
                for product in order.get("cartProducts", [])
            ],
            "subTotalAmount": order.get("subTotalAmount"),
            "shippingCost": order.get("shippingCost"),
            "totalAmount": order.get("totalAmount"),
            "totalWithDiscountAmount": order.get("totalWithDiscountAmount"),
            "user": order.get("user"),
            "trxDate": order.get("trxDate"),
        }
        for order in orders
    ]

# Registrar un usuario
def register_user(mongo: PyMongo, name: str, email: str, address: str, dateOfBirth: str, hashed_info: str, role: str):
    try:
        # Crear dict para validacion
        user_data = {
        "userName": name,
        "email": email,
        "address": address,
        "dateOfBirth": dateOfBirth,
        "password": hashed_info,
        "role": role,
        }

        # Validar que todos los campos obligatorios estén presentes
        validate_user_data(user_data)

        result = mongo.db.users.insert_one(user_data)
        
        # Obtener y serializar el documento recién creado
        return serialize_mongo_document(
            mongo.db.users.find_one({"_id": result.inserted_id})
        )
    except ValueError as e:
        return ErrorHandlerMongo.handleDBError(e)

# Actualizar user
def update_user(mongo: PyMongo, update_data: dict):
    try:
        data_id = update_data.get("_id")
        update_data.pop("_id")

        validate_user_data(update_data)

        result = mongo.db.users.update_one({"_id": ObjectId(data_id)}, {"$set": update_data})
        # print(result.modified_count)
        if result.modified_count > 0:
            return serialize_mongo_document(
                mongo.db.users.find_one({"_id": ObjectId(data_id)})
            )
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)

# Obtener un user
def get_user_by_id(mongo: PyMongo, _id: str):
    try:
        #product = mongo.db.products.find_one({"sku": product_sku})
        return serialize_mongo_document(mongo.db.users.find_one({"_id": ObjectId(_id)}))
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)
    
# Obtener todos los user
def get_users(mongo: PyMongo):
    users = mongo.db.users.find()
    return [
        {
            "_id": str(user["_id"]),
            "userName": user.get("userName"),
            "email": user.get("email"),
            "address": user.get("address"),
            "dateOfBirth": user.get("dateOfBirth"),
            "role": user.get("role")
        }
        for user in users
    ]

# Obtener un usuario
def get_user_by_email(mongo: PyMongo, email: str):
    try:
        #product = mongo.db.products.find_one({"sku": product_sku})
        return serialize_mongo_document(mongo.db.users.find_one({"email": email}))
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)

# Desactivar un producto
def deactivate_product(mongo: PyMongo, product_sku: str):
    try:
        # Buscar y desactivar el producto por el campo "sku", no "_id"
        result = mongo.db.products.update_one({"sku": product_sku}, {"$set": {"isActive": "false"}})
        if result.matched_count == 0:
            return None
        return serialize_mongo_document(
            mongo.db.products.find_one({"sku": product_sku})
        )
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)

# Crear un producto
def create_product(mongo: PyMongo, product_data: dict):
    try:
        # Validar que todos los campos obligatorios estén presentes
        validate_product_data(product_data)

        # Calcular el próximo id como el total actual de documentos + 1
        next_id = str(mongo.db.products.count_documents({}) + 1)

        # Asignar el nuevo `id` al producto
        product_data["sku"] = next_id
        result = mongo.db.products.insert_one(product_data)

        # Obtener y serializar el documento recién creado
        return serialize_mongo_document(
            mongo.db.products.find_one({"_id": result.inserted_id})
        )
    except ValueError as e:
        return ErrorHandlerMongo.handleDBError(e)

# Obtener un producto por su SKU
def get_product_by_sku(mongo: PyMongo, product_sku: str):
    try:
        #product = mongo.db.products.find_one({"sku": product_sku})
        return serialize_mongo_document(mongo.db.products.find_one({"sku": product_sku}))
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)
    
# Obtener todos los productos de una categoria
def get_products_by_category(mongo: PyMongo, product_category: str):
    try:
        products = [product for product in get_products_from_mongo(mongo) if product["category"] == product_category]
        return products
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)

# Obtener todos los productos de una sub categoria
def get_products_by_subCategory(mongo: PyMongo, product_category: str, product_subCategory: str):
    try:
        products = [product for product in get_products_by_category(mongo, product_category) if product["subCategory"] == product_subCategory]
        return products
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)    

# Actualizar un producto por su SKU
def update_product(mongo: PyMongo, update_data: dict):
    try:
        validation = validate_and_filter_update_data(update_data)
        if validation:
            return validation.get_json()
        product_id = update_data.get("_id")
        update_data.pop("_id")
        update_data.pop("imageResources")
        update_data.pop("rating")
        update_data.pop("uploadDateTime")
        result = mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
        if result.modified_count > 0:
            return serialize_mongo_document(
                mongo.db.products.find_one({"_id": ObjectId(product_id)})
            )
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)

# Borrar un usuario
def delete_user(mongo: PyMongo, user_id: str):
    try:
        if not user_id:
            return False
        result = mongo.db.users.delete_one({"_id": user_id})
        if result.matched_count == 0:
            return False
        return True
    except Exception as e:
        return ErrorHandlerMongo.handleDBError(e)

# Borrar un producto
def delete_product(mongo: PyMongo, product_id: str):
    try:
        if not product_id:
            return {"success": False, "error": "Missing ID"}
        result = mongo.db.products.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            return {"success": False, "error": "Product not found"}
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Obtener todos los pedidos de un user    
def get_orders_by_user_id(mongo: PyMongo, user_id: str):
    orders = mongo.db.orders.find({"user": user_id})
    return [
        {
            "_id": str(order.get("_id")),
            "address": order.get("address"),
            "deliveryDate": str(order.get("deliveryDate")),
            "email": order.get("email"),
            "couponFactor": order.get("couponFactor"),
            "couponAmount": order.get("couponAmount"),
            "paymentMethod": order.get("paymentMethod"),
            "cartProducts": [
                {**product, "_id": str(product["_id"])}
                for product in order.get("cartProducts", [])
            ],
            "subTotalAmount": order.get("subTotalAmount"),
            "shippingCost": order.get("shippingCost"),
            "totalAmount": order.get("totalAmount"),
            "totalWithDiscountAmount": order.get("totalWithDiscountAmount"),
            "trxDate": str(order.get("trxDate")),
            "user": order.get("user"),
            "status": order.get("status"),
            "lastStatusModificationDate": order.get("lastStatusModificationDate")
        }
        for order in orders
    ]
