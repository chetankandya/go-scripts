import numpy as np
from flask import Flask
from prometheus_client import Counter, Histogram, generate_latest, start_http_server
import time

app = Flask(__name__)

# Define Prometheus metrics
ITERATION_COUNTER = Counter('app_iterations_total', 'Total number of iterations')
ITERATION_DURATION = Histogram('app_iteration_duration_seconds', 'Iteration duration in seconds')

# Function for CPU-intensive matrix multiplication
def perform_calculations(number):
    matrix_a = np.random.randint(1, 10, size=(number, number))
    matrix_b = np.random.randint(1, 10, size=(number, number))
    result = np.dot(matrix_a, matrix_b)
    return result

# Background task to continuously perform matrix multiplication
def perform_matrix_multiplication():
    while True:
        start_time = time.time()

        # Perform CPU-intensive matrix multiplication
        result = perform_calculations(100)

        # Record iteration duration
        duration = time.time() - start_time
        ITERATION_DURATION.observe(duration)

        # Increment iteration counter
        ITERATION_COUNTER.inc()

        time.sleep(0.2)  # Delay between iterations

# Endpoint for exposing Prometheus metrics
@app.route('/metrics', methods=['GET'])
def expose_metrics():
    return generate_latest(ITERATION_COUNTER, ITERATION_DURATION)

if __name__ == '__main__':
    # Start Prometheus metrics endpoint
    start_http_server(8000)

    # Start the background task for matrix multiplication
    perform_matrix_multiplication()

    # Start Flask application
    app.run()
