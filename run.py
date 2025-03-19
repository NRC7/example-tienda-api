from app import create_app
import os
# Crear la aplicación Flask
app = create_app()

# Correr la aplicación
if __name__ == "__main__":
    a = os.getenv("FLASK_ENV")
    print(f"Running in {a} mode")
    if (os.getenv("FLASK_ENV") == "production"):
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        context = ("localhost-cert.pem", "localhost-key.pem")
        app.run(host="0.0.0.0", port=5000, ssl_context=context, debug=True)    
        
