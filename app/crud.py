from .models import User
from .database import db
from .services import serialize_mongo_document, validate_product_data, validate_and_filter_update_data
from flask_pymongo import PyMongo
from pymongo import DESCENDING, MongoClient


# Registrar un usuario
def register_user(name, email, hashed_password, role="jugador"):
    user = User(name=name, email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return user


# Obtener un usuario por email
def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


# Obtener todos los usuarios con batch fetching
def get_users(batch_size=100):
    offset = 0
    while True:
        batch = User.query.offset(offset).limit(batch_size).all()
        if not batch:
            break
        yield batch
        offset += batch_size


# Actualizar un usuario
def update_user(user_id, new_data):
    user = User.query.get(user_id)
    if not user:
        return None
    for key, value in new_data.items():
        setattr(user, key, value)
    db.session.commit()
    return user


# Borrar un usuario
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return False
    db.session.delete(user)
    db.session.commit()
    return True


# Consultar productos desde MongoDB
def get_products_from_mongo(mongo: PyMongo):
    products = mongo.db.products.find()
    return [
        {
            "_id": str(product["_id"]),
            "id": product.get("id"),
            "name": product.get("name"),
            "category": product.get("category"),
            "normalPrice": product.get("normalPrice"),
            "rating": product.get("rating"),
            "dealPrice": product.get("dealPrice"),
            "discountPercentage": product.get("discountPercentage"),
            "imageResources": product.get("imageResources"),
            "subCategory": product.get("subCategory"),
            "description": product.get("description"),
            "freeShiping": product.get("freeShiping")
        }
        for product in products
    ]


# Crear un producto
def create_product(mongo: PyMongo, product_data: dict):
    try:
        # Validar que todos los campos obligatorios estén presentes
        validate_product_data(product_data)

        # Calcular el próximo id como el total actual de documentos + 1
        next_id = str(mongo.db.products.count_documents({}) + 1)

        # Asignar el nuevo `id` al producto
        product_data["id"] = next_id
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


# Obtener un producto por su ID
def get_product_by_id(mongo: PyMongo, product_id: str):
    try:
        product = mongo.db.products.find_one({"id": product_id})
        return serialize_mongo_document(product)
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


# Actualizar un producto por su ID
def update_product(mongo: PyMongo, product_id: str, update_data: dict):
    try:
        # Validar y filtrar los datos antes de la actualización
        filtered_data = validate_and_filter_update_data(update_data)
        # Realizar la actualización con los datos filtrados
        result = mongo.db.products.update_one({"id": product_id}, {"$set": filtered_data})
        if result.matched_count == 0:
            return None
        return serialize_mongo_document(
            mongo.db.products.find_one({"id": product_id})
        )
    except Exception as e:
        raise Exception(f"Error al actualizar el producto: {e}")


# Eliminar un producto por su ID
def delete_product(mongo: PyMongo, product_id: str):
    try:
        # Buscar y eliminar el producto por el campo "id", no "_id"
        result = mongo.db.products.delete_one({"id": product_id})
        return result.deleted_count > 0  # Retorna True si se eliminó algo
    except Exception as e:
        raise Exception(f"Error al eliminar el producto: {e}")


