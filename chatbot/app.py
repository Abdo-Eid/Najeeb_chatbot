from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from .bot import get_bot_response

app = Flask(__name__, static_folder=".")
CORS(app)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(f"{app.static_folder}/assets", filename)

# Define a route that listens for POST requests at "/chat"
@app.route("/chat", methods=["POST"])
def chat():
    # Get the JSON data sent in the request body
    data = request.get_json()
    
    # Extract the "message" field from the JSON data (default to empty string if not provided)
    message = data.get("message", "")
    
    debug = app.config.get("DEBUG", False)  # Get debug flag from config
    response = get_bot_response(message, debug=debug)
    
    # Return the bot's response as a JSON object
    return jsonify({"response": response})


# if __name__ == "__main__":
#     app.run(debug=True)
