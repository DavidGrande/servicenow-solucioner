import requests
import json
from config import SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD, SYS_PARM_FIELDS, DEBUG

def get_incidents_assignedto_username_servicenow(username):
    if DEBUG:
        print(f"DEBUG: Calling ServiceNow for incidents assigned to: {username}")
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    params = {
        "sysparm_query": "stateNOT IN 6,7,8^assigned_to.user_name="+username,
        "sysparm_limit": 10,
        "sysparm_fields": ",".join(SYS_PARM_FIELDS.keys()),
        "sysparm_display_value": "all"
    }
    if DEBUG:
        print(f"DEBUG: Request params: {params}")
    try:
        response = requests.get(
            url,
            auth=(SERVICENOW_USERNAME, SERVICENOW_PASSWORD),
            headers=headers,
            params=params
        )
        if DEBUG:
            print(f"DEBUG: Response status: {response.status_code}")
        if response.status_code != 200:
            raise Exception(f'Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
        if DEBUG:
            print(json.dumps(response.json(), ensure_ascii=False))
        result = response.json()['result']
        if DEBUG:
            print(f"DEBUG: ServiceNow returned {len(result)} incidents")
        return result
    except Exception as e:
        if DEBUG:
            print(f"DEBUG: Error fetching incidents: {str(e)}")
        return f"Error fetching incidents: {str(e)}"

def get_incident_by_number_servicenow(number):
    if DEBUG:
        print(f"DEBUG: Calling ServiceNow for incident number: {number}")
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    params = {
        "sysparm_query": "number="+number,
        "sysparm_limit": 1,
        "sysparm_fields": ",".join(SYS_PARM_FIELDS.keys()),
        "sysparm_display_value": "all"
    }
    if DEBUG:
        print(f"DEBUG: Request params: {params}")
    try:
        response = requests.get(
            url,
            auth=(SERVICENOW_USERNAME, SERVICENOW_PASSWORD),
            headers=headers,
            params=params
        )
        if DEBUG:
            print(f"DEBUG: Response status: {response.status_code}")
        if response.status_code != 200:
            raise Exception(f'Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())

        if DEBUG:
            print(json.dumps(response.json(), ensure_ascii=False))
        result = response.json()['result']
        if DEBUG:
            print(f"DEBUG: ServiceNow returned incident data")
        return result
    except Exception as e:
        if DEBUG:
            print(f"DEBUG: Error fetching incident: {str(e)}")
        return f"Error fetching incidents: {str(e)}"

def get_object_servicenow(table, filter):
    if DEBUG:
        print(f"DEBUG: Calling ServiceNow for object: {table} by filter: {filter}")
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/" + table
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    params = {
        "sysparm_query": filter,
        "sysparm_limit": 100,
        "sysparm_display_value": "all"
    }
    if DEBUG:
        print(f"DEBUG: Request params: {params}")
    try:
        response = requests.get(
            url,
            auth=(SERVICENOW_USERNAME, SERVICENOW_PASSWORD),
            headers=headers,
            params=params
        )
        if DEBUG:
            print(f"DEBUG: Response status: {response.status_code}")
        if response.status_code != 200:
            raise Exception(f'Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())

        if DEBUG:
            print(json.dumps(response.json(), ensure_ascii=False))
        result = response.json()['result']
        if DEBUG:
            print(f"DEBUG: ServiceNow returned {len(result)} {table} records")
        return result
    except Exception as e:
        if DEBUG:
            print(f"DEBUG: Error fetching {table}: {str(e)}")
        return f"Error fetching {table}: {str(e)}"