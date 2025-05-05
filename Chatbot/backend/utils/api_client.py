# utils/api_client.py
import requests

def get_global_ip():
    with open('host_config.txt') as f:
        return f.read().strip()

global_ip = get_global_ip()

class APIClient:
    """
    Wrapper class for all backend API calls.
    """

    def __init__(self, base_url=f"{global_ip}"):
        self.base_url = base_url

    def get_chat_summary(self, user_id: int) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/get_chat_summary",
                json={"user_id": user_id}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("session_summary", "No summary found.")
            return "Failed to fetch chat summary."
        except Exception as e:
            return f"Error in API call: {e}"

    # Add other API calls here if needed
    # def store_chat_summary(...)
    # def verify_login(...)
    # etc.
