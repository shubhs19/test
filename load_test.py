from locust import HttpUser, task, between, TaskSet
from urllib.parse import urlencode
import json
import time

class APITasks(TaskSet):

    def on_start(self):
        self.thread_id = self.create_session()

    def create_session(self):
        for _ in range(3):  # Retry up to 3 times
            response = self.client.post("/api/create_session")
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print("Failed to decode JSON response for session creation")
                    print(response.text)
                    return None
            else:
                print("Failed to create session")
                print(response.status_code, response.text)
                time.sleep(1)  # Wait for 1 second before retrying
        return None

    @task
    def test_get_msg_endpoint(self):
        if not self.thread_id:
            self.thread_id = self.create_session()
            if not self.thread_id:
                print("Unable to create session after multiple attempts")
                return

        data = {
            "query": "my rank is 1784 which college can i get",
            "thread_id": self.thread_id
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        for _ in range(3):  # Retry up to 3 times
            response = self.client.post("/get_msg", data=urlencode(data), headers=headers)
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(response_json)
                    return
                except json.JSONDecodeError:
                    print("Failed to decode JSON response for get_msg")
                    print(response.status_code, response.text)
                    return
            elif response.status_code == 504:
                print("504 Gateway Time-out. Retrying...")
                time.sleep(1)  # Wait for 1 second before retrying
            else:
                print("Failed to get message")
                print(response.status_code, response.text)
                return

class APIUser(HttpUser):
    tasks = [APITasks]
    host = 'https://staging-chatbot.collegesuggest.com:8000'
    wait_time = between(20,80)

# To run the test, use the following command in the terminal:
# locust -f load_test.py
