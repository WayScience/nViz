"""
Read OME-TIFF files from this project into Avivator
"""

import pathlib
import threading
import time
import webbrowser

from flask import Flask, Response, send_from_directory
from flask_cors import CORS

# gather relative path for this file
relpath = pathlib.Path(__file__).parent

# Define the output path for the combined OME-TIFF file
combined_output_path = relpath / "data/example_output.ome.tiff"

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/src/raw_organoid_images_to_omezarr/data/<path:filename>")
def serve_file(filename: str) -> Response:
    return send_from_directory(relpath / "data", filename)


# Function to run the Flask app
def run_flask() -> None:
    app.run(port=8005, debug=False)


# Start the Flask app in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

time.sleep(5)  # Wait for the server to start

# Open Avivator in the web browser with the URL pointing to the served file
avivator_url = "https://avivator.gehlenborglab.org/?image_url=http://localhost:8005/src/raw_organoid_images_to_omezarr/data/example_output.ome.tiff"
print("Opening a web browser to: ", avivator_url)
webbrowser.open(avivator_url)

# Keep the server running for a specified duration (e.g., 60 seconds)
try:
    time.sleep(600)
except KeyboardInterrupt:
    print("Interrupted by user")

# Shut down the Flask server
# Note: Flask does not have a built-in way to
# shut down the server cleanly from another thread.
# You may need to manually stop the script or use a
# more advanced method to stop the Flask server.
print("Server has been shut down.")
