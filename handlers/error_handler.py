from flask import jsonify


class ErrorHandler:

    @staticmethod
    def bad_request_error(message):
        return jsonify({
            "code": "400",
            "message": f"Bad Request: {message}"
        }), 400

    @staticmethod
    def unauthorized_error(message):
        return jsonify({
            "code": "401",
            "message": f"Unauthorized: {message}"
        }), 401
    
    @staticmethod
    def invalid_credentials_error(message):
        return jsonify({
            "code": "402",
            "message": f"Invalid credentials: {message}"
        }), 402

    @staticmethod
    def forbidden_error(message):
        return jsonify({
            "code": "403",
            "message": f"Forbidden: {message}"
        }), 403

    @staticmethod
    def not_found_error(message):
        return jsonify({
            "code": "404",
            "message": f"Not Found: {message}"
        }), 404
    
    @staticmethod
    def expired_signature_error(message):
        return jsonify({
            "code": "405",
            "message": f"Signature has expired: {message}"
        }), 405
    
    @staticmethod
    def not_acceptable_error(message):
        return jsonify({
            "code": "406",
            "message": f"Not Acceptable: {message}"
        }), 406
    
    @staticmethod
    def conflict_error(message):
        return jsonify({
            "code": "409",
            "message": f"Identifiers do not mach: {message}"
        }), 409

    @staticmethod
    def internal_server_error(message):
        return jsonify({
            "code": "500",
            "message": f"Internal Server Error: {message}"
        }), 500
    
    @staticmethod
    def bad_gateway_error(message):
        return jsonify({
            "code": "502",
            "message": f"Bad gateway: {message}"
        }), 502

    @staticmethod
    def service_unavailable_error(message):
        return jsonify({
            "code": "503",
            "message": f"Service Unavailable: {message}"
        }), 503
    
    @staticmethod
    def gateway_timeout_error(message):
        return jsonify({
            "code": "504",
            "message": f"Gateway timeout: {message}"
        }), 504
