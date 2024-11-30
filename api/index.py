from flask import Flask, jsonify, render_template_string, request, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

url = "https://www.arrl.org/fcc/search"

def extract_data(payload):
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        return response.status_code, "Failed to fetch the page."
    
    soup = BeautifulSoup(response.text, 'html.parser')
    list2_div = soup.find('div', class_='list2')
    
    if not list2_div:
        return 404, "No results found."

    results = list2_div.get_text(strip=True, separator="\n").split("\n")
    results[1] = "Address: " + results[1]
    results[2] = "Location: " + results[2]

    print(results)

    return response.status_code, results

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/lookup", methods=["POST", "GET"])
@app.route("/lookup/<point>", methods=["POST", "GET"])
def lookup(point=None):
    try:
        input = request.form.get("callsign", None) or point
        if not input:
            return render_template("error.html", error="No callsign provided.", callsign="None Specified!")
        
        payload = {"data[Search][terms]": input}

        res, data = extract_data(payload)

        if res == 404:
            return render_template("error.html", error=data, callsign=input)
        
        if res != 200:
            return render_template("error.html", error=f"Failed to fetch the page, {res}", callsign=input)

        return render_template("lookup.html", data=data, callsign=input)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
