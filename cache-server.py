import os
import yt_dlp
from flask import Flask, send_from_directory, request

app = Flask(__name__)
CACHE_DIR = "cache/videos"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def descargar_video_youtube(url):
    """Descarga un video de YouTube y lo almacena en caché."""
    ydl_opts = {
        "format": "best",  # Descarga el mejor formato disponible
        "outtmpl": f"{CACHE_DIR}/%(title)s.%(ext)s",  # Guarda con el título del video
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.route("/download_youtube", methods=["POST"])
def download_youtube():
    """API para descargar un video de YouTube."""
    data = request.json
    video_url = data.get("url")

    if not video_url:
        return {"error": "URL no proporcionada"}, 400

    descargar_video_youtube(video_url)
    return {"status": "Video descargado con éxito"}

@app.route("/videos/<path:filename>")
def serve_video(filename):
    """Sirve los videos descargados en caché."""
    return send_from_directory(CACHE_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
