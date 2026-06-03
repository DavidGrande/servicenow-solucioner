import os
from dotenv import load_dotenv
load_dotenv(override=True)

# DEBUG FLAG
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

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
    "assignment_group.name": {
        "label": "Assignment group",
        "empty_value": "Unassigned"
    },
    "short_description": {
        "label": "Short Description",
        "empty_value": "N/A"
    },
    "description": {
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

SYS_DICTIONARY = {
    "sys_script" : {
        "name": "Business Rule",
        "fields": {
            "name": {
                "type": "string",
                "description": "Name of the business rule"
            },
            "active": {
                "type": "boolean",
                "description": "Is active or no"
            },
            "sys_table": {
                "type": "string",
                "description": "Table to which it applies"
            },
            "condition": {
                "type": "string",
                "description": "Condition expression"
            },
            "filter_condition": {
                "type": "string",
                "description": "Condition expression"
            },
            "action_insert": {
                "type": "boolean",
                "description": "Whether rule runs on insert"
            },
            "action_update": {
                "type": "boolean",
                "description": "Whether rule runs on update"
            },
            "action_delete": {
                "type": "boolean",
                "description": "Whether rule runs on delete"
            },
            "action_query": {
                "type": "boolean",
                "description": "Whether rule runs on query"
            },
            "script": {
                "type": "string",
                "description": "The code that runs"
            },
            "when": {
                "type": "string",
                "description": "When its runs",
                "enum": ["before", "after", "async_always", "before_display"]
            }
        }
    },
    "sys_ui_action" : {
        "name": "UI Action",
        "fields": {
            "name": {
                "type": "string",
                "description": "Name of the UI Action"
            },
            "active": {
                "type": "boolean",
                "description": "Is active or no"
            },
            "table": {
                "type": "string",
                "description": "Table to which it applies"
            },
            "condition": {
                "type": "string",
                "description": "Condition expression"
            },
            "client": {
                "type": "boolean",
                "description": "Does it run on the client side or the server side?"
            },
            "script": {
                "type": "string",
                "description": "The code that runs"
            }
        }
    },
    "sys_script_client" : {
        "name": "Client Script",
        "fields": {
            "name": {
                "type": "string",
                "description": "Name of the Client Script"
            },
            "active": {
                "type": "boolean",
                "description": "Is active or no"            
                },
            "table": {
                "type": "string",
                "description": "Table to which it applies"            
                },
            "type": {
                "type": "string",
                "description": "When its runs",
                "enum": ["onCellEdit", "OnChange", "onLoad", "onSubmit"]
            },
            "field": {
                "type": "string",
                "description": "If type is onChange or onCellEdit, which field should change?"            
                },
            "client": {
                "type": "boolean",
                "description": "Does it run on the client side or the server side?"
            },
            "script": {
                "type": "string",
                "description": "The code that runs"
            }
        }
    },
    "sys_ui_policy" : {
        "name": "UI Policy",
        "fields": {
            "short_description": {
                "type": "string",
                "description": "Name/Short Description of the UI Policy"
            },
            "active": {
                "type": "boolean",
                "description": "Is active or no"
            },
            "table": {
                "type": "string",
                "description": "Table to which it applies"
            },
            "conditions": {
                "type": "string",
                "description": "Condition expression"
            },
            "sys_ui_policy_action": {
                "type": "array",
                "description": "Ui Policy Actions"
            }
        }
    },
    "sys_ui_policy_action" : {
        "name": "UI Policy Action",
        "fields": {
            "sys_ui_policy": {
                "type": "object",
                "description": "UI Policy"
            },
            "table": {
                "type": "string",
                "description": "Table to which it applies"
            },
            "mandatory": {
                "type": "string",
                "description": "Mandatory",
                "enum": ["ignore", "true", "false"]
            },
            "visible": {
                "type": "string",
                "description": "Visible",
                "enum": ["ignore", "true", "false"]
            },
            "disabled": {
                "type": "string",
                "description": "Read only",
                "enum": ["ignore", "true", "false"]
            },
            "cleared": {
                "type": "boolean",
                "description": "Clear the field when runs"
            },
        }
    },
    "sys_script_include" : {
        "name": "Script Include",
        "fields": {
            "name": {
                "type": "string",
                "description": "Name of the Script Include"
            },
            "client_callable": {
                "type": "boolean",
                "description": "Clear the field when runs"
            },
            "active": {
                "type": "boolean",
                "description": "Is active or no"
            },
            "script": {
                "type": "string",
                "description": "The code that runs"
            }
        }
    }
}

OPERATORS = ["equals", "contains", "starts_with", "ends_with", "greater_than", "less_than", "not_equals", "is"]
AVAILABLE_TABLES = list(SYS_DICTIONARY.keys())