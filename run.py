from app import create_app
import os

# Crear la aplicación Flask
app = create_app()

if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    port = int(os.getenv("PORT", 5000))  # Render asigna un puerto dinámico

    print(f"Running in {env} mode on port {port}")

    if env == "production":
        app.run(host="0.0.0.0", port=port, debug=False)  # Sin SSL en Render
    else:
        context = ("localhost-cert.pem", "localhost-key.pem")  # Solo en desarrollo
        app.run(host="0.0.0.0", port=port, ssl_context=context, debug=True)
