# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo el archivo requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Expón el puerto 5000 donde Flask se ejecuta
EXPOSE 5000

# Establece el comando para ejecutar la app en el contenedor
CMD ["flask", "run", "--host=0.0.0.0"]
