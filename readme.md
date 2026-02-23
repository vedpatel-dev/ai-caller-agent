Pretty Good AI — Voice Bot Testing Challenge

Overview
This project implements an automated voice bot designed to stress-test the Pretty Good AI agent. It uses Twilio bi-directional Media Streams, FastAPI, and Google’s Gemini 2.5 Flash Native Audio model. The bot calls the provided test number and simulates a high-stress patient emergency scenario. The goal is to evaluate the agent’s responsiveness, robustness, and ability to handle sudden interruptions, emotional shifts, and complex edge cases without hallucinating or failing.

Prerequisites

Python 3.8+

Twilio account with an active phone number

Google Gemini API Key with access to: gemini-2.5-flash-native-audio-preview-12-2025

Ngrok for tunneling local webhooks

Setup & Installation

Navigate to your project folder:
cd "Pretty Good AI"

Set up a virtual environment:
python -m venv venv
source venv/bin/activate      (Mac/Linux)
venv\Scripts\activate         (Windows)

Install dependencies:
pip install fastapi uvicorn websockets twilio python-dotenv requests

Configure environment variables:
Create a file named .env in the project root and add:

GEMINI_API_KEY=your_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TARGET_PHONE_NUMBER=+18054398008
TWILIO_PHONE_NUMBER=your_twilio_number

How to Run the Bot
You will need three terminal windows.

1) Start Ngrok:
ngrok http 8000

2) Start the FastAPI server:
uvicorn main:app --host 127.0.0.1 --port 8000

3) Trigger the outbound call:
python trigger.py