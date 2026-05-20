import os
from dotenv import load_dotenv
import requests
import json
from openai import OpenAI
from datetime import datetime

load_dotenv(override=True)

# Configuration
SERVICENOW_INSTANCE = os.getenv('SERVICENOW_INSTANCE')
SERVICENOW_USERNAME = os.getenv('SERVICENOW_USERNAME')
SERVICENOW_PASSWORD = os.getenv('SERVICENOW_PASSWORD')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
OLLAMA_MODEL = "gpt-oss:latest"

assigned_to = "dgtes"

print(SERVICENOW_INSTANCE);

def get_incidents():
    """Fetch pending incidents from ServiceNow"""
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    params = {
        "sysparm_query": "stateNOT IN6,7,8^assigned_to.user_name="+assigned_to,
        "sysparm_limit": 10
    }
    response = requests.get(
        url,
        auth=(SERVICENOW_USERNAME, SERVICENOW_PASSWORD),
        headers=headers,
        params=params
    )
    if response.status_code != 200:
        raise Exception(f'Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
    
    return response.json()['result']

def generate_report(incidents):
    # Prepare incident data for prompt
    incident_list = []
    for incident in incidents:
        incident_list.append({
            "number": incident['number'],
            "short_description": incident['short_description'],
            "priority": incident['priority'],
            "assigned_to": incident['assigned_to'] if incident['assigned_to'] else "Unassigned",
            "opened_at": incident['opened_at']
        })
    
    # Create prompt for OpenAI
    prompt = f"""
    Please create a summary report of the following incidents:
    
    {json.dumps(incident_list, indent=2)}
    
    Format the report as:
    - Summary of all incidents
    - Priority breakdown
    - Total incidents count
    - Recommendations for next steps
    """
    
    try:
        """ response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful IT operations assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip() """

        """Fetch and summarize a website using Ollama."""
        ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')
        response = ollama.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful IT operations assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    except Exception as e:
        return f"Error generating report: {str(e)}"

def main():
    try:
        # Fetch incidents
        print("Fetching incidents from ServiceNow...")
        incidents = get_incidents()
        print(f"Found {len(incidents)} incidents")
        
        # Generate report
        print("Generating report with Ollama...")
        report = generate_report(incidents)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"servicenow_report_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write("ServiceNow Incident Report\n")
            f.write("=" * 50 + "\n")
            f.write(report)
            f.write("\n\n")
            f.write("Raw Incident Data:\n")
            f.write(json.dumps(incidents, indent=2))
        
        print(f"Report saved to {filename}")
        print("\nReport Preview:")
        print(report)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()