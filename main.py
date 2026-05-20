import os
from dotenv import load_dotenv
import requests
import json
from openai import OpenAI
import gradio as gr

load_dotenv(override=True)

# Configuration
SERVICENOW_INSTANCE = os.getenv('SERVICENOW_INSTANCE')
SERVICENOW_USERNAME = os.getenv('SERVICENOW_USERNAME')
SERVICENOW_PASSWORD = os.getenv('SERVICENOW_PASSWORD')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
OLLAMA_MODEL = "gpt-oss:latest"

assigned_to = "dgtes"

incidents_cache = []

def get_incidents():
    global incidents_cache

    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    params = {
        "sysparm_query": "stateNOT IN6,7,8^assigned_to.user_name="+assigned_to,
        "sysparm_limit": 10
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
        
        incidents = response.json()['result']
        incidents_cache = incidents
        return incidents
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
        formatted.append({
            "number": incident.get('number', 'N/A'),
            "short_description": incident.get('short_description', 'No description'),
            "priority": incident.get('priority', 'N/A'),
            "assigned_to": incident.get('assigned_to', {}).get('display_value', 'Unassigned'),
            "opened_at": incident.get('opened_at', 'N/A')
        })
    
    return json.dumps(formatted, indent=2)

def get_ollama_response(prompt, incidents_data):
    """Get response from Ollama"""
    try:
        # Create system prompt with incident context
        system_prompt = """
        You are an IT operations assistant. You have access to current ServiceNow incidents.
        When asked about incidents, use the provided incident data to answer questions.
        Keep responses concise and professional.
        """
        
        # Initialize OpenAI client for Ollama
        ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')
        
        # Create chat completion
        response = ollama.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {incidents_data}\n\nUser question: {prompt}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Return the actual response content
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error contacting Ollama: {str(e)}"

def respond(message, chat_history):
    """Main chat function"""
    # Get incidents if cache is empty
    if not incidents_cache:
        incidents = get_incidents()
        if isinstance(incidents, list):
            incidents_data = format_incidents_for_prompt(incidents)
        else:
            incidents_data = incidents  # Error message
    else:
        incidents_data = format_incidents_for_prompt(incidents_cache)
    
    # Get response from Ollama
    response = get_ollama_response(message, incidents_data)
    
    # Return both the message and response in proper format
    return "", chat_history + [[message, response]]

# Create Gradio interface
with gr.Blocks(title="ServiceNow Incident Assistant") as demo:
    gr.Markdown("# ServiceNow Incident Assistant")
    gr.Markdown("Ask questions about your active incidents. I'll retrieve current data from ServiceNow and answer using Ollama.")
    
    chatbot = gr.Chatbot(label="Chat")
    msg = gr.Textbox(label="Your Message", placeholder="Ask about incidents...")
    clear = gr.Button("Clear Chat")
    
    # Chat history state
    history = gr.State([])
    
    # Handle message submission
    msg.submit(respond, [msg, history], [msg, history]).then(
        lambda: None, None, chatbot, js="() => {setTimeout(() => {document.querySelector('.chatbot').scrollTop = document.querySelector('.chatbot').scrollHeight;}, 100);}"
    )
    
    # Handle clear button
    clear.click(lambda: [], None, chatbot)
    
    # Update chatbot with history
    history.change(lambda x: x, history, chatbot)

# Launch the app
if __name__ == "__main__":
    print("Starting ServiceNow Incident Assistant...")
    print(f"ServiceNow Instance: {SERVICENOW_INSTANCE}")
    print(f"Ollama Base URL: {OLLAMA_BASE_URL}")
    demo.launch(server_name="0.0.0.0", server_port=7860)