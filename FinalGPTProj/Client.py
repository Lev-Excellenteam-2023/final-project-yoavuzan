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

    def upload(self, file_path):
        url = f"{self.base_url}/upload"
        files = {"file": open(file_path, "rb")}
        response = requests.post(url, files=files)

        if response.status_code == 200:
            json_data = response.json()
            return json_data["uid"]

        raise Exception("Upload failed")

    def status (self, uid):
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

        raise Exception("Status check failed")


if __name__ == "__main__":
    client = GPTExplainerClient("http://localhost:5000")
    file_path = "C:/Users/becky/Assignments/untitled/FinalGPTProj/Tests.pptx"
    uid = client.upload(file_path)
    print(f"Upload successful. UID: {uid}")

    # Wait for the explainer to generate the explanation
    while True:
        status = client.status(uid)
        if status.is_done():
            print("Explanation generated:")
            print(f"Filename: {status.filename}")
            print(f"Timestamp: {status.timestamp}")
            print(f"Explanation: {status.explanation}")
            break
        elif status.status == "not found":
            print("File not found. Please check the UID.")
            break
        else:
            print("Explanation is still in progress. Please wait...")
            time.sleep(10)
