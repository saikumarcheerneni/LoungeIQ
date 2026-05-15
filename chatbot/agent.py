"""
LoungeIQ — Week 4
Agentic Chatbot using Groq (Free)
"""

from groq import Groq
import json
import requests
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY", "your-key-here"))
API_BASE = "http://localhost:8000"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_all_lounge_status",
            "description": "Get current live occupancy of all airport lounges",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_lounge",
            "description": "Recommend best lounge for a passenger",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_class": {"type": "string"},
                    "loyalty_tier": {"type": "string"},
                    "gate": {"type": "string"},
                    "hour": {"type": "integer"},
                    "day_of_week": {"type": "string"}
                },
                "required": ["ticket_class", "loyalty_tier", "gate", "hour", "day_of_week"]
            }
        }
    }
]

def execute_tool(tool_name, tool_input):
    try:
        if tool_name == "get_all_lounge_status":
            res = requests.get(f"{API_BASE}/status")
            return json.dumps(res.json(), indent=2)
        elif tool_name == "recommend_lounge":
            from datetime import datetime
            payload = {
                "ticket_class": tool_input.get("ticket_class", "economy"),
                "loyalty_tier": tool_input.get("loyalty_tier", "none"),
                "gate": tool_input.get("gate", "A1"),
                "hour": tool_input.get("hour", datetime.now().hour),
                "day_of_week": tool_input.get("day_of_week", "Monday"),
                "season": "summer",
                "flight_delay": 0
            }
            res = requests.post(f"{API_BASE}/recommend", json=payload)
            return json.dumps(res.json(), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

SYSTEM_PROMPT = """
You are LoungeIQ Assistant — a friendly AI for airport lounge services.
Help passengers find eligible lounges, check occupancy, get recommendations.
When passenger gives ticket class, loyalty tier and gate — call recommend_lounge.
Ticket classes: economy, business, first
Loyalty tiers: none, silver, gold, platinum
"""

def chat(user_message, history):
    history.append({"role": "user", "content": user_message})

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if message.tool_calls:
            history.append({"role": "assistant", "content": message.content or "", "tool_calls": message.tool_calls})
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                print(f"  [Agent calling: {tool_name}]")
                result = execute_tool(tool_name, tool_input)
                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            reply = message.content
            history.append({"role": "assistant", "content": reply})
            return reply, history

def run_chatbot():
    print("\n" + "="*55)
    print("  ✈  Welcome to LoungeIQ Assistant")
    print("  Type your question or 'quit' to exit")
    print("="*55 + "\n")
    history = []
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Assistant: Safe travels! Goodbye.")
            break
        reply, history = chat(user_input, history)
        print(f"\nAssistant: {reply}\n")

if __name__ == "__main__":
    run_chatbot()