# tools/nearest_therapist_tool.py

from langchain.tools import BaseTool
from typing import ClassVar, Type
from pydantic import BaseModel, Field
import requests

def get_global_ip():
    with open('host_config.txt') as f:
        return f.read().strip()

global_ip = get_global_ip()

class NearestTherapistInput(BaseModel):
    location: str = Field(..., description="Comma-separated latitude and longitude. Example: '37.7749,-122.4194'")

class NearestTherapistLocatorTool(BaseTool):
    name: ClassVar[str] = "NearestTherapistLocator"
    description: ClassVar[str] = (
        "Use this tool when the user says 'find nearest therapists'. "
        "The input should be a comma-separated latitude and longitude, like '37.7749,-122.4194'."
    )
    args_schema: Type[BaseModel] = NearestTherapistInput    
    return_direct: ClassVar[bool] = True

    def _run(self, location: str) -> str:
        try:
            lat, lng = map(float, location.strip().split(","))
            url = f"{global_ip}/api/nearby-doctors?lat={lat}&lng={lng}"
            response = requests.get(url)
            data = response.json()

            if "results" not in data:
                return "Sorry, I couldn't find any therapists near your location."

            results = data["results"][:5]
            
            formatted = [
                f"🔹 **{r['name']}**\n"
                f"📍 {r['vicinity']}\n"
                f"⭐ Rating: {r.get('rating', 'No rating')}\n"
                f"🗺️ [Get Directions](https://www.google.com/maps/search/?api=1&query={requests.utils.quote(r['name'] + ' ' + r['vicinity'])})"
                for r in results
            ]

            return (
                "🧠 Here are some nearby therapists I found:\n\n" + "\n\n".join(formatted)
                if formatted else "No therapists found nearby."
            )
        except Exception as e:
            return f"Error fetching therapists: {e}"

    async def _arun(self, location: str) -> str:
        raise NotImplementedError("Async not supported.")
