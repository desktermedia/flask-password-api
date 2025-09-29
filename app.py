from flask import Flask, request, send_file, jsonify
import py7zr
import tempfile
import os
import random
import string
import shutil

app = Flask(__name__)

# Pfade zu Originaldateien (müssen im Render-Verzeichnis liegen)
EXE_FILE = "base.exe"
DUMMY_DLL = "dummy.dll"
PASSWORD_STORE = "/tmp/passwords"

os.makedirs(PASSWORD_STORE, exist_ok=True)

def generate_password():
    return ''.join(random.choices(string.digits, k=4))

@app.route('/download/<path:filename>')
def download(filename):
    keyword = filename.rsplit('.', 1)[0].replace('+', ' ')
    password = generate_password()

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, f"{keyword}.7z")
        exe_dest = os.path.join(tmpdir, f"{keyword}.exe")
        dll_dest = os.path.join(tmpdir, DUMMY_DLL)

        # Kopiere Originaldateien ins Temp-Verzeichnis
        shutil.copy(EXE_FILE, exe_dest)
        shutil.copy(DUMMY_DLL, dll_dest)

        # 7z Archiv mit Passwort erstellen
        with py7zr.SevenZipFile(zip_path, 'w', password=password) as archive:
            archive.write(exe_dest, arcname=f"{keyword}.exe")
            archive.write(dll_dest, arcname=DUMMY_DLL)

        # Passwort zwischenspeichern
        with open(os.path.join(PASSWORD_STORE, f"{keyword}.txt"), "w") as f:
            f.write(password)

        return send_file(zip_path, as_attachment=True, download_name=f"{keyword}.7z")

@app.route('/get-password')
def get_password():
    file = request.args.get("file", "").replace('+', ' ').rsplit('.', 1)[0]
    pw_path = os.path.join(PASSWORD_STORE, f"{file}.txt")
    if os.path.exists(pw_path):
        with open(pw_path, "r") as f:
            return jsonify({"password": f.read().strip()})
    return jsonify({"password": "error"})

@app.route('/')
def hello():
    return "API is running."
