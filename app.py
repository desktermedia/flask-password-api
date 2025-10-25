from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os
import random
import threading
import time
import py7zr

app = Flask(__name__)
CORS(app)

def remove_later(path, delay=300):
    """Löscht eine Datei nach einer bestimmten Zeit automatisch."""
    def _rm():
        time.sleep(delay)
        try:
            os.remove(path)
            print(f"[CLEANUP] Deleted {path}")
        except Exception as e:
            print(f"[CLEANUP ERROR] {e}")
    t = threading.Thread(target=_rm, daemon=True)
    t.start()

@app.route("/download/<path:filename>")
def download(filename):
    password = str(random.randint(1000, 9999))
    filename = filename.replace("+", " ")
    base_name = os.path.splitext(os.path.basename(filename))[0]

    # Passwort direkt in den Dateinamen einbauen
    archive_name = f"{base_name}_PASSWORD_{password}.7z"

    exe_source = "base.exe"
    exe_target = f"{base_name}.exe"

    if os.path.exists(exe_source):
        with open(exe_source, "rb") as src, open(exe_target, "wb") as dst:
            dst.write(src.read())

        with py7zr.SevenZipFile(archive_name, 'w', password=password) as archive:
            archive.write(exe_target)

        os.remove(exe_target)
        remove_later(archive_name, delay=300)  # löscht Archiv nach 5 Minuten

    return jsonify({
        "download_url": f"/getfile/{archive_name}",
        "password": password,
        "archive_name": archive_name
    })

@app.route("/getfile/<path:filename>")
def getfile(filename):
    safe_path = os.path.basename(filename)
    if not os.path.exists(safe_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(safe_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
