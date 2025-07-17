# raw_output_test.py
import ollama
import time

def test_model_raw_output(model_name):
    """Test model and show raw output"""
    
    prompt = """Professional creating documentation for home support services.

CLIENT: Mary Thompson
LOCATION: Blacktown, NSW
SERVICES: domestic assistance, garden maintenance
CONCERNS: Mobility issues, uses walking frame, unable to mow lawn

CAURA SERVICE INFORMATION:
- Domestic Assistance: House cleaning services provided fortnightly for 2 hours. Includes general cleaning, dishwashing, clothes washing and ironing. Occasional unaccompanied shopping delivered to home.
- Garden Maintenance: Monthly garden maintenance focusing on safety and accessibility. Essential pruning, yard clearance, and lawn mowing for client safety and access. Also provides make-safe property services including window cleaning, gutter cleaning, property hazard identification and safety repairs.

All services focus on safety, accessibility and independence. Must relate directly to client safety and independence, not aesthetic improvements.

Generate professional care plan with JSON structure:
{
    "client_goals": [
        "Goal 1 focusing on independence and safety",
        "Goal 2 focusing on service outcomes", 
        "Goal 3 focusing on quality of life"
    ],
    "service_details": [
        {
            "care_need": "Care need 1",
            "goal": "Goal 1", 
            "intervention": "Specific intervention 1"
        },
        {
            "care_need": "Care need 2",
            "goal": "Goal 2",
            "intervention": "Specific intervention 2"
        },
        {
            "care_need": "Care need 3",
            "goal": "Goal 3",
            "intervention": "Specific intervention 3"
        }
    ],
    "assistance_tasks": [
        "Specific task 1",
        "Specific task 2", 
        "Specific task 3",
        "Specific task 4"
    ],
    "whs_issues": "Safety considerations and workplace health factors",
    "other_info": "Additional relevant information"
}

We provide Domestic Cleaning and Gardening Services. NO OTHER CHSP SERVICES. 
Focus the plans on cleaning and gardening do not talk about other services just Cleaning and Gardening.

Use professional language. Focus on safety, independence, and realistic service delivery."""

    print(f"\n{'='*80}")
    print(f"MODEL: {model_name.upper()}")
    print(f"{'='*80}")
    
    try:
        start_time = time.time()
        
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.3, 'max_tokens': 800}
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        response_text = response['message']['content']
        
        print(f"⏱️ TIME: {processing_time:.2f} seconds")
        print(f"📝 LENGTH: {len(response_text)} characters")
        print(f"\n📄 RAW OUTPUT:")
        print("-" * 80)
        print(response_text)
        print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    models = ['llama3.2:3b', 'llama3.2:1b', 'qwen2.5:1.5b']
    
    print("RAW OUTPUT COMPARISON - CAURA AGED CARE")
    print("="*80)
    
    for model in models:
        success = test_model_raw_output(model)
        if not success:
            print(f"Failed to test {model}")
        
        # Brief pause between models
        time.sleep(2)
    
    print(f"\n{'='*80}")
    print("COMPARISON COMPLETE")
    print("="*80)
    print("Review the raw outputs above to compare:")
    print("- Content quality and detail")
    print("- Professional language")
    print("- JSON structure compliance")
    print("- Service-specific accuracy")