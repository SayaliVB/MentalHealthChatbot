## Run the Flask app:

      python api_for_db.py

 Flask runs on: http://localhost:5000

## Frontend Setup (React + Vite)
1-Navigate to frontend:
  cd chatbot-app

2-Install Node modules:
  npm install

3-Create a .env file in chatbot-app

  VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key

  How to create a Google API Key:
   - Visit: https://console.cloud.google.com/
   - Need  Maps JavaScript API + Places API + Geolocation API

4-Run the frontend server
   npm run dev

Frontend runs on: http://localhost:5173