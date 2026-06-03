import json
from openai import OpenAI
from config import OLLAMA_BASE_URL, MODEL, DEBUG
from tools import tools, get_incidents_assignedto_username, get_incident_by_number, get_filter, get_business_rules_filtered

openai = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')
system_message = """
        You are an IT operations assistant and ServiceNow expert. You have access to current ServiceNow incidents and configuration objects.
        When asked about incidents, use the provided incident data to answer questions.
        When asked about ServiceNow configuration, use the provided configuration objects to answer questions.
        Keep responses concise and professional.

        Available ServiceNow tables and their fields:
        - incident: assigned_to, number, caller_id, category, subcategory, cmdb_ci, state, impact, urgency, priority, assignment_group, short_description, description, work_notes_list, comments
        - sys_script (Business Rule): name, active, sys_table, condition, filter_condition, action_insert, action_update, action_delete, action_query, script, when
        - sys_ui_action: name, active, table, condition, client, script
        - sys_script_client: name, active, table, type, field, client, script
        - sys_ui_policy: short_description, active, table, conditions, sys_ui_policy_action
        - sys_script_include: name, client_callable, active, script

        When filtering business rules, use 'sys_table' field to filter by table name.
        When filtering incidents, use fields like 'assigned_to', 'number', 'category', etc.
        
        If you're unsure about a field name, ask for clarification or use 'sys_table' for business rules.
        """

def handle_tool_calls(message):
    if DEBUG:
        print("DEBUG: handle_tool_calls called")
    responses = []
    for tool_call in message.tool_calls:
        if DEBUG:
            print(f"DEBUG: Processing tool call: {tool_call.function.name}")
        if tool_call.function.name == "get_incidents_assignedto_username":
            arguments = json.loads(tool_call.function.arguments)
            username = arguments.get('username')
            if DEBUG:
                print(f"DEBUG: Getting incidents for username: {username}")
            details = get_incidents_assignedto_username(username)
            if DEBUG:
                print(f"DEBUG: Got incidents data: {type(details)}")
            responses.append({
                "role": "tool",
                "content": details,
                "tool_call_id": tool_call.id
            })
        elif tool_call.function.name == "get_incident_by_number":
            arguments = json.loads(tool_call.function.arguments)
            number = arguments.get('number')
            if DEBUG:
                print(f"DEBUG: Getting incident by number: {number}")
            details = get_incident_by_number(number)
            if DEBUG:
                print(f"DEBUG: Got incident data: {type(details)}")
            responses.append({
                "role": "tool",
                "content": details,
                "tool_call_id": tool_call.id
            })
        elif tool_call.function.name == "get_filter":
            arguments = json.loads(tool_call.function.arguments)
            table_name = arguments.get('table_name')
            filters = arguments.get('filters', [])
            logic_operator = arguments.get('logic_operator', 'AND')
            if DEBUG:
                print(f"DEBUG: Generating filter for table: {table_name}")
                print(f"DEBUG: Filters: {filters}")
                print(f"DEBUG: Logic operator: {logic_operator}")

            # Generar filtro manualmente
            filter_string = get_filter(table_name, filters, logic_operator)
            if DEBUG:
                print(f"DEBUG: Generated filter string: {filter_string}")
            responses.append({
                "role": "tool",
                "content": json.dumps({
                    "generated_filter": filter_string,
                    "table": table_name,
                    "filters": filters,
                    "logic_operator": logic_operator
                }, indent=2, ensure_ascii=False),
                "tool_call_id": tool_call.id
            })
        elif tool_call.function.name == "get_business_rules_filtered":
            arguments = json.loads(tool_call.function.arguments)
            filters = arguments.get('filters', [])
            logic_operator = arguments.get('logic_operator', 'AND')
            if DEBUG:
                print(f"DEBUG: Getting business rules with filters: {filters}")
                print(f"DEBUG: Logic operator: {logic_operator}")

            details = get_business_rules_filtered(filters, logic_operator)
            if DEBUG:
                print(f"DEBUG: Got business rules data: {type(details)}")
            responses.append({
                "role": "tool",
                "content": details,
                "tool_call_id": tool_call.id
            })
    return responses

def chat(message, history):
    if DEBUG:
        print(f"DEBUG: Chat called with message: {message}")
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    if DEBUG:
        print(f"DEBUG: Sending messages to LLM: {len(messages)} messages")
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
    if DEBUG:
        print(f"DEBUG: LLM response received, finish_reason: {response.choices[0].finish_reason}")

    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        if DEBUG:
            print(f"DEBUG: Processing tool calls...")
        responses = handle_tool_calls(message)
        messages.append(message)
        messages.extend(responses)
        if DEBUG:
            print(f"DEBUG: Added {len(responses)} tool responses")
        response = openai.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        if DEBUG:
            print(f"DEBUG: Next LLM response, finish_reason: {response.choices[0].finish_reason}")

    if DEBUG:
        print(f"DEBUG: Final response: {response.choices[0].message.content}")
    return response.choices[0].message.content