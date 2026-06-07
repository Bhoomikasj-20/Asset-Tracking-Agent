from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from services.gemini_service import gemini_service
import os

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Clean history
contents = []
contents.append(types.Content(
    role="user", 
    parts=[types.Part.from_text(text="[SESSION_MEMORY_SYNC]\nCURRENT_SESSION_MEMORY:\n{}")]
))
contents.append(types.Content(
    role="user", 
    parts=[types.Part.from_text(text="Create a laptop of brand Apple, model MacBook Pro 16, category Laptop")]
))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=gemini_service.config
)

print("CANDIDATES:")
for c in response.candidates:
    print(f"Role: {c.content.role}")
    for part in c.content.parts:
        print(f"  Part: text={part.text}, function_call={part.function_call}")
