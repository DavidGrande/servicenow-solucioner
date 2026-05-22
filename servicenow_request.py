import requests
import json
from config import SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD, SYS_PARM_FIELDS

DEBUG=True

def get_incidents_assignedto_username_servicenow(username):
    url = f"https://{SERVICENOW_INSTANCE}/api/now/table/incident"
    headers = {"Content-Type":"application/json","Accept":"application/json"}
    params = {
        "sysparm_query": "stateNOT IN6,7,8^assigned_to.user_name="+username,
        "sysparm_limit": 10,
        "sysparm_fields": ",".join(SYS_PARM_FIELDS.keys()),
        "sysparm_display_value": "all"
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
        "sysparm_fields": ",".join(SYS_PARM_FIELDS.keys()),
        "sysparm_display_value": "all"
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