from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import py7zr, tempfile, os, random, string

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://save-drop.netlify.app"}})

EXE_FILE = "base.exe"      # deine echte EXE, liegt im Repo
PASSWORD_STORE = "/tmp/passwords"
os.makedirs(PASSWORD_STORE, exist_ok=True)

def generate_password():
    return ''.join(random.choices(string.digits, k=4))

@app.route("/download/<path:filename>")
def download(filename):
    keyword = filename.rsplit(".", 1)[0].replace("+", " ")
    password = generate_password()

    if not os.path.exists(EXE_FILE):
        return jsonify({"error": "base.exe not found on server"}), 500

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, f"{keyword}.7z")

            # Passwort-geschütztes Archiv erzeugen
            with py7zr.SevenZipFile(out_path, 'w', password=password) as z:
                z.write(EXE_FILE, arcname=f"{keyword}.exe")

            # Passwort in /tmp sichern
            pw_file = os.path.join(PASSWORD_STORE, f"{keyword}.txt")
            with open(pw_file, "w") as f:
                f.write(password)

            return send_file(out_path, as_attachment=True, download_name=f"{keyword}.7z")
    except Exception as e:
        return jsonify({"error": f"build failed: {e}"}), 500

@app.route("/get-password")
def get_password():
    file = (request.args.get("file", "") or "").rsplit(".", 1)[0].replace("+", " ")
    pw_path = os.path.join(PASSWORD_STORE, f"{file}.txt")
    if os.path.exists(pw_path):
        with open(pw_path, "r") as f:
            return jsonify({"password": f.read().strip()})
    return jsonify({"password": "error"})

@app.route("/")
def ok():
    return "API is running."
