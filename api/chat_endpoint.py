"""
LoungeIQ — Chat endpoint
Add this to api/main.py to connect the chatbot to the dashboard
"""

from pydantic import BaseModel
import anthropic
import json
import os

# Add this class and endpoint to your main.py

class ChatRequest(BaseModel):
    message: str

# Add to main.py:
# @app.post("/chat")
# def chat_endpoint(req: ChatRequest):
#     from chatbot.agent import chat
#     reply, _ = chat(req.message, [])
#     return {"reply": reply}
