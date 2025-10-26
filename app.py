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
    # generiere Passwort (4-stellig)
    password = str(random.randint(1000, 9999))

    # Ersetze + durch Leerzeichen, sichere Basis (basename verhindert ../)
    filename = filename.replace("+", " ")
    base_name = os.path.splitext(os.path.basename(filename))[0]

    # PASSWORD-Tag jetzt VOR dem Basisnamen
    # Beispiel: PASSWORD_1234_My File Name.7z
    archive_name = f"PASSWORD_{password}_{base_name}.7z"

    exe_source = "base.exe"
    exe_target = f"{base_name}.exe"

    if not os.path.exists(exe_source):
        return jsonify({"error": "base.exe not found"}), 404

    # Kopiere exe und erstelle verschlüsseltes 7z mit Passwort
    with open(exe_source, "rb") as src, open(exe_target, "wb") as dst:
        dst.write(src.read())

    # Erstelle 7z-Archiv mit Passwortschutz
    with py7zr.SevenZipFile(archive_name, 'w', password=password) as archive:
        archive.write(exe_target)

    # entferne temporäre exe
    os.remove(exe_target)

    # automatische Löschung nach 5 Minuten
    remove_later(archive_name, delay=300)

    # gib den genauen Archivnamen + Passwort zurück
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
