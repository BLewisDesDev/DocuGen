# test_ollama.py
import ollama

def test_ollama_connection():
    try:
        # Simple question
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {
                    'role': 'user', 
                    'content': 'Hello! Please respond with a greeting of your choice if you can hear me.'
                }
            ]
        )
        print("Response:", response['message']['content'])
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_ollama_connection()