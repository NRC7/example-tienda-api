# Trivia API

- Trivia API es un proyecto que permite gestionar una plataforma de trivias con funcionalidades para usuarios,
    preguntas, trivias y rankings. Este repositorio incluye la implementación de la API,
    documentación básica y una configuración para ejecutarla en un entorno local utilizando Docker.

## Características
- Registro e inicio de sesión con autenticación JWT.
- Gestión de usuarios, preguntas y trivias.
- Participación en trivias con cálculo automático de puntajes.
- Visualización de rankings.

## Algunas Tecnologías utilizadas
- Python 3.x
- Flask
- SQLite
- Docker
- Jwt

## Requisitos previos
1. [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/).
2. Clonar este repositorio:
   ```bash
   git clone https://github.com/nrc7/trivia-api.git
   cd trivia-api

## Ejecutar el proyecto con Docker Compose
- Este proyecto está configurado para ejecutarse mediante Docker Compose. Sigue estos pasos para ponerlo en funcionamiento:

1. Construir y ejecutar los contenedores: Ejecuta los siguientes comandos en la raíz del proyecto:
    
    docker-compose build
    docker-compose up
  
2. Acceder a la API: La API estará disponible en http://localhost:5000.

Nota: La base de datos SQLite se inicializa automáticamente cuando se ejecuta la API por primera vez. El archivo de base de datos trivia.db se guardará en el contenedor, pero se puede acceder a él mediante el volumen configurado.
Nota adicional: Si deseas eliminar la base de datos y reiniciar el entorno, puedes ejecutar:
    docker-compose down
    docker-compose up --build
