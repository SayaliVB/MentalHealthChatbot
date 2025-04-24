# utils/api_client.py
import requests

class APIClient:
    """
    Wrapper class for all backend API calls.
    """

    def __init__(self, base_url="http://127.0.0.1:5000"):
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
