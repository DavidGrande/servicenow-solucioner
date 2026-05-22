import json
from config import SYS_PARM_FIELDS
from servicenow_request import get_incidents_assignedto_username_servicenow, get_incident_by_number_servicenow
from formatter import format_incidents_for_prompt

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