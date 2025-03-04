from .services import serialize_mongo_document, validate_product_data, validate_user_data, validate_and_filter_update_data
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


# Consultar productos desde MongoDB
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

# Consultar imagenes del banner desde MongoDB
def get_banner_images_from_mongo(mongo: PyMongo):
    banner_images = mongo.db.bannerImages.find()
    return [
        {
            "name": image.get("name"),
            "imageResources": image.get("imageResources")
        }
        for image in banner_images
    ]

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
        # Manejar errores de validación
        raise Exception(f"Error de validación: {e}")
    except Exception as e:
        raise Exception(f"Error al crear el producto: {e}")


# Obtener un producto por su SKU
def get_product_by_sku(mongo: PyMongo, product_sku: str):
    try:
        #product = mongo.db.products.find_one({"sku": product_sku})
        return serialize_mongo_document(mongo.db.products.find_one({"sku": product_sku}))
    except Exception as e:
        raise Exception(f"Error al obtener el producto: {e}")
    
# Obtener todos los productos de una categoria
def get_products_by_category(mongo: PyMongo, product_category: str):
    try:
        products = [product for product in get_products_from_mongo(mongo) if product["category"] == product_category]
        return products
    except Exception as e:
        raise Exception(f"Error al obtener productos por categoria: {e}")

# Obtener todos los productos de una sub categoria
def get_products_by_subCategory(mongo: PyMongo, product_category: str, product_subCategory: str):
    try:
        products = [product for product in get_products_by_category(mongo, product_category) if product["subCategory"] == product_subCategory]
        return products
    except Exception as e:
        raise Exception(f"Error al obtener productos por subCategoria: {e}")         


# Actualizar un producto por su SKU
def update_product(mongo: PyMongo, product_sku: str, update_data: dict):
    try:
        # Validar y filtrar los datos antes de la actualización
        filtered_data = validate_and_filter_update_data(update_data)
        # Realizar la actualización con los datos filtrados
        result = mongo.db.products.update_one({"sku": product_sku}, {"$set": filtered_data})
        if result.matched_count == 0:
            return None
        return serialize_mongo_document(
            mongo.db.products.find_one({"sku": product_sku})
        )
    except Exception as e:
        raise Exception(f"Error al actualizar el producto: {e}")


# Eliminar un producto por su ID
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
        raise Exception(f"Error al desactivar el producto: {e}")


## CRUD PARA USER ##
# Registrar un usuario
def register_user(mongo: PyMongo, name: str, email: str, hashed_password: str, role: str):
    try:
        # Crear dict para validacion
        user_data = {
        "userName": name,
        "email": email,
        "password": hashed_password,
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
        # Manejar errores de validación
        raise Exception(f"Error de validación: {e}")
    except Exception as e:
        raise Exception(f"Error al crear el producto: {e}")


# Obtener un usuario por username
def get_user_by_username(mongo: PyMongo, userName: str):
    try:
        #product = mongo.db.products.find_one({"sku": product_sku})
        return serialize_mongo_document(mongo.db.users.find_one({"userName": userName}))
    except Exception as e:
        raise Exception(f"Error al obtener el user: {e}")

# Obtener un usuario por _id
def get_user_by_id(mongo: PyMongo, _id: str):
    try:
        #product = mongo.db.products.find_one({"sku": product_sku})
        return serialize_mongo_document(mongo.db.users.find_one({"_id": ObjectId(_id)}))
    except Exception as e:
        raise Exception(f"Error al obtener el user: {e}")    
    

# Obtener todos los usuarios con batch fetching
def get_users():
    return True


# Actualizar un usuario
def update_user(user_id, new_data):
    user = user_id
    if not user:
        return None
    for key, value in new_data.items():
        setattr(user, key, value)
    return user


# Borrar un usuario
def delete_user(user_id):
    user = user_id
    if not user:
        return False
    return True

