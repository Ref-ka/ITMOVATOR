import time
import logging
from flask import Flask, request, jsonify
from schemas.request import PredictionRequest, PredictionResponse
from utils.logger import setup_logger
from YaGPT2 import search_information, generate_answer

# Initialize Flask app
app = Flask(__name__)

# Setup logger
logger = setup_logger()


@app.before_request
def log_requests():
    request.start_time = time.time()
    body = request.get_data(as_text=True)
    logger.info(f"Incoming request: {request.method} {request.url}\nRequest body: {body}")


@app.after_request
def log_response(response):
    process_time = time.time() - request.start_time
    response_body = response.get_data(as_text=True)

    logger.info(
        f"Request completed: {request.method} {request.url}\n"
        f"Status: {response.status_code}\n"
        f"Response body: {response_body}\n"
        f"Duration: {process_time:.3f}s"
    )
    return response

@app.route('/', methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to ITMovator API",
        "status": "success",
        "data": {}
    })

@app.route("/api/request", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        body = PredictionRequest(**data)  # Ensure data is parsed correctly
        logger.info(f"Processing prediction request with id: {body.id}")

        # Correct attribute name
        search_results = search_information(body.query)  # Change from `question` to `query`
        final_answer = generate_answer(body.query, search_results, body.id)

        # Return the final answer directly as JSON
        return jsonify(final_answer), 200

    except ValueError as e:
        logger.exception(f"Validation error for request {body.id}: {str(e)}")
        return jsonify({"detail": str(e)}), 400
    except Exception as e:
        logger.exception(f"Internal error processing request {body.id}: {str(e)}")
        return jsonify({"detail": "Internal server error"}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
