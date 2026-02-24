# Autonomous AI Caller Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Twilio](https://img.shields.io/badge/Twilio-F22F46?style=flat&logo=twilio&logoColor=white)](https://www.twilio.com/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

## Overview
This project implements a highly responsive, autonomous voice bot capable of calling and engaging live in real calls, natural phone conversations. 

Designed to be highly versatile, the agent can be customized via prompts to fulfill almost any conversational role. Whether it's autonomously calling to book appointments, acting as a friendly conversational companion to help someone talk through their day, or deeply understanding and interacting with complex human emotions, this agent handles it seamlessly. 

Powered by **Twilio's bi-directional Media Streams**, **FastAPI**, and **Google’s Gemini 2.5 Flash Native Audio model**, the system processes voice-to-voice data with incredibly low latency, resulting in a human like interactive experience.

## Prerequisites
* **Python 3.8+**
* **Twilio Account** with an active phone number.
* **Google Gemini API Key** (Requires access to the `gemini-2.5-flash-native-audio-preview-12-2025` model).
* **Ngrok** to securely tunnel the local web server to the public internet for Twilio webhooks.

## 💻 Setup & Installation

**1. Clone the repository and navigate to the project folder:**
```bash
git clone [https://github.com/vedpatel-dev/ai-caller-agent.git](https://github.com/vedpatel-dev/ai-caller-agent.git)
cd "ai-caller-agent"
```

**2. Set up a virtual environment:**
```bash
# Mac/Linux
python -m venv venv
source venv/bin/activate  

# Windows
python -m venv venv
venv\Scripts\activate
```
**Note:** If python is not recognized, try using py or python3 instead.

**3. Install the required dependencies:**
```bash
pip install -r requirements.txt
```

```markdown
### 🌐 Ngrok Configuration
1. **Download:** [Get ngrok for Windows](https://ngrok.com/download).
2. **Setup:** Place `ngrok.exe` in your project root.
3. **Tunnel:** Start the tunnel on port 8000:
   ```bash
   .\ngrok.exe http 8000
   ```

**4. Configure Environment Variables:**

Create a file exactly named .env in the root of your project directory. This file safely stores your API credentials and phone configurations.
```bash
GEMINI_API_KEY=create_your_google_gemini_api_key_here
TWILIO_ACCOUNT_SID=create_your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=create_your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=create_your_twilio_purchased_phone_number_here
TARGET_PHONE_NUMBER=enter_the_destination_phone_number_here
NGROK_DOMAIN=enter_your_ngrok_forwarding_domain_here
```

**⚙️ How to Run the Bot**

You will need three separate terminal windows to run the system locally.

**Step 1: Start the Ngrok Tunnel**

Twilio requires a public HTTPS URL to communicate with your local machine. Start an ngrok tunnel on port 8000:
```bash
ngrok http 8000
```
**Step 2: Start the FastAPI Server**

In a new terminal window, launch the application server:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

**Step 3: Trigger the Outbound Call**

In a final terminal window, run the trigger script (or simply navigate to http://127.0.0.1:8000/make-call in your web browser) to instruct Twilio to dial the destination number:
```bash
python trigger.py
```

## Connect with the Developer 
Built by **Ved Patel**. If you're interested in AI, machine learning, or quantitative development, let's connect!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ved-rajeshkumar-patel-vrp)