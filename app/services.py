from bson import ObjectId

def serialize_mongo_document(document):
    """Convierte todos los ObjectId de un documento MongoDB a cadenas JSON serializables."""
    if not document:
        return None
    document["_id"] = str(document["_id"]) if "_id" in document else None
    return document


def validate_product_data(product_data: dict):
    """Valida que todos los campos requeridos estén presentes en el producto."""
    required_fields = [
        "name",
        "category",
        "normalPrice",
        "dealPrice",
        "discountPercentage",
        "rating",
        "imageResources"
    ]
    missing_fields = [field for field in required_fields if field not in product_data]
    
    if missing_fields:
        raise ValueError(f"Faltan los siguientes campos obligatorios: {', '.join(missing_fields)}")

def validate_and_filter_update_data(update_data: dict):
    """Filtra los campos permitidos para la actualización."""
    if not update_data:
        raise ValueError("No se proporcionaron datos para actualizar")
    
    # Filtrar solo los campos válidos
    required_fields = [
        "name",
        "category",
        "normalPrice",
        "dealPrice",
        "discountPercentage",
        "rating",
        "imageResources"
    ]
    filtered_data = {key: value for key, value in update_data.items() if key in required_fields}
    
    if not filtered_data:
        raise ValueError("Ningún campo válido proporcionado para la actualización")
    
    return filtered_data