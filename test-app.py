import numpy as np
from flask import Flask, request
from prometheus_client import Counter, Histogram, generate_latest, start_http_server
import time

app = Flask(__name__)

# Define Prometheus metrics
REQUEST_COUNTER = Counter('app_requests_total', 'Total number of requests')
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration in seconds')

# Endpoint for processing requests and performing matrix multiplication
@app.route('/multiply/<int:number>', methods=['GET'])
def multiply_matrices(number):
    start_time = time.time()

    # Perform CPU-intensive matrix multiplication
    result = perform_calculations(number)

    # Record request duration
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)

    # Increment request counter
    REQUEST_COUNTER.inc()

    return result

# Endpoint for exposing Prometheus metrics
@app.route('/metrics', methods=['GET'])
def expose_metrics():
    return generate_latest(REQUEST_COUNTER, REQUEST_DURATION)

# Function for CPU-intensive matrix multiplication
def perform_calculations(number):
    matrix_a = np.random.randint(1, 10, size=(number, number))
    matrix_b = np.random.randint(1, 10, size=(number, number))
    result = np.dot(matrix_a, matrix_b)
    return f"Matrix multiplication result:\n{result}"

if __name__ == '__main__':
    # Start Prometheus metrics endpoint
    start_http_server(8000)

    # Start Flask application
    app.run()
