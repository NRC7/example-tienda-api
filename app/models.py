from .database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Pass hasheada
    role = db.Column(db.String(20), nullable=False, default="jugador")

    def __repr__(self):
        return f'<User {self.name}>'
    
    
