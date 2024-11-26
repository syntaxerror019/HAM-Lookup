from flask import Flask, jsonify, render_template_string, request, render_template
import requests
from PyPDF2 import PdfReader
import io

app = Flask(__name__)

BASE_URL = "https://www.wt9v.net/license/printlicense.php?callsign="

def fetch_pdf_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return io.BytesIO(response.content)

def extract_pdf_data(pdf_bytes):
    reader = PdfReader(pdf_bytes)

    if len(reader.pages) != 1:
        return None

    page = reader.pages[0]
    text = page.extract_text()
    lines = text.split('\n')

    data = {
        "callsign": lines[3],
        "name": lines[4],
        "address": f"{lines[5]} {lines[6]}",
        "frn": lines[7],
        "special_conditions": lines[8],
        "grant_date": lines[9].split()[0],
        "effective_date": lines[9].split()[1],
        "print_date": lines[9].split()[2],
        "expiration_date": lines[9].split()[3],
        "operator_privileges": lines[10].split()[0],
        "station_privileges": lines[10].split()[1],
    }
    return data

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/lookup", methods=["POST"])
def lookup():
    url = BASE_URL + request.form.get("callsign", "")

    try:
        pdf_bytes = fetch_pdf_data(url)
        if not pdf_bytes:
            return jsonify({"error": "Failed to fetch PDF"}), 400

        data = extract_pdf_data(pdf_bytes)
        if not data:
            return jsonify({"error": "Invalid PDF format"}), 400

        return render_template("lookup.html", **data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
