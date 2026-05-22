import json
from config import SYS_PARM_FIELDS

def format_incidents_for_prompt(incidents):
    """Format incidents for prompt"""
    if not incidents:
        return "No incidents found."
    
    if isinstance(incidents, str):  # Error message
        return incidents
    
    formatted = []
    for incident in incidents[:10]:  # Limit to 10 incidents
        incident_data = {}
        
        for field_name, field_config in SYS_PARM_FIELDS.items():
            label = field_config["label"]
            empty_value = field_config["empty_value"]
            
            field_value = incident.get(field_name, None)
            
            # Manejar campos que tienen estructura display_value/value
            if isinstance(field_value, dict) and 'display_value' in field_value:
                # Usar display_value para mostrar al usuario
                display_value = field_value.get('display_value', '')
                if not display_value or str(display_value).strip() == '':
                    incident_data[label] = empty_value
                else:
                    incident_data[label] = display_value
            else:
                # Campo simple
                if not field_value or str(field_value).strip() == '':
                    incident_data[label] = empty_value
                else:
                    incident_data[label] = field_value
        formatted.append(incident_data)
    return json.dumps(formatted, indent=2, ensure_ascii=False)