from flask import Flask, Blueprint, request, jsonify, current_app
from .crud import (
    get_users, update_user, delete_user, 
    get_questions, create_question, update_question, delete_question,
    get_trivias, create_trivia, update_trivia, delete_trivia, register_user,
    get_user_by_email, create_participation, create_ranking
)
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest
from app.models import Question, Trivia, Ranking, User
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from middlewares.middlewares import jwt_required_middleware
import re
import os
from app import mongo
from flask_cors import cross_origin


app = Flask(__name__)

main = Blueprint('main', __name__)

# Configuración JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

@main.route('/products', methods=['GET'])
@cross_origin(origins="http://localhost:3000")
def get_products():
    try:
        # Acceder a la base de datos MongoDB usando current_app
        products = mongo.db.products.find()  # Obtiene los productos de la colección 'products'
        
        product_list = []
        for product in products:
            product_list.append({
                "_id": str(product["_id"]),  # Convierte ObjectId a string
                "id": product.get("id"),
                "name": product.get("name"),
                "category": product.get("category"),
                "normalPrice": product.get("normalPrice"),
                "rating": product.get("rating"),
                "dealPrice": product.get("dealPrice"),
                "discountPercentage": product.get("discountPercentage"),
                "imageResources": product.get("imageResources")
            })
        
        return jsonify({
            "code": "200",
            "len": len(product_list),
            "message": "Productos obtenidos exitosamente",
            "data": product_list
        }), 200

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": f"Error al obtener productos: {str(e)}"
        }), 500
    
# Endpoint para registrar usuarios
@main.route('/register', methods=['POST'])
def register():
    try:
        # Intentar crear un nuevo usuario
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'jugador')  # Por defecto, todos son jugadores

        # Verificar que todos los campos estén presentes
        if not name or not email or not password:
            return jsonify({
                "code": "400",
                "message": "Faltan datos obligatorios: nombre, correo o contraseña"
            }), 400
        
        # Validar formato del correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({
                "code": "400",
                "message": "El correo electrónico no es válido"
            }), 400

        # Validar que el rol sea válido
        if role not in ['admin', 'jugador']:
            return jsonify({
                "code": "400",
                "message": "El rol debe ser 'admin' o 'jugador'"
            }), 400
        
        # Verificar si el correo electrónico ya está registrado
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                "code": "400",
                "message": "El correo electrónico ya está registrado"
            }), 400

        # Registrar usuario en la base de datos
        user = register_user(name, email, generate_password_hash(password), role)

        return jsonify({"code": "201", "message": "Usuario registrado", "user": {"id": user.id, "name": user.name, "role": user.role}}), 201

    except IntegrityError as e:
        # Si hay un error de integridad (como clave duplicada)
        return jsonify({
            "code": "400",
            "message": "El usuario ya existe"
        }), 400

    except Exception as e:
        # Manejo de otros errores internos
        return jsonify({
            "code": "500",
            "message": f"Faltan datos necesarios {e}"
        }), 500
    

# Endpoint para login
@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validar que el correo y la contraseña estén presentes
    if not email or not password:
        return jsonify({"code": "400", "message": "Correo y contraseña son requeridos"}), 400

    # Validar formato del correo electrónico
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"code": "400", "message": "El correo electrónico no es válido"}), 400

    # Buscar al usuario por email
    user = get_user_by_email(email)
    
    # Si no se encuentra el usuario o la contraseña es incorrecta
    if not user or not check_password_hash(user.password, password):
        return jsonify({"code": "401", "message": "Credenciales inválidas"}), 401

    # Crear el token de acceso con identidad como el ID del usuario (convertido a string)
    access_token = create_access_token(
        identity=str(user.id),  # Asegurarse de que identity sea una cadena
        expires_delta=timedelta(minutes=30)  # El token expirará en 1 minuto
    )

    return jsonify({
        "code": "200",
        "message": "Login exitoso",
        "token": access_token
    }), 200


# Endpoint para obtener lista de usuarios
@main.route('/users', methods=['GET'])
@jwt_required_middleware(role="admin")
def get_users_route():
    users = get_users()
    return jsonify({
        "code": "200",
        "message": "Usuarios recuperados exitosamente",
        "data": [
            {"id": user.id, "name": user.name, "email": user.email, "rol": user.role} for user in users
        ]
    }), 200


# Endpoint para actualizar un usuario
@main.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required_middleware(role="admin")
def update_user_route(user_id):

    data = request.get_json()

    updated_user = update_user(user_id, data)

    if not updated_user:
        return jsonify({
            "code": "404",
            "message": "Usuario no encontrado"
    }), 404

    return jsonify({
        "code": "200",
        "message": "Usuario actualizado exitosamente",
        "data": {
            "id": updated_user.id,
            "name": updated_user.name,
            "email": updated_user.email,
            "role": updated_user.role
        }
    }), 200


# Endpoint para borrar un usuario
@main.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required_middleware(role="admin")
def delete_user_route(user_id):
    if not delete_user(user_id):

        return jsonify({"code": "404", "message": "Usuario no encontrado"}), 404
    
    return jsonify({"code": "200", "message": "Usuario eliminado exitosamente"}), 200


# Endpoint para crear una pregunta
@main.route('/questions', methods=['POST'])
@jwt_required_middleware(role="admin")
def create_question_route():

    data = request.get_json()

    # Validación de campos obligatorios
    if not all(key in data for key in ['question_text', 'correct_option', 'options', 'difficulty']):
        return jsonify({
            "code": "400",
            "message": "Faltan datos necesarios"
        }), 400
    
    # Validar que se proporcionen exactamente 3 opciones
    if len(data['options']) != 3:
        return jsonify({
            "code": "400",
            "message": "Debes proporcionar exactamente 3 alternativas por pregunta."
        }), 400

    try:
        question = create_question(
            data['question_text'], 
            data['correct_option'], 
            data['options'], 
            data['difficulty']
        )

        return jsonify({
            "code": "201",
            "message": "Pregunta creada exitosamente",
            "data": {
                "id": question.id,
                "question_text": question.question_text,
                "difficulty": question.difficulty
            }
        }), 201

    except IntegrityError as e:
        return jsonify({
            "code": "400",
            "message": "La pregunta ya existe o hay un error en los datos proporcionados."
        }), 400
    
    except BadRequest as e:
        return jsonify({
            "code": "400",
            "message": "La solicitud es incorrecta: " + str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": "Faltan datos necesarios"
        }), 500
    

# Endpoint para obtener todas las preguntas
@main.route('/questions', methods=['GET'])
@jwt_required_middleware(role="admin")
def get_questions_route():
    questions = get_questions()

    if not questions:
        return jsonify({
            "code": "404",
            "message": "No se encontraron preguntas.",
        }), 404

    try:
        response_data = [
            {
                "id": q.id,
                "question_text": q.question_text,
                "options": {
                    "option_1": q.option_1,
                    "option_2": q.option_2,
                    "option_3": q.option_3
                },
                "correct_option": q.correct_option,
                "difficulty": q.difficulty
            }
            for q in questions
        ]

        return jsonify({
            "code": "200",
            "length": len(response_data),
            "message": "Preguntas recuperadas exitosamente",
            "data": response_data
        }), 200
    except IntegrityError as e:
        return jsonify({
            "code": "400",
            "message": "La pregunta ya existe o hay un error en los datos proporcionados."
        }), 400
    
    except BadRequest as e:
        return jsonify({
            "code": "400",
            "message": "La solicitud es incorrecta: " + str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": "Faltan datos necesarios"
        }), 500


# Endpoint para actualizar una pregunta
@main.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required_middleware(role="admin")
def update_question_route(question_id):
    data = request.get_json()

    try:
        updated_question = update_question(question_id, data)

        if not updated_question:
            return jsonify({
                "code": "404",
                "message": "Pregunta no encontrada"
            }), 404

        return jsonify({
            "code": "200",
            "message": "Pregunta actualizada exitosamente",
            "data": {
                "id": updated_question.id,
                "question_text": updated_question.question_text,
                "difficulty": updated_question.difficulty
            }
        }), 200

    except IntegrityError:
        return jsonify({
            "code": "400",
            "message": "Error de integridad al actualizar la pregunta."
        }), 400

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": f"Error interno: {str(e)}"
        }), 500


# Endpoint para borrar una pregunta
@main.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required_middleware(role="admin")
def delete_question_route(question_id):
    try:
        result = delete_question(question_id)

        if not result:
            return jsonify({
                "code": "404",
                "message": "Pregunta no encontrada"
            }), 404

        return jsonify({
            "code": "200",
            "message": "Pregunta eliminada exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": f"Error interno: {str(e)}"
        }), 500


# Endpoint para crear una trivia
@main.route('/trivias', methods=['POST'])
@jwt_required_middleware(role="admin")
def create_trivia_route():
    data = request.get_json()

    # Validación de campos obligatorios
    if not all(key in data for key in ['name', 'description', 'user_ids', 'question_ids']):
        return jsonify({
            "code": "400",
            "message": "Faltan datos necesarios"
        }), 400

    # Verificar que estén presentes todos los datos
    name = data.get('name')
    description = data.get('description', '')  
    user_ids = data.get('user_ids', [])
    question_ids = data.get('question_ids', [])

    if not name or not description or not user_ids or not question_ids:
        return jsonify({
            "code": "400",
            "message": "Faltan datos necesarios",  
        }), 400

    # Obtener las preguntas de la base de datos mediante los IDs proporcionados
    question_ids = data.get('question_ids', [])
    valid_questions = []
    for question_id in question_ids:
        question = Question.query.get(question_id)
        if question:
            valid_questions.append(question)
        else:
            return jsonify({
                "code": "400",
                "message": f"La pregunta con ID {question_id} no existe"
            }), 400

    # Obtener los usuarios de la base de datos mediante los IDs proporcionados
    valid_users = []
    for user_id in user_ids:
        user = User.query.get(user_id)
        if user:
            valid_users.append(user)
        else:
            return jsonify({
                "code": "400",
                "message": f"El usuario con ID {user_id} no existe"
            }), 400

    try:
        trivia = create_trivia(
                    data['name'], 
                    data['description'], 
                    data['user_ids'], 
                    data['question_ids']
                )

        return jsonify({
            "code": "201",
            "message": "Trivia creada exitosamente",
            "data": {
                "id": trivia.id,
                "name": trivia.name,
                "description": trivia.description,
                "questions": [q.id for q in valid_questions],
                "users": [{"id": user.id, "name": user.name} for user in valid_users]
            }
        }), 201

    except IntegrityError as e:
        return jsonify({
            "code": "400",
            "message": "La trivia ya existe o hay un error en los datos proporcionados."
        }), 400
    
    except BadRequest as e:
        return jsonify({
            "code": "400",
            "message": "La solicitud es incorrecta: " + str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": "Faltan datos necesarios"
        }), 500


# Endpoint obtener todas las trivias
@main.route('/trivias', methods=['GET'])
@jwt_required_middleware()
def get_all_trivias():
    # Obtener todas las trivias de la base de datos
    trivias = get_trivias()

    # Obtener el usuario autenticado desde el token
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    # Verificar que el usuario exista (opcional, según requisitos)
    if not current_user:
        return jsonify({
            "code": "401",
            "message": "La sesión ha caducado, por favor inicia sesión nuevamente."
        }), 403
    

    # Si no se encuentran trivias, devolver un error 404
    if not trivias:
        return jsonify({"code": "404", "message": "No se han encontrado trivias", "data": []}), 404

    # Crear una lista de las trivias con su nombre, descripción y preguntas
    trivias_data = []
    for trivia in trivias:
        trivia_data = {
            "id": trivia.id,
            "name": trivia.name,
            "description": trivia.description,
            "questions": [{"id": q.id, "question_text": q.question_text} for q in trivia.questions],
            "users": [{"id": user.id, "name": user.name} for user in trivia.users]
        }
        trivias_data.append(trivia_data)

    return jsonify({
        "code": "200",
        "length": len(trivias_data),
        "message": "Trivias obtenidas exitosamente",
        "data": trivias_data
    }), 200


# Endpoint para obtener una trivia por su id
@main.route('/trivias/<int:trivia_id>', methods=['GET'])
@jwt_required_middleware()
def get_trivia_by_id(trivia_id):
    # Obtener la trivia por ID
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return jsonify({
            "code": "404",
            "message": "Trivia no encontrada",
        }), 404

    # Retornar la respuesta con el nombre de la trivia
    return jsonify({
        "code": "200",
        "message": "Ranking recuperado exitosamente",
        "data": {
            "trivia": {
                "id": trivia.id,
                "name": trivia.name,
                "description": trivia.description,
                "questions": [{"id": q.id, "question_text": q.question_text} for q in trivia.questions],
                "users": [{"id": user.id, "name": user.name} for user in trivia.users]
            }
        }
    }), 200


# Endpoint para actualizar una trivia
@main.route('/trivias/<int:trivia_id>', methods=['PUT'])
@jwt_required_middleware(role="admin")
def update_trivia_route(trivia_id):
    data = request.get_json()

    try:
        updated_trivia = update_trivia(trivia_id, data)

        if not updated_trivia:
            return jsonify({
                "code": "404",
                "message": "Trivia no encontrada"
            }), 404

        return jsonify({
            "code": "200",
            "message": "Trivia actualizada exitosamente",
            "data": {
                "id": updated_trivia.id,
                "name": updated_trivia.name,
                "description": updated_trivia.description
            }
        }), 200

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": f"Error interno: {str(e)}"
        }), 500


# Endpoint para borrar una trivia
@main.route('/trivias/<int:trivia_id>', methods=['DELETE'])
@jwt_required_middleware(role="admin")
def delete_trivia_route(trivia_id):
    try:
        result = delete_trivia(trivia_id)

        if not result:
            return jsonify({
                "code": "404",
                "message": "Trivia no encontrada"
            }), 404

        return jsonify({
            "code": "200",
            "message": "Trivia eliminada exitosamente"
        }), 200

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": f"Error interno: {str(e)}"
        }), 500


# Endpoint para obtener las trivias de un usuario por su user_id
@main.route('/users/<int:user_id>/trivias', methods=['GET'])
@jwt_required_middleware()
def get_user_trivias(user_id):

    user = User.query.get(user_id)
    
    if not user:
        return jsonify({
            "code": "404",
            "message": "Usuario no encontrado"
        }), 404

    # Obtener las trivias asociadas a este usuario
    trivias = user.trivias  # Esto es posible gracias a la relación definida en el modelo User
    
    # Si no tiene trivias asignadas
    if not trivias:
        return jsonify({
            "code": "404",
            "message": "Este usuario no tiene trivias asignadas"
        }), 404

    # Formatear las trivias para la respuesta
    trivias_data = []
    for trivia in trivias:
        trivia_data = {
            "id": trivia.id,
            "name": trivia.name,
            "description": trivia.description,
            "questions": [{"id": q.id, "question_text": q.question_text} for q in trivia.questions]
        }
        trivias_data.append(trivia_data)

    # Devolver la lista de trivias asignadas
    return jsonify({
        "code": "200",
        "message": f"Trivias de {user.name} obtenidas exitosamente",
        "data": trivias_data,
        "len": len(trivias_data),
        "user": {
            "id": user.id,
            "user_name": user.name
            }
    }), 200


# Endpoint para que un user participe en una trivia
@main.route('/participate/<int:trivia_id>', methods=['POST'])
@jwt_required_middleware()
def participate(trivia_id):

    data = request.get_json()

    # Validar que trivia_id esté presente y sea el respectivo
    if not trivia_id or trivia_id != data.get('trivia_id'):
        return jsonify({
            "code": "400",
            "message": "El identificador de trivia proporcionado no coincide con el esperado"
        }), 400

    user_name = data.get('user_name')
    answers = data.get('answers')

    # Validar que user_name y answers estén presentes
    if not user_name or not answers:
        return jsonify({
            "code": "400",
            "message": "Faltan datos necesarios"
        }), 400
    
    # Verificar si el usuario existe
    user = User.query.filter_by(name=user_name).first()
    if not user:
        return jsonify({
            "code": "404",
            "message": "Usuario no encontrado"
        }), 404
    
    # Validar si "answers" está presente
    if answers is None:
        return jsonify({
            "code": "400",
            "message": "No se proporcionaron respuestas en la solicitud"
        }), 400

    # Validar que "answers" no esté vacío
    if not isinstance(answers, dict) or not answers:
        return jsonify({
            "code": "400",
            "message": "Las respuestas no pueden estar vacías"
        }), 400

    # Verificar que la trivia existe
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return jsonify({
            "code": "404",
            "message": "Trivia no encontrada"
        }), 404
    
    # Obtener los IDs de las preguntas asociadas a la trivia
    trivia_question_ids = {question.id for question in trivia.questions}

    # Validar que los IDs de las respuestas del usuario estén dentro de los IDs de las preguntas de la trivia
    invalid_question_ids = set(answers.keys()).difference(trivia_question_ids)
    
    if not invalid_question_ids:
        return jsonify({
            "code": "400",
            "message": f"Alguna(s) pregunta(s) no pertenece(n) a esta trivia: {list(invalid_question_ids)}"
        }), 400
    
    # Verificar que "answers" tenga la cantidad de respuestas solicitadas
    if len(answers) != len(trivia.questions):
        return jsonify({
            "code": "400",
            "message": "Debes ingresar todas las respuestas solicitadas."
        }), 404

    # Validar respuestas y calcular el puntaje
    score = 0
    correct_answers = {}

    for question in trivia.questions:
        correct_option = question.correct_option
        user_answer = answers.get(str(question.id))

        # Acceder a las opciones de la pregunta (deberías tener 'option_1', 'option_2', 'option_3' en tu modelo)
        options = {
            "option_1": question.option_1,
            "option_2": question.option_2,
            "option_3": question.option_3
        }

        # Obtener el valor de la opción seleccionada por el usuario
        option_value = options.get(user_answer)

        is_correct = option_value == correct_option

        # Validar si la respuesta del usuario es correcta
        if is_correct:
            difficulty = question.difficulty  
            if difficulty == "fácil":  
                score += 1  
            elif difficulty == "medio": 
                score += 2
            elif difficulty == "difícil":  
                score += 3  
            else:
                score += 0

        # Guardar la respuesta correcta para la pregunta
        correct_answers[question.id] = {
            "correct_answer": correct_option,
            "difficulty": question.difficulty,
            "is_correct": "correcta" if is_correct else "incorrecta"
        }

    try:    
        # Guardar participación
        participation = create_participation(
                        data['user_name'], 
                        data['trivia_id'], 
                        data['answers'], 
                        score
                    )

        # Guardar en el ranking
        ranking = create_ranking(
                        data['trivia_id'], 
                        user.id, 
                        score
                    )

        # Responder con el puntaje y las respuestas correctas
        return jsonify({
            "code": "201",
            "message": "Participación registrada",
            "data": {
                "score": ranking.score,
                "correct_answers": correct_answers,  
                "trivia": {
                    "id": trivia.id,
                    "name": trivia.name
                },
                "user": {
                    "name": participation.user_name
                }
            }
        }), 201
    
    except IntegrityError as e:
        return jsonify({
            "code": "400",
            "message": "Ya participaste en esta trivia o hay un error en los datos proporcionados."
        }), 400
    
    except BadRequest as e:
        return jsonify({
            "code": "400",
            "message": "La solicitud es incorrecta: " + str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "code": "500",
            "message": "Faltan datos necesarios" + str(e)
        }), 500


# Endpoint para obtener el ranking de una trivia por su trivia_id
@main.route('/ranking/<int:trivia_id>', methods=['GET'])
@jwt_required_middleware()
def ranking(trivia_id):
    # Obtener la trivia por ID
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return jsonify({
            "code": "404",
            "message": "Trivia no encontrada"
        }), 404

    # Obtener los rankings ordenados por puntaje de mayor a menor
    rankings = Ranking.query.filter_by(trivia_id=trivia_id).order_by(Ranking.score.desc()).all()

    if not rankings:
        return jsonify({
            "code": "404",
            "message": "No hay participantes para esta trivia"
        }), 404

    # Construir la lista de rankings
    ranking_list = [
        {
            #"user_id": ranking.user_id,
            "user_name": ranking.user.name,
            "score": ranking.score
        }
        for ranking in rankings
    ]

    # Retornar la respuesta con el nombre de la trivia
    return jsonify({
        "code": "200",
        "message": "Ranking recuperado exitosamente",
        "data": {
            "trivia": {
                "id": trivia.id,
                "name": trivia.name,
                "descripcion": trivia.description
            },
            "ranking": ranking_list
        }
    }), 200



