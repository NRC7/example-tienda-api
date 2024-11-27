from .models import User
from .database import db
from flask_pymongo import PyMongo

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
        }
        for product in products
    ]

