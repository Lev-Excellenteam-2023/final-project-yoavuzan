from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from DbUserUpload import Base, User, Upload
import os
import hashlib
from datetime import datetime

app = Flask(__name__)

UPLOADS_FOLDER = "uploads"
OUTPUTS_FOLDER = "outputs"

# Database configuration
def create_database_engine():
    engine = create_engine('sqlite:///db/explainer.db')
    Base.metadata.create_all(engine)
    return engine


def get_session():
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def generate_uid(filename, timestamp):
    unique_str = f"{filename}{timestamp}"
    uid = hashlib.md5(unique_str.encode('utf-8')).hexdigest()
    return uid


@app.route("/")
def hello():
    return render_template('hello.html')


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    email = request.form.get("email")  # Get the optional email parameter
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file.save(os.path.join(UPLOADS_FOLDER, filename))

    uid = generate_uid(filename, timestamp)

    # Store the uploaded file information in the database
    session = get_session()
    user = None
    if email:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            session.add(user)

    # Convert timestamp to Python datetime object
    upload_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S")

    upload = Upload(uid=uid, filename=filename, upload_time=upload_time, user=user, status=Upload.STATUS_PENDING)
    session.add(upload)
    session.commit()
    session.close()

    return jsonify({"uid": uid})


@app.route("/status", methods=["GET"])  # Accepts the UID as a query parameter
def status():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "UID parameter is missing"}), 400

    session = get_session()
    upload = session.query(Upload).filter_by(uid=uid).first()

    if upload:
        data = {
            "status": upload.status,
            "filename": upload.filename,
            "timestamp": upload.upload_time,
            "explanation": None
        }

        if upload.finish_time:
            # Load the explanation from the output file if it's available
            output_file = os.path.join(OUTPUTS_FOLDER, f"{uid}.json")
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    data["explanation"] = f.read()

        session.close()
        return jsonify(data)
    else:
        session.close()
        return jsonify({"status": "not found"})


if __name__ == "__main__":
    app.debug = True
    app.run()
