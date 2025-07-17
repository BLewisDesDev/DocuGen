# test_care_plan_llm.py
import ollama
import json
from datetime import datetime

def build_care_plan_prompt(client_data, concerns_text=""):
    """
    Build a comprehensive prompt for generating care plan content
    """
    
    # Extract client information
    personal = client_data.get('personal_info', {})
    services = client_data.get('service_information', {}).get('services', [])
    location = client_data.get('location', {})
    
    # Determine service types
    service_types = [s['service_type'] for s in services if s['status'] == 'active']
    service_codes = [s['service_code'] for s in services if s['status'] == 'active']
    
    # Build context about client
    client_name = f"{personal.get('given_name', 'Client')} {personal.get('family_name', '')}"
    age_context = "elderly client" if personal.get('birth_date') else "client"
    location_context = f"in {location.get('suburb', 'the community')}"
    
    prompt = f"""You are a professional care coordinator at Caura Aged Care (cauraagedcare.com.au) creating a CHSP (Commonwealth Home Support Programme) care plan.

CLIENT INFORMATION:
- Name: {client_name}
- Services: {', '.join(service_types)}
- Location: {location_context}
- Service History: {len(services)} active services

CLIENT CONCERNS:
{concerns_text if concerns_text else "No specific concerns documented."}

CAURA SERVICES CONTEXT (CHSP COMPLIANT):
- Domestic Assistance (DA): House cleaning services provided fortnightly for 2 hours - general cleaning, dishwashing, clothes washing and ironing. Note: Does NOT include linen services, meal preparation, accompanied activities, or financial advice.
- Garden Maintenance (HM): Monthly garden maintenance for all clients focusing on safety and accessibility. Includes essential pruning, yard clearance, and lawn mowing for client safety and access. Additionally provides 2 safety focused services per client including window cleaning, gutter cleaning, property hazard identification and safety repairs. All services must relate directly to client safety, accessibility and independence (not aesthetic).

CARE PLAN REQUIREMENTS:
Generate appropriate content for the following sections. Use realistic, professional language suitable for formal care documentation.

TASK 1 - CLIENT GOALS (3 goals maximum):
Create realistic goals based on the client's service needs. Consider:
- Independence maintenance
- Safety and wellbeing
- Quality of life improvements
- Service-specific outcomes

TASK 2 - SERVICE DETAILS TABLE (3 entries maximum):
For each goal, provide:
- Care Need: What specific need does this address? (Must align with CHSP service scope)
- Goal: The outcome we want to achieve (Must focus on independence, safety, accessibility)
- Intervention: Specific CHSP-compliant actions/services to achieve the goal (Must be within service type scope and safety-focused)

TASK 3 - ASSISTANCE TASKS (4 tasks maximum):
List specific, actionable tasks our staff will perform. Must be:
- Within CHSP Domestic Assistance (fortnightly 2-hour house cleaning sessions) or Garden Maintenance scope
- Safety-focused for Garden Maintenance tasks (including make-safe property services)
- Reference monthly garden maintenance schedule and fortnightly domestic assistance
- Reference biannual make-safe services
- Compliant with Work Health and Safety requirements
- Measurable and realistic for entry-level support

TASK 4 - WHS ISSUES:
Identify potential workplace health and safety concerns based on the client's situation and services.

TASK 5 - OTHER INFO:
Any additional relevant information for care delivery.

OUTPUT FORMAT:
Provide your response as a structured JSON object with the following exact format:

{{
    "client_goals": [
        "Goal 1 description",
        "Goal 2 description", 
        "Goal 3 description"
    ],
    "service_details": [
        {{
            "care_need": "Care need 1",
            "goal": "Goal 1 description", 
            "intervention": "Intervention 1"
        }},
        {{
            "care_need": "Care need 2",
            "goal": "Goal 2 description",
            "intervention": "Intervention 2" 
        }},
        {{
            "care_need": "Care need 3",
            "goal": "Goal 3 description",
            "intervention": "Intervention 3"
        }}
    ],
    "assistance_tasks": [
        "Task 1",
        "Task 2", 
        "Task 3",
        "Task 4"
    ],
    "whs_issues": "WHS concerns or 'None identified'",
    "other_info": "Additional information or 'None'"
}}

QUALITY STANDARDS (CHSP COMPLIANCE):
- Use professional, clinical language aligned with CHSP Standards
- Be specific and measurable within service type limitations
- Align goals with CHSP-compliant interventions only
- Consider CHSP guidelines, client dignity, and wellness/reablement approach
- Ensure Garden Maintenance tasks are safety-focused, not aesthetic
- Ensure Domestic Assistance focuses on fortnightly 2-hour house cleaning sessions
- Reference monthly garden maintenance and biannual make-safe property services
- All interventions must support independence, safety, and accessibility
- Default to safety-focused outcomes when information is limited
- Consider Work Health and Safety requirements for both client and worker

Generate the care plan content now:"""
    
    return prompt

def test_care_plan_generation():
    """Test the LLM with sample client data"""
    
    # Sample client data (your JSON structure)
    sample_client = {
        "caura_id": "CL00000001",
        "personal_info": {
            "given_name": "Mary",
            "family_name": "Thompson",
            "birth_date": "1945-03-15",
            "gender_code": "F"
        },
        "location": {
            "address_1": "23 Oak Street",
            "address_2": None,
            "suburb": "Blacktown",
            "state_code": "NSW",
            "postcode": "2148"
        },
        "service_information": {
            "services": [
                {
                    "service_type": "domestic_assistance",
                    "service_code": "DA",
                    "status": "active",
                    "start_date": "2025-01-15",
                    "session_count": 24
                },
                {
                    "service_type": "home_maintenance", 
                    "service_code": "HM",
                    "status": "active",
                    "start_date": "2025-02-01",
                    "session_count": 12
                }
            ]
        }
    }
    
    # Sample concerns text (shortened to 1.5 sentences)
    sample_concerns = """18/11/24 Mary suffers from mobility issues and uses a walking frame. 18/11/24 Mary is unable to mow her"""
    
    try:
        # Build the prompt
        prompt = build_care_plan_prompt(sample_client, sample_concerns)
        
        print("=" * 60)
        print("TESTING CARE PLAN LLM GENERATION")
        print("=" * 60)
        print(f"Client: {sample_client['personal_info']['given_name']} {sample_client['personal_info']['family_name']}")
        print(f"Services: DA, HM")
        print(f"Concerns: {sample_concerns}")
        print("=" * 60)
        
        # Call the LLM with configurable model
        model_name = 'llama3.2:1b'  # Change this to your preferred model
        
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            options={
                'temperature': 0.3,  # Lower temperature for more consistent output
                'top_p': 0.9,
                'max_tokens': 2000
            }
        )
        
        response_text = response['message']['content']
        print("RAW LLM RESPONSE:")
        print("-" * 40)
        print(response_text)
        print("-" * 40)
        
        # Try to parse JSON from the response
        try:
            # Look for JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                parsed_data = json.loads(json_text)
                
                print("\nPARSED CARE PLAN DATA:")
                print("=" * 40)
                
                print("\nCLIENT GOALS:")
                for i, goal in enumerate(parsed_data.get('client_goals', []), 1):
                    print(f"  {i}. {goal}")
                
                print("\nSERVICE DETAILS:")
                for i, detail in enumerate(parsed_data.get('service_details', []), 1):
                    print(f"  Entry {i}:")
                    print(f"    Care Need: {detail.get('care_need', 'N/A')}")
                    print(f"    Goal: {detail.get('goal', 'N/A')}")
                    print(f"    Intervention: {detail.get('intervention', 'N/A')}")
                
                print("\nASSISTANCE TASKS:")
                for i, task in enumerate(parsed_data.get('assistance_tasks', []), 1):
                    print(f"  {i}. {task}")
                
                print(f"\nWHS ISSUES: {parsed_data.get('whs_issues', 'N/A')}")
                print(f"OTHER INFO: {parsed_data.get('other_info', 'N/A')}")
                
                # Test template integration
                print("\n" + "=" * 60)
                print("TEMPLATE INTEGRATION TEST")
                print("=" * 60)
                test_template_integration(parsed_data)
                
                return True, parsed_data
                
            else:
                print("ERROR: No valid JSON found in response")
                return False, None
                
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON: {e}")
            print("This might be due to the model not following the exact format.")
            return False, None
            
    except Exception as e:
        print(f"ERROR: LLM call failed: {e}")
        return False, None

def test_template_integration(parsed_data):
    """Test how the parsed data would integrate with your template"""
    
    print("Template Variable Mapping:")
    print("-" * 30)
    
    # Goals
    goals = parsed_data.get('client_goals', [])
    for i in range(3):
        goal_key = f"Goal{i+1}"
        goal_value = goals[i] if i < len(goals) else ""
        print(f"  {goal_key}: {goal_value}")
    
    # Service details
    service_details = parsed_data.get('service_details', [])
    for i in range(3):
        care_need_key = f"CareNeed{i+1}"
        intervention_key = f"Intervention{i+1}"
        
        if i < len(service_details):
            care_need_value = service_details[i].get('care_need', '')
            intervention_value = service_details[i].get('intervention', '')
        else:
            care_need_value = ""
            intervention_value = ""
            
        print(f"  {care_need_key}: {care_need_value}")
        print(f"  {intervention_key}: {intervention_value}")
    
    # Tasks
    tasks = parsed_data.get('assistance_tasks', [])
    for i in range(4):
        task_key = f"Task{i+1}"
        task_value = tasks[i] if i < len(tasks) else ""
        print(f"  {task_key}: {task_value}")
    
    # Other fields
    print(f"  WHSIssues: {parsed_data.get('whs_issues', '')}")
    print(f"  OtherInfo: {parsed_data.get('other_info', '')}")

if __name__ == "__main__":
    print("CAURA AGED CARE - LLM CARE PLAN GENERATOR TEST")
    print("=" * 60)
    
    # Test with shortened concerns data
    success, data = test_care_plan_generation()
    
    if success:
        print("\n✅ LLM Generation successful!")
        print("✅ JSON parsing successful!")
        print("✅ Template integration ready!")
    else:
        print("\n❌ LLM Generation failed!")
        print("Check the prompt format or model capabilities.")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)