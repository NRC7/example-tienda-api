from .models import User, Question, Trivia, Participate, Ranking
from .database import db

# Registrar un usuario
def register_user(name, email, hashed_password, role="jugador"):
    user = User(name=name, email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()
    return user

# Obtener un usuario por campo email
def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

# Obtener todos los usuarios
def get_users():
    return User.query.all()

# Actualizar/Modificar un usuario
def update_user(user_id, new_data):
    user = User.query.get(user_id)
    if not user:
        return None
    user.name = new_data.get('name', user.name)
    user.email = new_data.get('email', user.email)
    user.role = new_data.get('role', user.role)
    db.session.commit()
    return user

# Borrar un usuario
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return None
    db.session.delete(user)
    db.session.commit()
    return True

# Crear una pregunta
def create_question(question_text, correct_option, options, difficulty):
    question = Question(
        question_text=question_text,
        correct_option=correct_option,
        option_1=options[0],
        option_2=options[1],
        option_3=options[2],
        difficulty=difficulty
    )
    db.session.add(question)
    db.session.commit()
    return question

# Obtener todas las preguntas
def get_questions():
    return Question.query.all()

# Actualizar/Modificar una pregunta
def update_question(question_id, new_data):
    question = Question.query.get(question_id)
    if not question:
        return None
    question.question_text = new_data.get('question_text', question.question_text)
    question.correct_option = new_data.get('correct_option', question.correct_option)
    question.option_1 = new_data.get('options', {}).get('option_1', question.option_1)
    question.option_2 = new_data.get('options', {}).get('option_2', question.option_2)
    question.option_3 = new_data.get('options', {}).get('option_3', question.option_3)
    question.difficulty = new_data.get('difficulty', question.difficulty)
    db.session.commit()
    return question

# Borrar una pregunta
def delete_question(question_id):
    question = Question.query.get(question_id)
    if not question:
        return None
    db.session.delete(question)
    db.session.commit()
    return True

# Crear una trivia
def create_trivia(name, description, user_ids, question_ids,):

    trivia = Trivia(name=name, description=description)

    for question_id in question_ids:
        question = Question.query.get(question_id)
        trivia.questions.append(question)

    for user_id in user_ids:
        user = User.query.get(user_id)
        trivia.users.append(user)

    db.session.add(trivia)
    db.session.commit()

    return trivia

# Obtener todas las trivias
def get_trivias():
    return Trivia.query.all()

# Actualizar/Modificar una trivia
def update_trivia(trivia_id, new_data):
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return None
    trivia.name = new_data.get('name', trivia.name)
    trivia.description = new_data.get('description', trivia.description)

    # Actualizar preguntas asociadas
    question_ids = new_data.get('question_ids', [])
    if question_ids:
        trivia.questions = [Question.query.get(q_id) for q_id in question_ids if Question.query.get(q_id)]

    # Actualizar usuarios asociados
    user_ids = new_data.get('user_ids', [])
    if user_ids:
        trivia.users = [User.query.get(u_id) for u_id in user_ids if User.query.get(u_id)]

    db.session.commit()
    return trivia

# Borrar una trivia
def delete_trivia(trivia_id):
    trivia = Trivia.query.get(trivia_id)
    if not trivia:
        return None
    db.session.delete(trivia)
    db.session.commit()
    return True


# Crear una participacion
def create_participation(user_name, trivia_id, answers, score):

    participation = Participate(user_name=user_name, trivia_id=trivia_id, answers=answers, score=score)

    db.session.add(participation)
    db.session.commit()
    
    return participation

# Obtener todas las trivias
def get_trivias():
    return Trivia.query.all()


# Crear un ranking
def create_ranking(trivia_id, user_id, score):

    ranking = Ranking(trivia_id=trivia_id, user_id=user_id, score=score)

    db.session.add(ranking)
    db.session.commit()
    
    return ranking

