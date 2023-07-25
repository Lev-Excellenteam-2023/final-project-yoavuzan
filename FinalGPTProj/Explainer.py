import time
import os
import json
import glob
import asyncio
from sqlalchemy.exc import IntegrityError  # Import the IntegrityError class
from sqlalchemy.orm import sessionmaker
from DbUserUpload import Upload, Base, DB_FILE, OUTPUTS_FOLDER, UPLOADS_FOLDER
from sqlalchemy import create_engine
from ProjGpt import responses_from_server


def create_database_engine():
    engine = create_engine(f'sqlite:///{DB_FILE}')
    Base.metadata.create_all(engine)
    return engine

import uuid

def upload_file_with_email(client, file_path, email=None):
    while True:
        uid = str(uuid.uuid4())  # Generate a random UUID
        if email:
            uid = client.upload(file_path, email=email, uid=uid)  # Pass the generated UID to the client
        else:
            uid = client.upload(file_path, uid=uid)  # Pass the generated UID to the client

        # Check if the generated uid already exists in the database
        engine = create_engine(f'sqlite:///{DB_FILE}')
        Session = sessionmaker(bind=engine)
        session = Session()
        existing_upload = session.query(Upload).filter_by(uid=uid).first()

        if not existing_upload:
            break  # The uid is unique, break out of the loop

    return uid


def check_status(client, uid):
    status = client.status(uid)
    return status


async def process_files():
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)

    while True:
        upload_files = glob.glob(f"{UPLOADS_FOLDER}/*.pptx")

        for upload_file in upload_files:
            filename = upload_file.split("\\")[-1]
            output_file = os.path.join(OUTPUTS_FOLDER, f"{filename}.json")

            if os.path.exists(output_file):
                # Log that the file has already been processed
                print(f"Skipped {filename}. File already processed.")
                continue

            print(f"Processing {filename}")

            # Create a new upload record in the database
            session = Session()
            upload = Upload(filename=filename, status="processing")
            session.add(upload)
            session.commit()

            # Call the function to get responses from the server
            explanation = await responses_from_server(upload_file)

            # Save the explanation to the output file
            with open(output_file, "w") as f:
                json.dump(explanation, f)

            # Update upload status and finish_time in the database
            upload.status = "done"
            upload.set_finish_time()
            session.commit()

            print(f"Finished processing {filename}")

        await asyncio.sleep(10)

async def main():
    # Log that the file processing has started
    print("File processing started.")

    await process_files()

if __name__ == "__main__":
    # Log that the main function is being executed
    print("Main function execution started.")

    asyncio.run(main())
