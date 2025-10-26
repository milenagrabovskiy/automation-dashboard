from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

RESULTS_FILE = os.path.join("results", "latest.json")


def load_test_results():
    if not os.path.exists(RESULTS_FILE):
        return []

    with open(RESULTS_FILE, "r") as f:
        data = json.load(f)

    # Adapt this depending on your JSON structure
    # Example pytest-json format
    results = []
    for test in data.get("tests", []):
        results.append({
            "name": test.get("nodeid"),
            "outcome": test.get("outcome"),
            "duration": test.get("duration"),
        })
    return results


@app.route("/")
def dashboard():
    results = load_test_results()
    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
