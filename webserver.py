from flask import Flask, request, jsonify, render_template
import logging

def start_flask_app(incoming_queue, outgoing_queue):
    app = Flask(__name__)

    # Set up logging for debugging
    logging.basicConfig(level=logging.INFO)

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/send_message', methods=['POST'])
    def send_message():
        data = request.get_json()
        user_message = data.get('message')
        if user_message:
            logging.info(f"Received message: {user_message}")
            incoming_queue.put(user_message)
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "error": "No message provided"}), 400

    @app.route('/get_responses', methods=['GET'])
    def get_responses():
        responses = []
        while not outgoing_queue.empty():
            response = outgoing_queue.get()
            logging.info(f"Sending response to client: {response}")
            responses.append(response)
        return jsonify({"responses": responses})

    app.run(host='0.0.0.0', port=8000, debug=False)