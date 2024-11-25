from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.models import User

def jwt_required_middleware(role=None):

    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            try:
                # Verify the JWT in the request
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)

                if not user:
                    return jsonify({
                        "code": "404",
                        "message": "Usuario no encontrado"
                    }), 404

                if role and user.role != role:
                    return jsonify({
                        "code": "403",
                        "message": "Acceso denegado. Se requiere rol de administrador"
                    }), 403

                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    "code": "401",
                    "message": f"Token inválido o sesión expirada: {str(e)}"
                }), 401
        return decorated_function
    return wrapper
