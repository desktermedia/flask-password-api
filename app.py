from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os
import random
import threading
import time
import zipfile

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
    # Zufällige ID generieren
    file_id = str(random.randint(1000, 9999))
    filename = filename.replace("+", " ")
    base_name = os.path.splitext(os.path.basename(filename))[0]

    # Archivname mit ID am Ende
    archive_name = f"{base_name}_ID_{file_id}.zip"

    exe_source = "base.exe"
    exe_target = f"{base_name}.exe"

    if os.path.exists(exe_source):
        # Kopie der exe-Datei erstellen
        with open(exe_source, "rb") as src, open(exe_target, "wb") as dst:
            dst.write(src.read())

        # ZIP-Archiv ohne Passwort erstellen
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as archive:
            archive.write(exe_target)

        # temporäre Datei entfernen
        os.remove(exe_target)

        # automatische Löschung nach 5 Minuten
        remove_later(archive_name, delay=300)
    else:
        return jsonify({"error": "base.exe not found"}), 404

    return jsonify({
        "download_url": f"/getfile/{archive_name}",
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
