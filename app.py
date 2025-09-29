from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/get-password')
def get_password():
    file = request.args.get("file")
    if not file:
        return jsonify({"error": "missing file parameter"}), 400

    # Simuliert z. B. ein immer gleiches, aber dynamisches Passwort pro Datei
    seed = sum(ord(c) for c in file)
    random.seed(seed)
    password = f"{random.randint(1000, 9999)}"

    return jsonify({"password": password})
