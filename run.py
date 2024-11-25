from app import create_app

# Crear la aplicación Flask
app = create_app()

# Correr la aplicación
if __name__ == "__main__":
    app.run(debug=True)
