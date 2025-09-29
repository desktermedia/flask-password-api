from flask import Flask, request, jsonify, send_file
import os
import random
import string
import py7zr

app = Flask(__name__)

# Speicherpfade
TMP_DIR = "/tmp/packages"
os.makedirs(TMP_DIR, exist_ok=True)

# Dummy EXE (deine echte Datei kannst du hier referenzieren)
EXE_FILE = "myexe.exe"

def generate_password():
    return ''.join(random.choices(string.digits, k=4))

@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    """
    Erstellt ein 7z-Archiv mit Passwortschutz und gibt JSON zurück:
    {
      "password": "1234",
      "download_url": "/getfile/test123.7z"
    }
    """
    keyword = filename.replace(".zip", "")
    archive_name = f"{keyword}.7z"
    archive_path = os.path.join(TMP_DIR, archive_name)

    # Passwort erzeugen
    password = generate_password()

    # Falls altes Archiv existiert, löschen
    if os.path.exists(archive_path):
        os.remove(archive_path)

    # Archiv erstellen
    with py7zr.SevenZipFile(archive_path, 'w', password=password) as archive:
        # arcname bestimmt, wie die Datei IM Archiv heißt
        archive.write(EXE_FILE, arcname=f"{keyword}.exe")

    return jsonify({
        "password": password,
        "download_url": f"/getfile/{archive_name}"
    })

@app.route("/getfile/<path:filename>", methods=["GET"])
def getfile(filename):
    """
    Gibt die reale 7z-Datei zum Download zurück.
    """
    archive_path = os.path.join(TMP_DIR, filename)
    if not os.path.exists(archive_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(archive_path, as_attachment=True)

@app.route("/", methods=["GET"])
def home():
    return "Flask Password API is running!"
