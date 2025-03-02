import os
import csv
import requests
import configparser
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from googlesearch import search

# Cargar configuración desde el archivo .conf
config = configparser.ConfigParser()
config.read("config.conf")

API_KEY = config.get("settings", "api_key")
BASE_URL = config.get("settings", "base_url")
SQUID_PROXY = config.get("settings", "squid_proxy")
OUTPUT_FOLDER = config.get("settings", "output_folder")

# Asegurar que la carpeta de salida exista
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)

# 🔥 Configuración de CORS 🔥
CORS(app, supports_credentials=True)

# Middleware para agregar headers CORS a todas las respuestas
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# 🔥 Manejar solicitudes OPTIONS para evitar bloqueos de CORS 🔥
@app.route('/generate_keywords', methods=['OPTIONS'])
@app.route('/update_csv', methods=['OPTIONS'])
def handle_preflight():
    response = jsonify({"message": "Preflight OK"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route('/generate_keywords', methods=['POST'])
def generate_keywords():
    data = request.json
    theme = data.get("theme", "integral")  # Valor por defecto

    n_combinations = 3
    n_combinations_text = f"{n_combinations}"

    prompt = (
        f"Provide list of {n_combinations_text} key words combinations to find the best sources of information about {theme} on Google. "
        "Present combinations as a list formatted like this: [Python web scraping, Data science tutorials, Machine learning examples]"
    )

    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
    )

    response = client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant who knows everything.",
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
    )

    message = response.choices[0].message.content

    print(f"Assistant: {message}")

    # Eliminar corchetes y comillas adicionales
    cleaned_message = message.strip("[]").replace('"', '').replace("'", "")
    # Dividir la cadena en una lista de combinaciones de palabras clave
    keyword_combinations = [combination.strip() for combination in cleaned_message.split(',')]

    n_URL = 3
    table_name = os.path.join(OUTPUT_FOLDER, f'{theme}.csv')

    urls_found = []

    with open(table_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Theme", "Keyword Combination", "Num URLs", "URL"])

        for keywords in keyword_combinations:
            try:
                for url in search(keywords, num_results=n_URL):
                    writer.writerow([theme, keywords, n_URL, url])
                    urls_found.append(url)  # Guardamos las URLs
            except Exception as e:
                print(f"Error al buscar '{keywords}': {e}")

    # Enviar las URLs al Squid Proxy para precaching
    cache_results = cache_urls_with_squid(urls_found)

    return jsonify({
        "message": "CSV file generated and URLs cached",
        "file": table_name,
        "cached_urls": cache_results
    })

def cache_urls_with_squid(urls):
    """
    Envia solicitudes a través del proxy Squid para precargar las URLs.
    """
    results = []
    proxies = {"http": SQUID_PROXY, "https": SQUID_PROXY}

    for url in urls:
        try:
            response = requests.get(url, proxies=proxies, timeout=5)  # Usar Squid Proxy
            if response.status_code == 200:
                results.append({"url": url, "status": "cached"})
            else:
                results.append({"url": url, "status": f"error {response.status_code}"})
        except requests.RequestException as e:
            results.append({"url": url, "status": f"failed: {str(e)}"})

    return results

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
