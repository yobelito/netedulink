FROM python:3.9

WORKDIR /app

# Copiar todos los archivos de la carpeta actual al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]