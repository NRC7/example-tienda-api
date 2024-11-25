import sys
import os

# Asegúrate de que el directorio `app` esté en el path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app import create_app

import unittest
from app import create_app
from flask import json
from app.models import db, User, Question, Trivia, Ranking
from werkzeug.security import generate_password_hash

# Clase de pruebas unitarias para las rutas
class TestRoutes(unittest.TestCase):

    def setUp(self):
        """Crear la aplicación y un cliente de prueba para cada prueba."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Configura la base de datos para pruebas en memoria
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)  

        # Crear las tablas en la base de datos de prueba
        with self.app.app_context():
            db.create_all()  

        # Crear un usuario de prueba con la contraseña cifrada
        hashed_password = generate_password_hash("testpassword")
        self.user = User(name="Test User", email="test@example.com", password=hashed_password, role="admin")
        db.session.add(self.user)
        db.session.commit()

        # Iniciar sesión para obtener el token
        response = self.client.post('/login', json={'email': self.user.email, 'password': 'testpassword'})
        self.token = response.json['token']  

        # Crear preguntas de prueba
        self.question1 = Question(question_text="¿Cuál es la capital de Francia?", correct_option="París", option_1="Londres", option_2= "Madrid", option_3= "Roma", difficulty="fácil")
        self.question2 = Question(question_text="¿Cuál es la capital de España?", correct_option="Madrid", option_1="Londres", option_2= "Madrid", option_3= "Roma", difficulty="medio")
        db.session.add(self.question1)
        db.session.add(self.question2)
        db.session.commit()

        # Crear una trivia de prueba
        self.trivia_data = {
            "name": "Trivia de prueba",
            "description": "Una trivia de prueba",
            "user_ids": [self.user.id],
            "question_ids": [self.question1.id, self.question2.id]
        }

        response = self.client.post(
            '/trivias',
            json=self.trivia_data,
            headers={'Authorization': f'Bearer {self.token}'}  # Agrega el token en las cabeceras
        )

        self.trivia_id = response.json['data']['id']  # Guardar el ID de la trivia recién creada


    def tearDown(self):
        """Limpiar la base de datos después de cada prueba."""
        db.session.remove()
        db.drop_all()  


    def test_register(self):
        """Probar el endpoint de registro."""
        response = self.client.post('/register', json={
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'password123',
            'role': 'admin'
        })

        # Verificar que la respuesta sea 201 y que el mensaje esté correcto
        self.assertEqual(response.status_code, 201)
        self.assertIn('Usuario registrado', response.json['message'])


    def test_login(self):
        """Probar el endpoint de login."""
        self.client.post('/register', json={
            'name': 'Test User',
            'email': 'testuser@example.com',
            'password': 'password123',
            'role': 'admin'
        })
        
        response = self.client.post('/login', json={
            'email': 'testuser@example.com',
            'password': 'password123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)


    def test_get_users(self):
        """Probar el endpoint de obtener usuarios."""
        response = self.client.get('/users', headers={'Authorization': f'Bearer {self.token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.json)


    def test_update_user(self):
        """Probar el endpoint para actualizar un usuario."""
        # Crear un usuario de prueba adicional
        user_to_update = User(
            name="User To Update",
            email="updateuser@example.com",
            password="password",
            role="user"
        )
        db.session.add(user_to_update)
        db.session.commit()

        # Datos de actualización
        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "role": "admin"
        }

        # Realizar la solicitud PUT con el token de administrador
        response = self.client.put(
            f'/users/{user_to_update.id}',
            json=update_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response_data = response.json

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn('Usuario actualizado exitosamente', response_data['message'])

        # Validar que los datos del usuario se hayan actualizado
        self.assertEqual(response_data['data']['name'], "Updated Name")
        self.assertEqual(response_data['data']['email'], "updated@example.com")
        self.assertEqual(response_data['data']['role'], "admin")


    def test_delete_user(self):
        """Probar el endpoint para eliminar un usuario."""
        # Crear un usuario de prueba adicional
        user_to_delete = User(
            name="User To Delete",
            email="deleteuser@example.com",
            password="password",
            role="user"
        )
        db.session.add(user_to_delete)
        db.session.commit()

        # Realizar la solicitud DELETE con el token de administrador
        response = self.client.delete(
            f'/users/{user_to_delete.id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response_data = response.json

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn('Usuario eliminado exitosamente', response_data['message'])

        # Validar que el usuario haya sido eliminado de la base de datos
        deleted_user = User.query.get(user_to_delete.id)
        self.assertIsNone(deleted_user)


    def test_create_question(self):
        """Probar el endpoint para crear una pregunta."""
        response = self.client.post('/questions', json={
            'question_text': '¿Cuál es la capital de Francia?',
            'correct_option': 'París',
            "options": ["Pulmones", "Hígado", "Corazón"],
            'difficulty': 'fácil'
        }, headers={'Authorization': f'Bearer {self.token}'})  
        print(response.json)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Pregunta creada exitosamente', response.json['message'])


    def test_get_questions(self):
  
        # Limpiar las preguntas existentes antes de agregar nuevas
        Question.query.delete()
        db.session.commit()

        # Crear preguntas de prueba
        question1 = Question(
            question_text="¿Cuál es la capital de Francia?",
            correct_option="París",
            option_1="Londres",
            option_2="Madrid",
            option_3="Roma",
            difficulty="fácil"
        )
        question2 = Question(
            question_text="¿Cuál es la capital de España?",
            correct_option="Madrid",
            option_1="Londres",
            option_2="Madrid",
            option_3="París",
            difficulty="medio"
        )
        db.session.add(question1)
        db.session.add(question2)
        db.session.commit()

        # Realizar la solicitud GET con el token de administrador
        response = self.client.get('/questions', headers={'Authorization': f'Bearer {self.token}'})
        print(response.json)

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['code'], '200')
        self.assertIn('Preguntas recuperadas exitosamente', response.json['message'])

        # Validar que las preguntas se incluyan correctamente en la respuesta
        self.assertEqual(len(response.json['data']), 2)
        self.assertEqual(response.json['data'][0]['question_text'], "¿Cuál es la capital de Francia?")
        self.assertEqual(response.json['data'][1]['question_text'], "¿Cuál es la capital de España?")


    def test_update_question(self):
        """Probar el endpoint para actualizar una pregunta."""
        # Crear una pregunta de prueba
        question_to_update = Question(
            question_text="¿Cuál es la capital de Francia?",
            correct_option="París",
            option_1="Londres",
            option_2="Madrid",
            option_3="Roma",
            difficulty="fácil"
        )
        db.session.add(question_to_update)
        db.session.commit()

        # Datos de actualización
        update_data = {
            "question_text": "¿Cuál es la capital de España?",
            "correct_option": "Madrid",
            "option_1": "Londres",
            "option_2": "Madrid",
            "option_3": "Roma",
            "difficulty": "medio"
        }

        # Realizar la solicitud PUT con el token de administrador
        response = self.client.put(
            f'/questions/{question_to_update.id}',
            json=update_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response_data = response.json

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn('Pregunta actualizada exitosamente', response_data['message'])

        # Validar que los datos de la pregunta se hayan actualizado
        self.assertEqual(response_data['data']['question_text'], "¿Cuál es la capital de España?")
        self.assertEqual(response_data['data']['difficulty'], "medio")


    def test_delete_question(self):
        """Probar el endpoint para eliminar una pregunta."""
        # Crear una pregunta de prueba
        question_to_delete = Question(
            question_text="¿Cuál es la capital de Francia?",
            correct_option="París",
            option_1="Londres",
            option_2="Madrid",
            option_3="Roma",
            difficulty="fácil"
        )
        db.session.add(question_to_delete)
        db.session.commit()

        # Realizar la solicitud DELETE con el token de administrador
        response = self.client.delete(
            f'/questions/{question_to_delete.id}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response_data = response.json

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn('Pregunta eliminada exitosamente', response_data['message'])

        # Validar que la pregunta haya sido eliminada de la base de datos
        deleted_question = Question.query.get(question_to_delete.id)
        self.assertIsNone(deleted_question)


    def test_create_trivia_success(self):
        """Probar el endpoint de crear trivia."""
        # Datos válidos para crear una trivia
        data = {
            "name": "Trivia de prueba",
            "description": "Una trivia de prueba",
            "user_ids": [self.user.id],
            "question_ids": [self.question1.id, self.question2.id]
        }
        response = self.client.post('/trivias', json=data, headers={'Authorization': f'Bearer {self.token}'})
        
        # Verificar que la respuesta sea 201 y que el mensaje sea el esperado
        self.assertEqual(response.status_code, 201)
        self.assertIn('Trivia creada exitosamente', response.json['message'])
        self.assertEqual(response.json['data']['name'], data['name'])
        self.assertEqual(response.json['data']['description'], data['description'])


    def test_create_trivia_missing_data(self):
        """Probar el endpoint de crear trivia con datos faltantes."""
        data = {
            "name": "Trivia de prueba",
            "user_ids": [self.user.id],  
        }

        response = self.client.post('/trivias', json=data, headers={'Authorization': f'Bearer {self.token}'})
        
        # Verificar que la respuesta sea 400 debido a la falta de datos
        self.assertEqual(response.status_code, 400)
        self.assertIn('Faltan datos necesarios', response.json['message'])


    def test_create_trivia_unauthorized(self):
        """Probar el endpoint de crear trivia cuando el usuario no es admin."""
        # Crear un usuario sin rol de admin
        non_admin_user = User(name="Non Admin User", email="nonadmin@example.com", password=generate_password_hash("password"), role="user")
        db.session.add(non_admin_user)
        db.session.commit()

        # Obtener token para el usuario no admin
        response = self.client.post('/login', json={'email': non_admin_user.email, 'password': 'password'})
        non_admin_token = response.json['token']

        data = {
            "name": "Trivia de prueba",
            "description": "Una trivia de prueba",
            "user_ids": [non_admin_user.id],  # Usamos el usuario no admin
            "question_ids": [self.question1.id, self.question2.id]
        }
        response = self.client.post('/trivias', json=data, headers={'Authorization': f'Bearer {non_admin_token}'})
        
        # Verificar que la respuesta sea 403 debido a que el usuario no es admin
        self.assertEqual(response.status_code, 403)
        self.assertIn('Acceso denegado', response.json['message'])


    def test_create_trivia_invalid_question(self):
        """Probar el endpoint de crear trivia con una pregunta inválida."""
        data = {
            "name": "Trivia de prueba",
            "description": "Una trivia de prueba",
            "user_ids": [self.user.id],
            "question_ids": [999]
        }
        response = self.client.post('/trivias', json=data, headers={'Authorization': f'Bearer {self.token}'})
        
        # Verificar que la respuesta sea 400 debido a la pregunta inválida
        self.assertEqual(response.status_code, 400)
        self.assertIn("La pregunta con ID 999 no existe", response.json['message'])    


    def test_get_trivia_by_id(self):
        """Probar el endpoint para obtener una trivia por su ID."""
        # Crear una trivia de prueba
        trivia = Trivia(name="Trivia de Prueba", description="Descripción de prueba")
        trivia.questions = [self.question1, self.question2]
        trivia.users = [self.user]
        db.session.add(trivia)
        db.session.commit()

        # Realizar la solicitud GET
        response = self.client.get(
            f'/trivias/{trivia.id}', headers={'Authorization': f'Bearer {self.token}'}
        )
        response_data = response.json

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn('Ranking recuperado exitosamente', response_data['message'])

        # Validar que los datos de la trivia estén en la respuesta
        self.assertEqual(response_data['data']['trivia']['id'], trivia.id)
        self.assertEqual(response_data['data']['trivia']['name'], "Trivia de Prueba")
        self.assertEqual(len(response_data['data']['trivia']['questions']), 2)


    def test_update_trivia(self):
        """Probar el endpoint para actualizar una trivia."""
        # Crear una trivia de prueba
        trivia = Trivia(name="Trivia Original", description="Descripción Original")
        db.session.add(trivia)
        db.session.commit()

        # Datos para actualizar la trivia
        update_data = {
            "name": "Trivia Actualizada",
            "description": "Descripción Actualizada"
        }

        # Realizar la solicitud PUT
        response = self.client.put(
            f'/trivias/{trivia.id}',
            json=update_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response_data = response.json

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn('Trivia actualizada exitosamente', response_data['message'])

        # Validar que los datos se hayan actualizado
        self.assertEqual(response_data['data']['name'], "Trivia Actualizada")
        self.assertEqual(response_data['data']['description'], "Descripción Actualizada")


    def test_delete_trivia(self):
        """Probar el endpoint para eliminar una trivia."""
        # Crear una trivia de prueba
        trivia = Trivia(name="Trivia a Eliminar", description="Descripción a Eliminar")
        db.session.add(trivia)
        db.session.commit()

        # Realizar la solicitud DELETE
        response = self.client.delete(
            f'/trivias/{trivia.id}', headers={'Authorization': f'Bearer {self.token}'}
        )
        response_data = response.json

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn('Trivia eliminada exitosamente', response_data['message'])

        # Validar que la trivia haya sido eliminada
        deleted_trivia = Trivia.query.get(trivia.id)
        self.assertIsNone(deleted_trivia)


    def test_get_user_trivias(self):
        """Probar el endpoint para obtener las trivias asociadas a un usuario por su user_id."""

        # Crear un usuario de prueba
        user = User(name="Test User", email="testuser@example.com", password="testpassword", role="admin")
        db.session.add(user)
        db.session.commit()

        # Crear preguntas de prueba
        question1 = Question(question_text="¿Cuál es la capital de Francia?", correct_option="París", option_1="Londres", option_2="Madrid", option_3="Roma", difficulty="fácil")
        question2 = Question(question_text="¿Cuál es la capital de España?", correct_option="Madrid", option_1="Londres", option_2="Madrid", option_3="Roma", difficulty="medio")
        db.session.add(question1)
        db.session.add(question2)
        db.session.commit()

        # Crear una trivia y asociarla al usuario
        trivia = Trivia(name="Trivia de ejemplo", description="Trivia sobre ciudades", users=[user], questions=[question1, question2])
        db.session.add(trivia)
        db.session.commit()

        # Realizar la solicitud GET para obtener las trivias del usuario
        response = self.client.get(f'/users/{user.id}/trivias', headers={'Authorization': f'Bearer {self.token}'})
        response_data = response.json

        # Validar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn(f"Trivias de {user.name} obtenidas exitosamente", response_data['message'])

        # Validar que las trivias del usuario estén correctamente incluidas
        self.assertEqual(len(response_data['data']), 1)  # El usuario debería tener al menos una trivia
        self.assertEqual(response_data['data'][0]['name'], "Trivia de ejemplo")
        self.assertEqual(response_data['data'][0]['questions'][0]['question_text'], "¿Cuál es la capital de Francia?")


    def test_get_user_trivias_no_trivias(self):
        """Probar el endpoint cuando el usuario no tiene trivias asignadas."""

        # Crear un usuario de prueba sin trivias asignadas
        user = User(name="Test User", email="testuser@example.com", password="testpassword", role="admin")
        db.session.add(user)
        db.session.commit()

        # Realizar la solicitud GET para obtener las trivias del usuario
        response = self.client.get(f'/users/{user.id}/trivias', headers={'Authorization': f'Bearer {self.token}'})
        response_data = response.json

        # Validar que la respuesta sea correcta cuando no se encuentran trivias
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['code'], '404')
        self.assertIn("Este usuario no tiene trivias asignadas", response_data['message'])


    def test_get_user_trivias_user_not_found(self):
        """Probar el endpoint cuando no se encuentra el usuario por su ID."""

        # Realizar la solicitud GET para obtener las trivias de un usuario que no existe
        response = self.client.get('/users/9999/trivias', headers={'Authorization': f'Bearer {self.token}'})
        response_data = response.json

        # Validar que la respuesta sea correcta cuando el usuario no se encuentra
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['code'], '404')
        self.assertIn("Usuario no encontrado", response_data['message'])


    def test_participate(self):
        """Probar el endpoint para que un usuario participe en una trivia."""
        data = {
            'user_name': 'Test User',
            'trivia_id': self.trivia_id,
            'answers': {
                str(self.question1.id): 'option_2',  # Respuesta correcta 'París' para la pregunta 1
                str(self.question2.id): 'option_2'   # Respuesta correcta 'Madrid' para la pregunta 2
            }
        }

        # Hacer la solicitud POST para participar en la trivia
        response = self.client.post(f'/participate/{self.trivia_id}', json=data, headers={'Authorization': f'Bearer {self.token}'})
        
        # Verificar que la respuesta sea 201 y que se registre la participación
        self.assertEqual(response.status_code, 201)
        self.assertIn('Participación registrada', response.json['message'])
        self.assertIn('score', response.json['data'])
        self.assertIn('correct_answers', response.json['data'])


    def test_participate_invalid_trivia(self):
        """Probar el endpoint para participar en una trivia con una trivia no válida."""
        invalid_trivia_id = 999  # Un ID que no existe
        data = {
            'user_name': 'Test User',
            'trivia_id': invalid_trivia_id,
            'answers': {
                str(self.question1.id): 'option_2',
                str(self.question2.id): 'option_2'
            }
        }

        response = self.client.post(f'/participate/{invalid_trivia_id}', json=data, headers={'Authorization': f'Bearer {self.token}'})
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('Trivia no encontrada', response.json['message'])


    def test_participate_missing_answer(self):
        """Probar el endpoint para participar en una trivia sin respuestas."""
        data = {
            'user_name': 'Test User',
            'trivia_id': self.trivia_id,
            'answers': {}  # No hay respuestas proporcionadas
        }

        response = self.client.post(f'/participate/{self.trivia_id}', json=data, headers={'Authorization': f'Bearer {self.token}'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('Faltan datos necesarios', response.json['message'])  # Cambiar el mensaje esperado


    def test_get_ranking(self):
        """Probar el endpoint para obtener el ranking de una trivia."""
        # Crear preguntas de prueba
        question = Question(
            question_text="¿Cuál es la capital de Francia?",
            correct_option="París",
            option_1="Londres",
            option_2="Madrid",
            option_3="París",
            difficulty="fácil"
        )
        db.session.add(question)
        db.session.commit()

        # Crear una trivia de prueba
        trivia = Trivia(
            name="Trivia de Geografía",
            description="Prueba tus conocimientos sobre geografía.",
            questions=[question]
        )
        db.session.add(trivia)
        db.session.commit()

        # Crear usuarios de prueba
        user1 = User(name="User 1", email="user1@example.com", password="password", role="user")
        user2 = User(name="User 2", email="user2@example.com", password="password", role="user")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        # Crear rankings de prueba
        ranking1 = Ranking(trivia_id=trivia.id, user_id=user1.id, score=10)
        ranking2 = Ranking(trivia_id=trivia.id, user_id=user2.id, score=15)
        db.session.add(ranking1)
        db.session.add(ranking2)
        db.session.commit()

        # Realizar la solicitud GET para obtener el ranking
        response = self.client.get(f'/ranking/{trivia.id}', headers={'Authorization': f'Bearer {self.token}'})
        response_data = response.json

        # Validar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['code'], '200')
        self.assertIn('Ranking recuperado exitosamente', response_data['message'])

        # Validar el contenido del ranking
        self.assertEqual(response_data['data']['trivia']['id'], trivia.id)
        self.assertEqual(len(response_data['data']['ranking']), 2)
        self.assertEqual(response_data['data']['ranking'][0]['user_name'], "User 2")
        self.assertEqual(response_data['data']['ranking'][0]['score'], 15)
        self.assertEqual(response_data['data']['ranking'][1]['user_name'], "User 1")


