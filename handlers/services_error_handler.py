from flask import jsonify


class ErrorHandlerServices:

    @staticmethod
    def missing_requeried_fields_error(message):
        return jsonify({
            "code": "5051",
            "message": f"Missing requeried fields {message}"
        })