import time
import requests

class Status:
    def __init__(self, status, filename, timestamp, explanation):
        self.status = status
        self.filename = filename
        self.timestamp = timestamp
        self.explanation = explanation

    def is_done(self):
        return self.status == "done"

class GPTExplainerClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def upload(self, file_path, email=None):
        url = f"{self.base_url}/upload"
        files = {"file": open(file_path, "rb")}
        data = {}
        if email:
            data = {"email": email}
        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            json_data = response.json()
            return json_data["uid"]
        else:
            return None

    def status(self, uid):
        url = f"{self.base_url}/status/{uid}"
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            return Status(
                json_data["status"],
                json_data["filename"],
                json_data["timestamp"],
                json_data["explanation"]
            )
        else:
            return None

if __name__ == "__main__":
    client = GPTExplainerClient("http://localhost:5000")
    file_path = "C:/Users/becky/Desktop/Assignments-Python/untitled/FinalGPTProj/Tests.pptx"
    email = "example@example.com"
    uid = client.upload(file_path, email=email)

    if uid is not None:
        # Log the upload status
        print(f"Upload successful. UID: {uid}")

        # Wait for the explainer to generate the explanation
        while True:
            status = client.status(uid)
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
    else:
        # Log the upload failure
        print("Upload failed. Please check the server.")
