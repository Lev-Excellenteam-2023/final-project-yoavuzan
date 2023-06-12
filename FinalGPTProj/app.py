from flask import Flask, request, jsonify, render_template
import os
import uuid
from datetime import datetime
import glob

app = Flask(__name__)

UPLOADS_FOLDER = "uploads"
OUTPUTS_FOLDER = "outputs"


@app.route("/")
def hello():
    return  render_template('Hello.html')


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    uid = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{uid}_{file.filename}"
    file.save(os.path.join(UPLOADS_FOLDER, filename))
    return jsonify({"uid": uid})


@app.route("/status/<uid>", methods=["GET"])
def status(uid):
    upload_files = glob.glob(f"{UPLOADS_FOLDER}/*_{uid}_*")
    output_files = glob.glob(f"{OUTPUTS_FOLDER}/*_{uid}_*")

    if len(upload_files) == 0:
        return jsonify({"status": "not found"})

    upload_file = upload_files[0]
    filename = os.path.basename(upload_file).split("_", 1)[1]
    time = upload_file.split("_", 1)[0].split("\\")[-1]
    timestamp = datetime.strptime(time, "%Y%m%d%H%M%S")

    if len(output_files) > 0:
        with open(output_files[0], "r") as f:
            explanation = f.read()
        return jsonify({
            "status": "done",
            "filename": filename,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "explanation": explanation
        })

    return jsonify({
        "status": "pending",
        "filename": filename,
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "explanation": None
    })


if __name__ == "__main__":
    app.debug = True
    app.run()
