from dotenv import load_dotenv
load_dotenv()

import asyncio
import sys
from services.gemini_service import gemini_service

sys.stdout.reconfigure(encoding='utf-8')

session = {
    'history': [{
        'role': 'user', 
        'parts': [{'text': 'Create a laptop of brand Apple, model MacBook Pro 16, category Laptop'}]
    }], 
    'metadata': {}
}

async def run():
    print("Sending message...")
    async for chunk in gemini_service.generate_response_sse(session):
        print(f"CHUNK: {chunk}")

asyncio.run(run())
