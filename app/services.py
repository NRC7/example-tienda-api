from .crud import get_trivia_by_id, create_participation, create_ranking

def process_participation(trivia_id, data):
    try:
        # Validar datos básicos
        user_name = data.get("user_name")
        answers = data.get("answers")
        if not user_name or not answers:
            return {"code": 400, "message": "Faltan datos necesarios"}

        # Obtener trivia y validar preguntas
        trivia = get_trivia_by_id(trivia_id)
        if not trivia:
            return {"code": 404, "message": "Trivia no encontrada"}

        # Calcular puntaje
        score = 0
        correct_answers = {}
        for question in trivia.questions:
            user_answer = answers.get(str(question.id))
            if user_answer == question.correct_option:
                difficulty = question.difficulty
                score += {"fácil": 1, "medio": 2, "difícil": 3}.get(difficulty, 0)

            correct_answers[question.id] = {
                "correct_answer": question.correct_option,
                "is_correct": user_answer == question.correct_option
            }

        # Registrar participación y ranking
        participation = create_participation(user_name, trivia_id, answers, score)
        ranking = create_ranking(trivia_id, participation.id, score)

        return {
            "code": 201,
            "message": "Participación registrada",
            "data": {
                "score": score,
                "correct_answers": correct_answers,
                "trivia": {"id": trivia.id, "name": trivia.name},
                "user": {"name": participation.user_name}
            }
        }
    except Exception as e:
        return {"code": 500, "message": f"Error interno: {str(e)}"}
