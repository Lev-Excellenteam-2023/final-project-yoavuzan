import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from GPTExplainerClient import GPTExplainerClient
from DbUserUpload import Upload, Base

def create_database_engine():
    engine = create_engine('sqlite:///db/explainer.db')
    Base.metadata.create_all(engine)
    return engine

def upload_file_with_email(client, file_path, email=None):
    if email:
        uid = client.upload(file_path, email=email)
    else:
        uid = client.upload(file_path)
    return uid

def check_status(client, uid):
    status = client.status(uid)
    return status

if __name__ == "__main__":
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)

    client = GPTExplainerClient("http://localhost:5000")
    file_path = "C:/Users/becky/Desktop/Assignments-Python/untitled/FinalGPTProj/Tests.pptx"
    email = "example@example.com"

    with Session() as session:
        # Check if the file already exists in the database
        filename = file_path.split("\\")[-1]
        upload = session.query(Upload).filter_by(filename=filename).first()

        if upload:
            # Log that the file has already been uploaded and processed
            print(f"File '{filename}' with UID: {upload.uid} already processed.")
        else:
            # Perform the upload and get the UID
            uid = upload_file_with_email(client, file_path, email=email)

            if uid is None:
                # Log the upload failure
                print("Upload failed. Please check the server.")
                exit()

            # Log the upload status
            print(f"Upload successful. UID: {uid}")

        # Wait for the explainer to generate the explanation
        while True:
            status = check_status(client, uid)
            if status is not None:
                if status.is_done():
                    # Log the successful generation of explanation
                    print("Explanation generated:")
                    print(f"Filename: {status.filename}")
                    print(f"Timestamp: {status.timestamp}")
                    print(f"Explanation: {status.explanation}")
                    break
                elif status.status == "not found":
                    # Log file not found status
                    print("File not found. Please check the UID.")
                    break
                else:
                    # Log that explanation generation is still in progress
                    print("Explanation is still in progress. Please wait...")
                    time.sleep(10)
            else:
                # Log status check failure
                print("Failed to check status. Exiting...")
                break
