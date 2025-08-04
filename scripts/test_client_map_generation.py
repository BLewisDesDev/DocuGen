#!/usr/bin/env python3
# File: scripts/test_client_map_generation.py

import sys
import os
import json
import logging
from pathlib import Path

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.importers.json_importer import JsonImporter
from src.core.config_loader import ConfigLoader
from src.generators.care_plan_generator import CarePlanGenerator

def generate_llm_prompt(client_data: dict, service_types: list) -> str:
    """Generate LLM prompt for care plan fields."""
    
    client_name = f"{client_data.get('FirstName', '')} {client_data.get('LastName', '')}"
    location_context = f"{client_data.get('Suburb', '')}, NSW {client_data.get('PostCode', '')}"
    concerns_text = client_data.get('Concerns', '')
    
    prompt = f"""You are a professional care coordinator at Caura Aged Care (cauraagedcare.com.au) creating a CHSP (Commonwealth Home Support Programme) care plan.

CLIENT INFORMATION:
- Name: {client_name}
- Services: {', '.join(service_types)}
- Location: {location_context}
- Service History: Active services

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

def call_llm_api(prompt: str) -> dict:
    """Call LLM API to generate care plan content."""
    try:
        import requests
        
        # Using Ollama with llama3.2:3b model
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        print("Calling LLM API...")
        response = requests.post(url, json=payload, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result.get('response', '')
            
            # Parse the JSON response
            try:
                care_plan_data = json.loads(llm_response)
                print("LLM response received and parsed successfully")
                return care_plan_data
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM JSON response: {e}")
                print(f"Raw response: {llm_response}")
                return None
        else:
            print(f"LLM API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error calling LLM API: {e}")
        return None

def enhance_client_data_with_llm(client_data: dict, service_types: list) -> dict:
    """Enhance client data with LLM-generated fields."""
    
    prompt = generate_llm_prompt(client_data, service_types)
    llm_response = call_llm_api(prompt)
    
    if llm_response:
        # Map LLM response to template fields
        enhanced_data = client_data.copy()
        
        # Goals
        goals = llm_response.get('client_goals', [])
        enhanced_data['Goal1'] = goals[0] if len(goals) > 0 else ''
        enhanced_data['Goal2'] = goals[1] if len(goals) > 1 else ''
        enhanced_data['Goal3'] = goals[2] if len(goals) > 2 else ''
        
        # Service details
        service_details = llm_response.get('service_details', [])
        enhanced_data['CareNeed1'] = service_details[0]['care_need'] if len(service_details) > 0 else ''
        enhanced_data['CareNeed2'] = service_details[1]['care_need'] if len(service_details) > 1 else ''
        enhanced_data['CareNeed3'] = service_details[2]['care_need'] if len(service_details) > 2 else ''
        
        enhanced_data['Intervention1'] = service_details[0]['intervention'] if len(service_details) > 0 else ''
        enhanced_data['Intervention2'] = service_details[1]['intervention'] if len(service_details) > 1 else ''
        enhanced_data['Intervention3'] = service_details[2]['intervention'] if len(service_details) > 2 else ''
        
        # Tasks
        tasks = llm_response.get('assistance_tasks', [])
        enhanced_data['Task1'] = tasks[0] if len(tasks) > 0 else ''
        enhanced_data['Task2'] = tasks[1] if len(tasks) > 1 else ''
        enhanced_data['Task3'] = tasks[2] if len(tasks) > 2 else ''
        enhanced_data['Task4'] = tasks[3] if len(tasks) > 3 else ''
        
        # WHS and other info
        enhanced_data['WHSIssues'] = llm_response.get('whs_issues', 'None identified')
        enhanced_data['RiskMitigation'] = 'Standard safety protocols to be followed'
        enhanced_data['OtherInfo'] = llm_response.get('other_info', 'None')
        
        print(f"Enhanced client data with LLM-generated content")
        return enhanced_data
    else:
        print("Using fallback content due to LLM API failure")
        # Fallback content
        enhanced_data = client_data.copy()
        service_type = service_types[0] if service_types else 'DA'
        
        if 'DA' in service_types:
            enhanced_data.update({
                'Goal1': 'Maintain independence in home environment through regular cleaning support',
                'Goal2': 'Ensure safe and hygienic living conditions',
                'Goal3': 'Support wellbeing through reduced cleaning burden',
                'CareNeed1': 'Home cleaning assistance',
                'CareNeed2': 'Hygiene maintenance',
                'CareNeed3': 'Independence support',
                'Intervention1': 'Fortnightly 2-hour house cleaning sessions',
                'Intervention2': 'Regular dishwashing and clothes washing',
                'Intervention3': 'General cleaning and tidying',
                'Task1': 'Fortnightly house cleaning (2 hours)',
                'Task2': 'Dishwashing and kitchen cleaning',
                'Task3': 'Clothes washing and ironing',
                'Task4': 'General cleaning and tidying',
                'WHSIssues': 'Standard household cleaning risks',
                'RiskMitigation': 'Standard safety protocols to be followed',
                'OtherInfo': 'Standard domestic assistance services'
            })
        else:  # HM service
            enhanced_data.update({
                'Goal1': 'Maintain safe property access through garden maintenance',
                'Goal2': 'Ensure property safety through regular maintenance',
                'Goal3': 'Support independence through accessible outdoor areas',
                'CareNeed1': 'Garden maintenance for safety',
                'CareNeed2': 'Property access maintenance',
                'CareNeed3': 'Safety hazard management',
                'Intervention1': 'Monthly garden maintenance visits',
                'Intervention2': 'Biannual make-safe property services',
                'Intervention3': 'Essential pruning and yard clearance',
                'Task1': 'Monthly lawn mowing for safe access',
                'Task2': 'Essential pruning for safety',
                'Task3': 'Yard clearance and debris removal',
                'Task4': 'Biannual window and gutter cleaning',
                'WHSIssues': 'Outdoor work risks, ladder use, garden tools',
                'RiskMitigation': 'Standard safety protocols for outdoor work',
                'OtherInfo': 'Safety-focused garden maintenance services'
            })
        
        return enhanced_data

def main():
    """Main function to test client map generation."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        json_importer = JsonImporter()
        config_loader = ConfigLoader()
        
        # Load client data
        client_map_path = "/Users/byron/repos/DATABASE/chsp_client_mapper/output/chsp_client_map.json"
        clients = json_importer.load_data(client_map_path)
        
        # Find 1 random DA client and 1 random HM client
        da_clients = json_importer.filter_clients_by_service(clients, 'DA', limit=1, random_selection=True)
        hm_clients = json_importer.filter_clients_by_service(clients, 'HM', limit=1, random_selection=True)
        
        generated_docs = []
        
        # Process DA clients
        if da_clients:
            print(f"\n=== Processing {len(da_clients)} DA Clients ===")
            config = config_loader.load_mapper_config("client_map_da_mapper.yaml")
            app_config = config_loader.load_app_config()
            output_dir = Path("output/test_client_map")
            generator = CarePlanGenerator(output_dir, app_config)
            
            from src.core.jinja_processor import JinjaProcessor
            template_processor = JinjaProcessor()
            template_path = Path("templates") / config['template_file']
            
            for i, da_client in enumerate(da_clients, 1):
                print(f"\n--- DA Client {i} ---")
                
                # Map basic client data
                client_data = json_importer.map_client_data(da_client, config)
                service_types = ['DA']
                
                # Enhance with LLM
                enhanced_data = enhance_client_data_with_llm(client_data, service_types)
                
                print(f"Client: {enhanced_data.get('FirstName')} {enhanced_data.get('LastName')}")
                print(f"ACN: {enhanced_data.get('ACN')}")
                print(f"Service Start: {enhanced_data.get('ServiceStartDate')}")
                
                # Generate document (skip PDF to avoid permissions)
                result = generator.generate_document(template_path, enhanced_data, template_processor, generate_pdf=False)
                generated_docs.append(('DA', result.get('docx')))
                print(f"Generated: {result.get('docx')}")
        
        # Process HM clients
        if hm_clients:
            print(f"\n=== Processing {len(hm_clients)} HM Clients ===")
            config = config_loader.load_mapper_config("client_map_hm_mapper.yaml")
            app_config = config_loader.load_app_config()
            output_dir = Path("output/test_client_map")
            generator = CarePlanGenerator(output_dir, app_config)
            
            from src.core.jinja_processor import JinjaProcessor
            template_processor = JinjaProcessor()
            template_path = Path("templates") / config['template_file']
            
            for i, hm_client in enumerate(hm_clients, 1):
                print(f"\n--- HM Client {i} ---")
                
                # Map basic client data
                client_data = json_importer.map_client_data(hm_client, config)
                service_types = ['HM']
                
                # Enhance with LLM
                enhanced_data = enhance_client_data_with_llm(client_data, service_types)
                
                print(f"Client: {enhanced_data.get('FirstName')} {enhanced_data.get('LastName')}")
                print(f"ACN: {enhanced_data.get('ACN')}")
                print(f"Service Start: {enhanced_data.get('ServiceStartDate')}")
                
                # Generate document (skip PDF to avoid permissions)
                result = generator.generate_document(template_path, enhanced_data, template_processor, generate_pdf=False)
                generated_docs.append(('HM', result.get('docx')))
                print(f"Generated: {result.get('docx')}")
        
        # Summary
        print(f"\n=== Generation Complete ===")
        print(f"Generated {len(generated_docs)} documents:")
        for service_type, path in generated_docs:
            print(f"  {service_type}: {path}")
            
    except Exception as e:
        logger.error(f"Error in test generation: {e}")
        raise

if __name__ == "__main__":
    main()