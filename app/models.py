from .database import db

# Tabla de asociación para la relación muchos a muchos entre Trivia y Question
trivia_questions = db.Table(
    'trivia_questions',
    db.Column('trivia_id', db.Integer, db.ForeignKey('trivia.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True)
)


# Tabla de asociación para la relación muchos a muchos entre Trivia y User
trivia_users = db.Table(
    'trivia_users',
    db.Column('trivia_id', db.Integer, db.ForeignKey('trivia.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class Trivia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)  # Se agrega description aquí
    
    # Relación con preguntas a través de la tabla intermedia trivia_questions
    questions = db.relationship('Question', secondary=trivia_questions, back_populates='trivias')
    
    # Relación con participaciones
    participations = db.relationship('Participate', back_populates='trivia', cascade='all, delete-orphan')

    # Relación con usuarios a través de la tabla intermedia trivia_users
    users = db.relationship('User', secondary=trivia_users, back_populates='trivias')
    
    # Relación con rankings
    rankings = db.relationship('Ranking', back_populates='trivia', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Trivia {self.name}>'


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(100), nullable=False)
    option_1 = db.Column(db.String(100), nullable=False)
    option_2 = db.Column(db.String(100), nullable=False)
    option_3 = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(7), nullable=False)
    trivias = db.relationship('Trivia', secondary=trivia_questions, back_populates='questions')

    def __repr__(self):
        return f'<Question {self.question_text}>'
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Pass hasheada
    role = db.Column(db.String(20), nullable=False, default="jugador")

    # Relación con trivias a través de la tabla intermedia trivia_users
    trivias = db.relationship('Trivia', secondary=trivia_users, back_populates='users')

    def __repr__(self):
        return f'<User {self.name}>'
    
    
class Participate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), db.ForeignKey('user.name'), nullable=False)
    trivia_id = db.Column(db.Integer, db.ForeignKey('trivia.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    # Relación con Trivia
    trivia = db.relationship('Trivia', back_populates='participations')
    
    # Relación con User
    user = db.relationship('User', backref='participations') 

    def __repr__(self):
        return f'<Participate {self.user_name}>'


class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trivia_id = db.Column(db.Integer, db.ForeignKey('trivia.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    # Relación con Trivia
    trivia = db.relationship('Trivia', back_populates='rankings')

    # Relación con User
    user = db.relationship('User', backref='rankings')

    def __repr__(self):
        return f'<Ranking {self.user_id}>'


