# app.py
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import py7zr, tempfile, os, random, string

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://save-drop.netlify.app"}})

# Diese beiden Dateien müssen im Repo / im Render-Image liegen
EXE_FILE = "base.exe"      # deine echte EXE
DUMMY_DLL = "dummy.dll"    # wird bei Bedarf erzeugt
PASSWORD_STORE = "/tmp/passwords"
os.makedirs(PASSWORD_STORE, exist_ok=True)

def generate_password():
    return ''.join(random.choices(string.digits, k=4))

def ensure_dummy_dll(path, size_mb=28):
    """Erzeuge 28MB-DLL nur einmal, streaming (keine großen RAM-Objekte)."""
    if os.path.exists(path):
        return
    chunk = b"\0" * (1024 * 1024)          # 1 MB Nullbytes
    with open(path, "wb") as f:
        for _ in range(size_mb):
            f.write(chunk)

@app.route("/download/<path:filename>")
def download(filename):
    # z.B. filename = "tester+supi+77.zip"
    keyword = filename.rsplit(".", 1)[0].replace("+", " ")
    password = generate_password()

    # Vorbedingungen prüfen
    if not os.path.exists(EXE_FILE):
        return jsonify({"error": "base.exe not found on server"}), 500

    ensure_dummy_dll(DUMMY_DLL, 28)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, f"{keyword}.7z")
            # Kompressions-Filter flach halten, um CPU/Timeout zu vermeiden:
            # COPY = keine Kompression (schnell, aber groß)
            # Alternativ: LZMA2 mit niedrigem preset (1) für leichtere Kompression
            filters = [{'id': py7zr.FILTER_LZMA2, 'preset': 1}]
            with py7zr.SevenZipFile(out_path, 'w', password=password, filters=filters) as z:
                # Ohne Kopieren, nur arcname setzen
                z.write(EXE_FILE, arcname=f"{keyword}.exe")
                z.write(DUMMY_DLL, arcname=os.path.basename(DUMMY_DLL))

            # Passwort ablegen (überlebt den Request in /tmp)
            with open(os.path.join(PASSWORD_STORE, f"{keyword}.txt"), "w") as f:
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
