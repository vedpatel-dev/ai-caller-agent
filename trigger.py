# Import the library to send web requests 
import requests

# local URL of your FastAPI server to make call
url = "http://127.0.0.1:8000/make-call"

try:
    # Send a GET request to the URL
    response = requests.get(url)
    
    # server's confirmation message to the terminal
    print(f"Response: {response.text}")
    
except Exception as e:
    # If your FastAPI server isn't running
    print(f"Error: {e}")