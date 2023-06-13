import os
import json
import glob
import asyncio
from ProjGpt import responses_from_server

UPLOADS_FOLDER = "uploads"
OUTPUTS_FOLDER = "outputs"

async def process_files():
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

            # Call the function to get responses from the server
            explanation = await responses_from_server(upload_file)

            with open(output_file, "w") as f:
                json.dump(explanation, f)

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
