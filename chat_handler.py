import json
from openai import OpenAI
from config import OLLAMA_BASE_URL, MODEL
from tools import tools, get_incidents_assignedto_username, get_incident_by_number

openai = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')

system_message = """
        You are an IT operations assistant. You have access to current ServiceNow incidents.
        When asked about incidents, use the provided incident data to answer questions.
        Keep responses concise and professional.
        """

def handle_tool_calls(message):
    responses = []
    for tool_call in message.tool_calls:
        if tool_call.function.name == "get_incidents_assignedto_username":
            arguments = json.loads(tool_call.function.arguments)
            username = arguments.get('username')
            details = get_incidents_assignedto_username(username)
            responses.append({
                "role": "tool",
                "content": details,
                "tool_call_id": tool_call.id
            })
        elif tool_call.function.name == "get_incident_by_number":
            arguments = json.loads(tool_call.function.arguments)
            number = arguments.get('number')
            details = get_incident_by_number(number)
            responses.append({
                "role": "tool",
                "content": details,
                "tool_call_id": tool_call.id
            })
    return responses

def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    
    return response.choices[0].message.content