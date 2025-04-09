from handlers.services_error_handler import ErrorHandlerServices

def serialize_mongo_document(document):
    if not document:
        return None
    document["_id"] = str(document["_id"]) if "_id" in document else None
    return document


def validate_product_data(product_data: dict):
    required_fields = [
        "name",
        "category",
        "subCategory",
        "normalPrice",
        "dealPrice",
        "discountPercentage",
        "rating",
        "imageResources",
        "description",
        "freeShiping",
        "isActive",
        "sku"
    ]
    missing_fields = [field for field in required_fields if field not in product_data]
    
    if missing_fields:
        return ErrorHandlerServices.missing_requeried_fields_error(f"{'s:, '.join(missing_fields)}")
    
def validate_user_data(user_data: dict):
    required_fields = [
        "email",
        "password",
        "role",
        "userName",
        "address",
        "dateOfBirth"
    ]
    missing_fields = [field for field in required_fields if field not in user_data]
    
    if missing_fields:
        return ErrorHandlerServices.missing_requeried_fields_error(f"{'s:, '.join(missing_fields)}")
    
def validate_checkout_data(checkout_data: dict):
    required_fields = [
        "address",
        "deliveryDate",
        "email",
        "couponFactor",
        "couponAmount",
        "paymentMethod",
        "cartProducts",
        "subTotalAmount",
        "shippingCost",
        "totalAmount",
        "totalWithDiscountAmount",
        "user",
        "trxDate" ,
        "status",
        "lastStatusModificationDate"
    ]
    missing_fields = [field for field in required_fields if field not in checkout_data]
    
    if missing_fields:
        return ErrorHandlerServices.missing_requeried_fields_error(f"{'s:, '.join(missing_fields)}")

def validate_update_order_status_data(update_order_data: dict):
    required_fields = [
        "order_id",
        "update_status"
    ]
    missing_fields = [field for field in required_fields if field not in update_order_data]
    
    if missing_fields:
        return ErrorHandlerServices.missing_requeried_fields_error(f"{'s:, '.join(missing_fields)}")
        

def validate_and_filter_update_data(update_data: dict):
    if not update_data:
        return ErrorHandlerServices.missing_requeried_fields_error("s: No data provided to update")
    
    # Filtrar solo los campos válidos
    required_fields = [
        "_id",
        "name",
        "category",
        "subCategory",
        "normalPrice",
        "dealPrice",
        "discountPercentage",
        "rating",
        "imageResources",
        "description",
        "freeShiping",
        "isActive",
        "sku",
        "uploadDateTime"
    ]
    filtered_data = {key: value for key, value in update_data.items() if key in required_fields}
    
    if not filtered_data:
        return ErrorHandlerServices.missing_requeried_fields_error("s: Not enough data provided to update")
    
    print(f"filtered_data: {filtered_data}")
    return filtered_data