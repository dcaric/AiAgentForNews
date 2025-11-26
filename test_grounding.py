import os
import google.generativeai as genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not set.")
    exit(1)

genai.configure(api_key=api_key)

def test_grounding():
    print("Testing Gemini with Google Search Grounding...")
    try:
        # specific syntax check: tools argument
        # Trying the string alias first as implemented
        model = genai.GenerativeModel('gemini-2.5-flash', tools='google_search')
        
        prompt = """
        Find the next HOME game for HNK Hajduk Split at Poljud. 
        Return the Date, Time, and Opponent.
        """
        print(f"Prompt: {prompt.strip()}")
        
        response = model.generate_content(prompt)
        print("\nResponse:")
        print(response.text)
        
        # Check if grounding metadata is present (if accessible)
        if response.candidates and response.candidates[0].grounding_metadata:
             print("\nGrounding Metadata found.")
        else:
             print("\nNo Grounding Metadata found.")

    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_grounding()
