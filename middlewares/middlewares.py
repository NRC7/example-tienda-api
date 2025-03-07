from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required
from functools import wraps
from handlers.error_handler import ErrorHandler
from app.crud import get_user_by_id
from app import mongo

def jwt_required_middleware(role=None, refresh=False, location=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            try:
                # Verifica access o refresh
                if refresh:
                    jwt_required(refresh=True, locations=location)(lambda: None)()
                elif not refresh:
                    jwt_required(locations=location)(lambda: None)()
                else:
                    verify_jwt_in_request() 

                identity = get_jwt_identity()
                if not identity:
                    return ErrorHandler.unauthorized_error("Invalid token m")
                
                if not get_user_by_id(mongo, identity):
                    return ErrorHandler.not_found_error("User not found m")
                
                user = get_user_by_id(mongo, identity)

                if role and user.get("role") != role:
                    return ErrorHandler.forbidden_error("Access denied requires different role m")

                return fn(*args, **kwargs)
            except Exception as e:
                return ErrorHandler.internal_server_error(f"Error during verification m: {str(e)}")
        return decorated_function
    return wrapper
