import json
from config import SYS_PARM_FIELDS, SYS_DICTIONARY, OPERATORS, AVAILABLE_TABLES, DEBUG
from servicenow_request import get_incidents_assignedto_username_servicenow, get_incident_by_number_servicenow, get_object_servicenow
from formatter import format_incidents_for_prompt

def get_incidents_assignedto_username(username):
    if DEBUG:
        print(f"DEBUG: get_incidents_assignedto_username called with username: {username}")
    incidents = get_incidents_assignedto_username_servicenow(username)
    if DEBUG:
        print(f"DEBUG: Raw incidents data: {type(incidents)}")
    if isinstance(incidents, list):
        incidents_data = format_incidents_for_prompt(incidents)
    else:
        incidents_data = incidents  # Error message
    if DEBUG:
        print(f"DEBUG: Formatted incidents data: {type(incidents_data)}")
    return incidents_data

def get_incident_by_number(number):
    if DEBUG:
        print(f"DEBUG: get_incident_by_number called with number: {number}")
    result = get_incident_by_number_servicenow(number)
    if DEBUG:
        print(f"DEBUG: Raw incident data: {type(result)}")
    formatted = format_incidents_for_prompt(result)
    if DEBUG:
        print(f"DEBUG: Formatted incident data: {type(formatted)}")
    return formatted

def get_filter(table_name, filters, logic_operator="AND"):
    if DEBUG:
        print(f"DEBUG: get_filter called with table: {table_name}, filters: {filters}")
    if not filters:
        if DEBUG:
            print("DEBUG: No filters provided")
        return ""

    # Map string operators to ServiceNow operators
    operator_mapping = {
        "equals": "=",
        "contains": "LIKE",
        "starts_with": "STARTSWITH",
        "ends_with": "ENDSWITH",
        "greater_than": ">",
        "less_than": "<",
        "not_equals": "!",
        "is": "="
    }

    filter_parts = []
    for filter_obj in filters:
        field = filter_obj.get('field')
        operator = filter_obj.get('operator')
        value = filter_obj.get('value')

        if not field or not operator or value is None:
            continue

        if DEBUG:
            print(f"DEBUG: Processing filter - field: {field}, operator: {operator}, value: {value}")

        # Convert string operator to ServiceNow operator
        service_now_operator = operator_mapping.get(operator, operator)
        
        if service_now_operator == "=":
            filter_parts.append(f"{field}={value}")
        elif service_now_operator == "LIKE":
            filter_parts.append(f"{field}LIKE{value}")
        elif service_now_operator == "STARTSWITH":
            filter_parts.append(f"{field}STARTSWITH{value}")
        elif service_now_operator == "ENDSWITH":
            filter_parts.append(f"{field}ENDSWITH{value}")
        elif service_now_operator == ">":
            filter_parts.append(f"{field}>{value}")
        elif service_now_operator == "<":
            filter_parts.append(f"{field}<{value}")
        elif service_now_operator == "!":
            filter_parts.append(f"{field}!{value}")
        else:
            # Fallback - use the operator as-is
            filter_parts.append(f"{field}{service_now_operator}{value}")

    if filter_parts:
        result = "^".join(filter_parts) if logic_operator == "AND" else "^OR".join(filter_parts)
        if DEBUG:
            print(f"DEBUG: Generated filter string: {result}")
        return result
    return ""

def get_business_rules_filtered(filters=None, logic_operator="AND"):
    if DEBUG:
        print(f"DEBUG: get_business_rules_filtered called with filters: {filters}")
        print(f"DEBUG: Logic operator: {logic_operator}")
        print(f"DEBUG: Available fields for sys_script: name, active, sys_table, condition, filter_condition, action_insert, action_update, action_delete, action_query, script, when")
    
    if not filters:
        if DEBUG:
            print("DEBUG: No filters provided, getting all business rules")
        return json.dumps(get_object_servicenow('sys_script'), indent=2, ensure_ascii=False)

    filter_string = get_filter('sys_script', filters, logic_operator)
    if DEBUG:
        print(f"DEBUG: Generated filter string for business rules: {filter_string}")

    if not filter_string:
        return json.dumps({"error": "Invalid filters provided"}, indent=2, ensure_ascii=False)

    results = get_object_servicenow('sys_script', filter_string)
    if DEBUG:
        print(f"DEBUG: Got business rules results: {len(results) if isinstance(results, list) else 'Not a list'}")
    return json.dumps(results, indent=2, ensure_ascii=False)

get_filter_function = {
    "name": "get_filter",
    "description": "Generate a ServiceNow query filter string based on field, operator, and value. Use 'sys_table' field for business rules.",
    "parameters": {
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "The ServiceNow table name to filter on (e.g., 'incident', 'sys_script')"
            },
            "filters": {
                "type": "array",
                "description": "List of filter objects with field, operator, and value",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {
                            "type": "string",
                            "description": "Field name to filter on",
                        },
                        "operator": {
                            "type": "string",
                            "description": "Operator to use. Valid operators: equals, contains, starts_with, ends_with, greater_than, less_than, not_equals, is",
                            "enum": OPERATORS
                        },
                        "value": {
                            "type": ["string", "number", "boolean"],
                            "description": "Value to filter by"
                        }
                    },
                    "required": ["field", "operator", "value"],
                    "additionalProperties": False
                }
            },
            "logic_operator": {
                "type": "string",
                "description": "Logic operator for combining filters",
                "enum": ["AND", "OR"],
                "default": "AND"
            }
        },
        "required": ["table_name", "filters"],
        "additionalProperties": False
    }
}

get_business_rules_filtered_function = {
    "name": "get_business_rules_filtered",
    "description": "Get business rules with dynamic filtering. Use 'sys_table' field to filter by table name (e.g., 'incident').",
    "parameters": {
        "type": "object",
        "properties": {
            "filters": {
                "type": "array",
                "description": "List of filter objects. Available fields for sys_script: name, active, sys_table, condition, filter_condition, action_insert, action_update, action_delete, action_query, script, when",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {
                            "type": "string",
                            "description": "Field name to filter on (use 'sys_table' for table name). Available fields: name, active, sys_table, condition, filter_condition, action_insert, action_update, action_delete, action_query, script, when"
                        },
                        "operator": {
                            "type": "string",
                            "description": "Operator to use. Valid operators: equals, contains, starts_with, ends_with, greater_than, less_than, not_equals, is",
                            "enum": OPERATORS
                        },
                        "value": {
                            "type": ["string", "number", "boolean"],
                            "description": "Value to filter by"
                        }
                    },
                    "required": ["field", "operator", "value"],
                    "additionalProperties": False
                }
            },
            "logic_operator": {
                "type": "string",
                "description": "Logic operator for combining filters",
                "enum": ["AND", "OR"],
                "default": "AND"
            }
        },
        "additionalProperties": False
    }
}

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
        "required": ["username"],
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
    {"type": "function", "function": get_filter_function},
    {"type": "function", "function": get_business_rules_filtered_function},
    {"type": "function", "function": get_incidents_assignedto_function},
    {"type": "function", "function": get_incident_by_number_function}
]