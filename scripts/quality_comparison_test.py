# quality_comparison_test.py
import ollama
import json
import time
from datetime import datetime

def build_full_prompt(client_data, concerns_text=""):
    """Full prompt for quality testing"""
    
    personal = client_data.get('personal_info', {})
    services = client_data.get('service_information', {}).get('services', [])
    location = client_data.get('location', {})
    
    service_types = [s['service_type'] for s in services if s['status'] == 'active']
    client_name = f"{personal.get('given_name', 'Client')} {personal.get('family_name', '')}"
    location_context = f"in {location.get('suburb', 'the community')}"
    
    prompt = f"""You are a professional care coordinator at Caura Aged Care (cauraagedcare.com.au) creating a CHSP (Commonwealth Home Support Programme) care plan.

CLIENT INFORMATION:
- Name: {client_name}
- Services: {', '.join(service_types)}
- Location: {location_context}

CLIENT CONCERNS:
{concerns_text if concerns_text else "No specific concerns documented."}

CAURA SERVICES CONTEXT (CHSP COMPLIANT):
- Domestic Assistance (DA): House cleaning services provided fortnightly for 2 hours - general cleaning, dishwashing, clothes washing and ironing. Minor unaccompanied shopping delivered to home. Note: Does NOT include linen services, meal preparation, accompanied activities, or financial advice.
- Garden Maintenance (HM): Monthly garden maintenance for all clients focusing on safety and accessibility. Includes essential pruning, yard clearance, and lawn mowing for client safety and access. Additionally provides 2 "make safe" full property services per client including window cleaning, gutter cleaning, property hazard identification and safety repairs. All services must relate directly to client safety, accessibility and independence (not aesthetic).

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
- Ensure Domestic Assistance focuses on fortnightly 2-hour house cleaning sessions (99%) with minimal shopping (1%)
- Reference monthly garden maintenance and biannual make-safe property services
- All interventions must support independence, safety, and accessibility
- Default to safety-focused outcomes when information is limited
- Consider Work Health and Safety requirements for both client and worker

Generate the care plan content now:"""
    
    return prompt

def evaluate_quality(parsed_data, model_name):
    """Evaluate the quality of generated content"""
    
    quality_score = 0
    max_score = 100
    feedback = []
    
    # Check structure completeness (20 points)
    goals = parsed_data.get('client_goals', [])
    service_details = parsed_data.get('service_details', [])
    tasks = parsed_data.get('assistance_tasks', [])
    whs = parsed_data.get('whs_issues', '')
    other = parsed_data.get('other_info', '')
    
    structure_score = 0
    if len(goals) == 3:
        structure_score += 4
    elif len(goals) >= 2:
        structure_score += 3
    elif len(goals) >= 1:
        structure_score += 2
        
    if len(service_details) == 3:
        structure_score += 4
    elif len(service_details) >= 2:
        structure_score += 3
        
    if len(tasks) >= 4:
        structure_score += 4
    elif len(tasks) >= 3:
        structure_score += 3
    elif len(tasks) >= 2:
        structure_score += 2
        
    if whs and whs.lower() != 'none':
        structure_score += 4
        
    if other and other.lower() != 'none':
        structure_score += 4
        
    quality_score += structure_score
    feedback.append(f"Structure completeness: {structure_score}/20")
    
    # Professional language check (20 points)
    professional_score = 0
    
    # Safely convert all content to strings
    text_parts = []
    text_parts.extend(goals)
    
    # Handle service_details (list of dicts)
    for detail in service_details:
        if isinstance(detail, dict):
            text_parts.extend([str(v) for v in detail.values()])
        else:
            text_parts.append(str(detail))
    
    text_parts.extend(tasks)
    text_parts.append(str(whs))
    text_parts.append(str(other))
    
    # Filter out None/empty values and join
    text_parts = [str(part) for part in text_parts if part]
    all_text = ' '.join(text_parts)
    
    # Check for professional terms
    professional_terms = ['independence', 'safety', 'wellbeing', 'assistance', 'support', 'maintain', 'enhance']
    found_terms = sum(1 for term in professional_terms if term.lower() in all_text.lower())
    professional_score += min(found_terms * 2, 10)
    
    # Check for informal language (deduct points)
    informal_terms = ['awesome', 'cool', 'great job', 'super', 'amazing']
    found_informal = sum(1 for term in informal_terms if term.lower() in all_text.lower())
    professional_score -= found_informal * 2
    
    # Check sentence structure (basic check for complete sentences)
    if all(len(goal.strip()) > 20 for goal in goals):
        professional_score += 5
    if all(len(task.strip()) > 15 for task in tasks):
        professional_score += 5
        
    professional_score = max(0, min(professional_score, 20))
    quality_score += professional_score
    feedback.append(f"Professional language: {professional_score}/20")
    
    # Service compliance check (25 points)
    compliance_score = 0
    
    # Check for proper service references in all text content
    all_content = all_text  # Use the safely created all_text from above
    
    if 'fortnightly' in all_content.lower() or 'bi-weekly' in all_content.lower():
        compliance_score += 5
    if 'monthly' in all_content.lower():
        compliance_score += 5
    if 'make safe' in all_content.lower() or 'make-safe' in all_content.lower():
        compliance_score += 5
    if 'garden' in all_content.lower():
        compliance_score += 5
    if 'cleaning' in all_content.lower():
        compliance_score += 5
        
    quality_score += compliance_score
    feedback.append(f"Service compliance: {compliance_score}/25")
    
    # Safety focus check (20 points)
    safety_score = 0
    safety_terms = ['safety', 'safe', 'risk', 'hazard', 'secure', 'accident', 'fall', 'trip']
    found_safety = sum(1 for term in safety_terms if term.lower() in all_text.lower())
    safety_score = min(found_safety * 3, 20)
    
    quality_score += safety_score
    feedback.append(f"Safety focus: {safety_score}/20")
    
    # Specificity and realism (15 points)
    specificity_score = 0
    
    # Check for specific details in all content
    if 'hour' in all_content.lower():
        specificity_score += 5
    if any(len(str(task).strip()) > 30 for task in tasks):
        specificity_score += 5
    if whs and len(str(whs).strip()) > 20:
        specificity_score += 5
        
    quality_score += specificity_score
    feedback.append(f"Specificity: {specificity_score}/15")
    
    return quality_score, feedback

def test_model_quality(model_name, client_data, concerns_text):
    """Test quality for a specific model"""
    
    print(f"\n{'='*60}")
    print(f"QUALITY TEST: {model_name}")
    print(f"{'='*60}")
    
    try:
        prompt = build_full_prompt(client_data, concerns_text)
        
        start_time = time.time()
        
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            options={
                'temperature': 0.3,
                'top_p': 0.9,
                'max_tokens': 2000
            }
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        response_text = response['message']['content']
        
        print(f"⏱️  Processing Time: {processing_time:.2f} seconds")
        print(f"📝 Response Length: {len(response_text)} characters")
        
        # Parse JSON
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                parsed_data = json.loads(json_text)
                
                # Evaluate quality
                quality_score, feedback = evaluate_quality(parsed_data, model_name)
                
                print(f"🏆 QUALITY SCORE: {quality_score}/100")
                print(f"📊 BREAKDOWN:")
                for item in feedback:
                    print(f"   - {item}")
                
                # Show sample outputs
                print(f"\n📋 SAMPLE CONTENT:")
                goals = parsed_data.get('client_goals', [])
                if goals:
                    print(f"   Goal 1: {goals[0][:100]}...")
                
                service_details = parsed_data.get('service_details', [])
                if service_details and len(service_details) > 0:
                    detail = service_details[0]
                    intervention = detail.get('intervention', 'N/A')
                    print(f"   Intervention: {intervention[:100]}...")
                
                tasks = parsed_data.get('assistance_tasks', [])
                if tasks:
                    print(f"   Task 1: {tasks[0][:100]}...")
                
                return {
                    'model': model_name,
                    'processing_time': processing_time,
                    'quality_score': quality_score,
                    'success': True,
                    'parsed_data': parsed_data,
                    'feedback': feedback
                }
                
            else:
                print("❌ JSON PARSING FAILED: No valid JSON found")
                return {'model': model_name, 'success': False, 'error': 'No JSON found'}
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON PARSING FAILED: {e}")
            return {'model': model_name, 'success': False, 'error': f'JSON decode error: {e}'}
            
    except Exception as e:
        print(f"❌ MODEL ERROR: {e}")
        return {'model': model_name, 'success': False, 'error': str(e)}

def run_quality_comparison():
    """Run quality comparison across models"""
    
    # Test data
    sample_client = {
        "personal_info": {
            "given_name": "Mary",
            "family_name": "Thompson",
            "birth_date": "1945-03-15",
            "gender_code": "F"
        },
        "location": {
            "suburb": "Blacktown",
            "state_code": "NSW",
            "postcode": "2148"
        },
        "service_information": {
            "services": [
                {
                    "service_type": "domestic_assistance",
                    "service_code": "DA",
                    "status": "active"
                },
                {
                    "service_type": "garden_maintenance", 
                    "service_code": "HM",
                    "status": "active"
                }
            ]
        }
    }
    
    sample_concerns = "18/11/24 Mary suffers from mobility issues and uses a walking frame. 18/11/24 Mary is unable to mow her"
    
    # Test models
    models_to_test = ['llama3.2:3b', 'qwen2.5:1.5b', 'llama3.2:1b']
    
    print("CAURA AGED CARE - MODEL QUALITY COMPARISON")
    print("="*60)
    print(f"Test Client: Mary Thompson")
    print(f"Services: DA + HM")
    print(f"Concerns: Limited mobility, walking frame, lawn mowing issues")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    for model in models_to_test:
        result = test_model_quality(model, sample_client, sample_concerns)
        results.append(result)
        time.sleep(3)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("QUALITY vs SPEED SUMMARY")
    print(f"{'='*60}")
    
    print(f"{'Model':<15} {'Time (s)':<10} {'Quality':<10} {'Verdict':<15}")
    print("-" * 55)
    
    successful_results = [r for r in results if r.get('success')]
    
    for result in successful_results:
        time_str = f"{result['processing_time']:.1f}s"
        quality_str = f"{result['quality_score']}/100"
        
        # Determine verdict
        if result['quality_score'] >= 80:
            verdict = "Excellent ⭐"
        elif result['quality_score'] >= 70:
            verdict = "Good ✅"
        elif result['quality_score'] >= 60:
            verdict = "Acceptable 👍"
        else:
            verdict = "Needs work ⚠️"
            
        print(f"{result['model']:<15} {time_str:<10} {quality_str:<10} {verdict:<15}")
    
    # Recommendations
    if successful_results:
        print(f"\n🎯 RECOMMENDATIONS:")
        
        # Find best quality
        best_quality = max(successful_results, key=lambda x: x['quality_score'])
        print(f"   Highest Quality: {best_quality['model']} ({best_quality['quality_score']}/100)")
        
        # Find fastest
        fastest = min(successful_results, key=lambda x: x['processing_time'])
        print(f"   Fastest: {fastest['model']} ({fastest['processing_time']:.1f}s)")
        
        # Find best balance
        for result in successful_results:
            if result['quality_score'] >= 70 and result['processing_time'] < 10:
                print(f"   Best Balance: {result['model']} (Quality: {result['quality_score']}/100, Speed: {result['processing_time']:.1f}s)")
                break

if __name__ == "__main__":
    run_quality_comparison()