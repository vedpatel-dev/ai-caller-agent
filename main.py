import os
import json
import base64
import asyncio
import websockets
import audioop
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# fetching everything from the .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TARGET_PHONE_NUMBER = os.getenv("TARGET_PHONE_NUMBER")
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN") 
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Initializing Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

print(f"--- SERVER STARTING ---")

SYSTEM_PROMPT = """
You are an established patient calling your clinic because you have a scheduling conflict and are also running out of your medication.

BEHAVIOR & RULES:
- Start the call by saying you need to cancel your upcoming appointment for this Thursday at 2:00 PM because you have a work emergency.
- As soon as the agent confirms the cancellation, immediately ask for a medication refill: "Since I can't make it in, can you just call in a refill for my Metformin to my CVS pharmacy?"
- If the agent says they need to reschedule your appointment first, refuse. Say: "I don't know my schedule yet, I just really need my pills by tomorrow so I don't run out."
- If the agent tells you that a doctor must see you before authorizing a refill, act frustrated. Argue back: "But I've been on this for years, can't you just give me a one-month supply?"
- After pushing back once or twice, eventually accept whatever solution they offer (or say you will call back when you have your schedule) and politely hang up.
"""

# Webhook
@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    
    # 1. Start the Stream
    connect = Connect()
    # Twilio to stream live audio to WebSocket URL
    connect.stream(url=f"wss://{NGROK_DOMAIN}/media-stream")
    
    response.append(connect)
    
    # return XML as Twilio easily understand
    return HTMLResponse(content=str(response), media_type="application/xml")

# Gemini Audio model
MODEL_ID = "models/gemini-2.5-flash-native-audio-preview-12-2025" 

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):

    # accept the connection from Twilio
    await websocket.accept()
    print("!!! Media Stream WebSocket Accepted !!!")
    
    # for two way audio flow tunnel
    gemini_ws_url = f"wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={GEMINI_API_KEY}"
    
    # establish the connection to Gemini server
    async with websockets.connect(gemini_ws_url) as gemini_ws:
        
        setup_msg = {
            "setup": {
                "model": "models/gemini-2.5-flash-native-audio-preview-12-2025", 
                "generationConfig": {
                    # Telling Gemini to repsond in voice data and not text
                    "responseModalities": ["audio"]
                },
                # plugging system promt instructions
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}
            }
        }
        # Send configuration to Gemini's server
        await gemini_ws.send(json.dumps(setup_msg))
        # Wait for Gemini to confirm it 
        await gemini_ws.recv() 
        
        # Initializing the ID to track specific phone strem
        stream_sid = None
       
        resample_state_in = None  # Twilio to Gemini
        resample_state_out = None   # Gemini to Twilio

        async def receive_from_twilio():
            # previosuly initialized variables
            nonlocal stream_sid, resample_state_in
            try:
                while True:
                    # wait for the data to arrive from phone line
                    data = await websocket.receive_text()
                    packet = json.loads(data)

                    # Check if this is the very first message from Twilio
                    if packet['event'] == 'start':
                        # then extract unquie ID for this call
                        stream_sid = packet['start']['streamSid']

                    # Check if packet conatin media (voice data) 
                    elif packet['event'] == 'media' and stream_sid:
                        # convert text audio string to raw digital bytes
                        raw_payload = base64.b64decode(packet['media']['payload'])
                        # audio from phone format to computer format 
                        audio_pcm = audioop.ulaw2lin(raw_payload, 2)
                        
                        # Resample 8000 Hz -> 16000 as Twilio operates on 8k and Gemini undersatnds 16k better
                        audio_pcm_16k, resample_state_in = audioop.ratecv(
                            audio_pcm, 2, 1, 8000, 16000, resample_state_in
                        )
                        
                        # sending processed 16k audio to Gemini
                        await gemini_ws.send(json.dumps({
                            "realtimeInput": {
                                "mediaChunks": [{
                                    "mimeType": "audio/pcm;rate=16000", 
                                    "data": base64.b64encode(audio_pcm_16k).decode("utf-8")
                                }]
                            }
                        }))
            except Exception as e:
                print(f"Twilio Input Loop Error: {e}")

        async def receive_from_gemini():
            nonlocal resample_state_out

           
            try:
                while True:
                    # Wait for Gemini to send message (voice to text)
                    message = await gemini_ws.recv()
                    response = json.loads(message)
                    
                    # If Gemini is sending real response turn, as gemini sends too much noisy data
                    if "serverContent" in response and "modelTurn" in response["serverContent"]:
                        # grab all components from AI response
                        parts = response["serverContent"]["modelTurn"].get("parts", [])
                        for part in parts:
                            if "inlineData" in part and stream_sid:
                                raw_audio = base64.b64decode(part["inlineData"]["data"])
                                # Gemini 16,000 Hz to 8,000 Hz for Twilio
                                audio_pcm_8k, resample_state_out = audioop.ratecv(
                                    raw_audio, 2, 1, 16000, 8000, resample_state_out
                                )
                                # convert to phone compatible
                                ulaw_payload = audioop.lin2ulaw(audio_pcm_8k, 2)
                                await websocket.send_text(json.dumps({
                                    "event": "media",
                                    "streamSid": stream_sid,
                                    "media": {"payload": base64.b64encode(ulaw_payload).decode("utf-8")}
                                }))
            except Exception as e:
                # if the connection drops
                print(f"Gemini Output Loop Error: {e}")

        # Execute and wait
        await asyncio.gather(receive_from_twilio(), receive_from_gemini())
        print("Session Ended....")

# create web URL path to trigger call
@app.get("/make-call")
async def make_outbound_call():
    try:
        # Dual Recording help us hear both sides clearly
        call = client.calls.create(
            from_=str(TWILIO_PHONE_NUMBER),
            to=str(TARGET_PHONE_NUMBER),
            url=f"https://{NGROK_DOMAIN}/incoming-call",
            record=True,
            recording_channels="dual" # Channel 1 = AI Patient, Channel 2 = Receiver
        )
        print(f"--- CALL INITIATED ---")
        
        return {"message": "Call initiated with recording", "sid": call.sid}
    except Exception as e: 
        print(f"Call Error: {e}")
        return {"error": str(e)}