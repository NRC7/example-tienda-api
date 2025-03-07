from flask import jsonify

class ErrorHandlerMongo:

    @staticmethod
    def connection_db_error(message):
        return jsonify({
            "code": "1001",
            "message": f"Error connecting to DB: {message}"
        })
    
    @staticmethod
    def executing_query_error(message):
        return jsonify({
            "code": "1002",
            "message": f"Error executing a query: {message}"
        })

    @staticmethod
    def document_not_found_error(message):
        return jsonify({
            "code": "1003",
            "message": f"Document not found: {message}"
        })

    @staticmethod
    def duplicated_value_in_unique_field_error(message):
        return jsonify({
            "code": "1004",
            "message": f"Duplicate value in unique field: {message}"
        })    

    @staticmethod
    def db_timeout_error(message):
        return jsonify({
            "code": "1005",
            "message": f"DB operation timed out: {message}"
        })    
    
    @staticmethod
    def db_deadlock_error(message):
        return jsonify({
            "code": "1006",
            "message": f"Deadlock error detected: {message}"
        })   

    @staticmethod
    def db_validation_error(message):
        return jsonify({
            "code": "1007",
            "message": f"Validation error: {message}"
        })   

    @staticmethod
    def db_transaction_error(message):
        return jsonify({
            "code": "1008",
            "message": f"DB transaction error: {message}"
        })   

    @staticmethod
    def db_unauthorized_error(message):
        return jsonify({
            "code": "1009",
            "message": f"Unauthorized error: {message}"
        })

    @staticmethod
    def db_general_error(message):
        return jsonify({
            "code": "1010",
            "message": f"DB internal error: {message}"
        })      

    def handleDBError(error):
        errorResponse = ErrorHandlerMongo.db_general_error("c:")

        errorCode = ""
        if not hasattr(error, 'code'):
            error_data = error.args[0]
            errorCode = error_data["code"]
        else :
            errorCode = str(error.code)

        if errorCode == "1001":
            errorResponse = ErrorHandlerMongo.connection_db_error("c:")
        elif errorCode == "1002":
            errorResponse = ErrorHandlerMongo.executing_query_error("c:")
        elif errorCode == "1003":
            errorResponse = ErrorHandlerMongo.document_not_found_error("c:")
        elif errorCode == "1004":
            errorResponse = ErrorHandlerMongo.duplicated_value_in_unique_field_error("c:")
        elif errorCode == "1005":
            errorResponse = ErrorHandlerMongo.db_timeout_error("c:")
        elif errorCode == "1006":
            errorResponse = ErrorHandlerMongo.db_deadlock_error("c:")
        elif errorCode == "1007":
            errorResponse = ErrorHandlerMongo.db_validation_error("c:")
        elif errorCode == "1008":
            errorResponse = ErrorHandlerMongo.db_transaction_error("c:")
        elif errorCode == "1009":
            errorResponse = ErrorHandlerMongo.db_unauthorized_error("c:")
        else:
            errorResponse = ErrorHandlerMongo.db_general_error(f"c: {error.code}")

        return errorResponse        