from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from slack_block_to_ms_teams_adaptive_card import convert_slack_block_to_adaptive_card

app = Flask(__name__)
cors = CORS(app, resources={r"/convert": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}}, allow_headers="*", supports_credentials=True)

@app.route("/")
def index():
    return "API server is running!"

@app.route("/convert", methods=["POST"])
@cross_origin(origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_headers="*", supports_credentials=True)
def convert():
    data = request.json
    slack_json = data.get("slackJson")
    if not slack_json:
        return jsonify({"error": "Invalid input"}), 400

    try:
        ms_teams_adaptive_card_json = convert_slack_block_to_adaptive_card(slack_json)
        return jsonify({"msTeamsAdaptiveCardJson": ms_teams_adaptive_card_json})
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred during the conversion"}), 500

if __name__ == "__main__":
    app.run()
