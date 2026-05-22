import os
from dotenv import load_dotenv

load_dotenv(override=True)

#SERVICENOW CONNECTION
SERVICENOW_INSTANCE = os.getenv('SERVICENOW_INSTANCE')
SERVICENOW_USERNAME = os.getenv('SERVICENOW_USERNAME')
SERVICENOW_PASSWORD = os.getenv('SERVICENOW_PASSWORD')

#OLLAMA
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
MODEL = os.getenv('MODEL')

#INCIDENT FIELDS
SYS_PARM_FIELDS = {
    "assigned_to.user_name": {
        "label": "Assigned to",
        "empty_value": "Unassigned"
    },
    "number": {
        "label": "Number",
        "empty_value": "N/A"
    },
    "caller_id.user_name": {
        "label": "Caller",
        "empty_value": "Unassigned"
    },
    "category": {
        "label": "Category",
        "empty_value": "N/A"
    },
    "subcategory": {
        "label": "Subcategory",
        "empty_value": "N/A"
    },
    "cmdb_ci": {
        "label": "Configuration Item",
        "empty_value": "N/A"
    },
    "state": {
        "label": "State",
        "empty_value": "N/A"
    },
    "impact": {
        "label": "Impact",
        "empty_value": "N/A"
    },
    "urgency": {
        "label": "Urgency",
        "empty_value": "N/A"
    },
    "priority": {
        "label": "Priority",
        "empty_value": "N/A"
    },
    "u_business_stopper": {
        "label": "Business Stopper",
        "empty_value": "False"
    },
    "assignment_group.name": {
        "label": "Assignment group",
        "empty_value": "Unassigned"
    },
    "short_description": {
        "label": "Short Description",
        "empty_value": "N/A"
    },
    "u_description": {
        "label": "Description",
        "empty_value": "N/A"
    },
    "work_notes_list": {
        "label": "Work notes",
        "empty_value": "No work notes"
    },
    "comments": {
        "label": "Additional comments",
        "empty_value": "No comments"
    }
}