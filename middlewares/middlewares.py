from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required
from functools import wraps
from app.crud import get_user_by_id
from app import mongo

def jwt_required_middleware(role=None, refresh=False):

    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            try:
                # Verifica el JWT en la solicitud (access o refresh)
                if refresh:
                    jwt_required(refresh=True)(lambda: None)()  # Verifica el refresh token
                else:
                    verify_jwt_in_request()  # Verifica el access token

                identity = get_jwt_identity()
                if not identity:
                    return jsonify({"code": "401", "message": "Invalid token"}), 401
                
                if not get_user_by_id(mongo, identity):
                    return jsonify({"code": "401", "message": "User not foundy"}), 401
                
                user = get_user_by_id(mongo, identity)

                if role and user.role != role:
                    return jsonify({
                        "code": "403",
                        "message": "Access denied. requires different rol"
                    }), 403

                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    "code": "401",
                    "message": f"Invalid token or expired session: {str(e)}"
                }), 401
        return decorated_function
    return wrapper
