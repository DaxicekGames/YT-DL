from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_apscheduler import APScheduler
import yt_dlp
import os
import uuid
import re
import shutil
from zipfile import ZipFile
from datetime import datetime

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[\\/:"*?<>|]+', '_', name)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')

@app.route("/")
def index():
    return send_from_directory("", "index.html")

@app.route("/api/info", methods=["POST"])
def video_info():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL není zadána"}), 400

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)

            if '_type' in info and info['_type'] == 'playlist':
                title = info.get('title', 'Playlist')
                count = len(info.get('entries', []))
                return jsonify({"title": f"Playlist: {title} ({count} videí)", "is_playlist": True})

            # Získání všech rozlišení
            resolutions = sorted(
                {f.get("height") for f in info.get("formats", []) if f.get("height")},
                reverse=True
            )
            qualities = [str(r) for r in resolutions]

            return jsonify({
                "title": info.get("title", "Neznámý název"),
                "is_playlist": False,
                "qualities": qualities or ["best"]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download")
def download():
    url = request.args.get("url")
    format = request.args.get("format", "mp4")
    quality = request.args.get("quality", "best")

    uid = str(uuid.uuid4())
    temp_dir = os.path.join(DOWNLOAD_FOLDER, uid)
    os.makedirs(temp_dir, exist_ok=True)

    # Výběr formátu
    if format == "mp3":
        ydl_format = "bestaudio"
    elif format == "webm":
        ydl_format = f"bestvideo[ext=webm][height<={quality}]+bestaudio[ext=webm]/best[ext=webm]"
    else:
        ydl_format = f"bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4]"

    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(title).200s.%(ext)s'),
        'quiet': True,
        'format': ydl_format,
        'noplaylist': False,
        'postprocessors': [],
        'merge_output_format': format if format != "mp3" else None,
    }

    if format == 'mp3':
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = os.listdir(temp_dir)
        if len(files) == 1:
            file_path = os.path.join(temp_dir, files[0])
            return send_file(file_path, as_attachment=True, download_name=sanitize_filename(files[0]))
        else:
            zip_path = os.path.join(DOWNLOAD_FOLDER, f"{uid}.zip")
            with ZipFile(zip_path, 'w') as zipf:
                for fname in files:
                    zipf.write(os.path.join(temp_dir, fname), arcname=sanitize_filename(fname))
            shutil.rmtree(temp_dir)
            return send_file(zip_path, as_attachment=True, download_name="playlist.zip")

    except Exception as e:
        return f"Chyba při stahování: {str(e)}", 500


# 🧹 Čištění složky downloads
def clean_downloads():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] Spouštím čištění složky downloads...")

    for item in os.listdir(DOWNLOAD_FOLDER):
        item_path = os.path.join(DOWNLOAD_FOLDER, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            elif os.path.isfile(item_path):
                os.remove(item_path)
        except Exception as e:
            print(f"⚠️ Nepodařilo se smazat {item}: {e}")

# 🕒 Naplánování denního čištění
class Config:
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
scheduler.add_job(id='daily_cleanup', func=clean_downloads, trigger='cron', hour=0, minute=0)

if __name__ == "__main__":
    app.config.from_object(Config())
    app.run(host="0.0.0.0", port=5050)
