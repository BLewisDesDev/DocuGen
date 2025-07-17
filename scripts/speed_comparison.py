# quick_model_test.py
import ollama
import json
import time

def quick_test(model_name):
    """Quick isolated test of a single model"""
    
    prompt = """Professional care coordinator at Caura Aged Care creating CHSP care plan.

CLIENT: Mary Thompson
SERVICES: domestic_assistance, garden_maintenance
CONCERNS: Mobility issues, uses walking frame, unable to mow lawn

Generate care plan JSON:
{
    "client_goals": ["goal1", "goal2", "goal3"],
    "assistance_tasks": ["task1", "task2", "task3", "task4"]
}"""

    print(f"Testing {model_name}...")
    
    start_time = time.time()
    
    try:
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.3, 'max_tokens': 800}
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        response_text = response['message']['content']
        
        print(f"✅ {model_name}: {processing_time:.2f} seconds")
        print(f"   Response length: {len(response_text)} chars")
        
        # Quick JSON check
        if '{' in response_text and '}' in response_text:
            print("   JSON format: ✅ Present")
        else:
            print("   JSON format: ❌ Missing")
            
        return processing_time
        
    except Exception as e:
        print(f"❌ {model_name}: Failed - {e}")
        return None

if __name__ == "__main__":
    models = ['llama3.2:3b', 'llama3.2:1b', 'qwen2.5:1.5b']
    
    results = {}
    
    for model in models:
        print(f"\n{'='*40}")
        time.sleep(2)  # Brief pause between tests
        processing_time = quick_test(model)
        if processing_time:
            results[model] = processing_time
    
    print(f"\n{'='*40}")
    print("SPEED COMPARISON:")
    for model, speed in sorted(results.items(), key=lambda x: x[1]):
        print(f"{model}: {speed:.2f}s")
    
    if results:
        fastest = min(results.items(), key=lambda x: x[1])
        print(f"\nFastest: {fastest[0]} ({fastest[1]:.2f}s)")