import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr
from config import SYS_PARM_FIELDS

DEBUG=True

load_dotenv(override=True)

SERVICENOW_INSTANCE = os.getenv('SERVICENOW_INSTANCE')
SERVICENOW_USERNAME = os.getenv('SERVICENOW_USERNAME')
SERVICENOW_PASSWORD = os.getenv('SERVICENOW_PASSWORD')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
MODEL = "gpt-oss:latest"

openai = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')

system_message = """
        You are an IT operations assistant. You have access to current ServiceNow incidents.
        When asked about incidents, use the provided incident data to answer questions.
        Keep responses concise and professional.
        """

def get_incidents_assignedto_username_servicenow(username):

    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    params = {
        "sysparm_query": "stateNOT IN6,7,8^assigned_to.user_name="+username,
        "sysparm_limit": 10,
        "sysparm_fields": ",".join(SYS_PARM_FIELDS.keys())
    }
    try:
        response = requests.get(
            url,
            auth=(SERVICENOW_USERNAME, SERVICENOW_PASSWORD),
            headers=headers,
            params=params
        )
        if response.status_code != 200:
            raise Exception(f'Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())

        if DEBUG:
            print(json.dumps(response.json(), ensure_ascii=False))
        return response.json()['result']
    except Exception as e:
        return f"Error fetching incidents: {str(e)}"
    
def get_incident_by_number_servicenow(number):
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    params = {
        "sysparm_query": "number="+number,
        "sysparm_limit": 1,
        "sysparm_fields": ",".join(SYS_PARM_FIELDS.keys())
    }
    try:
        response = requests.get(
            url,
            auth=(SERVICENOW_USERNAME, SERVICENOW_PASSWORD),
            headers=headers,
            params=params
        )
        if response.status_code != 200:
            raise Exception(f'Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        
        if DEBUG:
            print(json.dumps(response.json(), ensure_ascii=False))
        return response.json()['result']
    except Exception as e:
        return f"Error fetching incidents: {str(e)}"
    
def format_incidents_for_prompt(incidents):
    """Format incidents for prompt"""
    if not incidents:
        return "No incidents found."
    
    if isinstance(incidents, str):  # Error message
        return incidents
    
    formatted = []
    for incident in incidents[:10]:  # Limit to 10 incidents
        incident_data = {}
        
        # Iterar sobre cada campo en la configuración
        for field_name, field_config in SYS_PARM_FIELDS.items():
            label = field_config["label"]
            empty_value = field_config["empty_value"]
            
            # Campo simple (no anidado)
            value = incident.get(field_name, None)
            
            # Si el valor está vacío o None, usar valor por defecto
            if not value or str(value).strip() == '':
                incident_data[label] = empty_value
            else:
                incident_data[label] = value
        
        formatted.append(incident_data)
    
    return json.dumps(formatted, indent=2, ensure_ascii=False)

def get_incidents_assignedto_username(username):
    
    incidents = get_incidents_assignedto_username_servicenow(username)
    if isinstance(incidents, list):
        incidents_data = format_incidents_for_prompt(incidents)
    else:
        incidents_data = incidents  # Error message
    
    return incidents_data

def get_incident_by_number(number):
    return format_incidents_for_prompt(get_incident_by_number_servicenow(number))

get_incidents_assignedto_function = {
    "name": "get_incidents_assignedto_username",
    "description": "Get all the incidents assigned to an user using his User Id",
    "parameters": {
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "Employee's user id",
            },
        },
        "required": ["useername"],
        "additionalProperties": False
    }
}

get_incident_by_number_function = {
    "name": "get_incident_by_number",
    "description": "Get a single incident by incident number.",
    "parameters": {
        "type": "object",
        "properties": {
            "number": {
                "type": "string",
                "description": "Incident ID. Should start by 'INC' a followed by 7 digits. Example: INC0123456",
            },
        },
        "required": ["number"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": get_incidents_assignedto_function},
    {"type": "function", "function": get_incident_by_number_function}
]

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

gr.ChatInterface(fn=chat).launch(server_port=7870)