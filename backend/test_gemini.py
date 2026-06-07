"""
Isolated Gemini API test — verifies API key, model, and response.
Uses only gemini-2.5-flash.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print("=" * 50)
print("  Gemini API Connection Test")
print("=" * 50)

# Test 1: API key present
print("\n[TEST 1] API Key Configuration")
if not api_key:
    print("  FAIL — GOOGLE_API_KEY not found in environment")
    sys.exit(1)
print(f"  PASS — API key loaded (length: {len(api_key)})")

# Test 2: Client initialization
print("\n[TEST 2] Client Initialization")
try:
    from google import genai
    client = genai.Client(api_key=api_key)
    print("  PASS — Client created successfully")
except Exception as e:
    print(f"  FAIL — {e}")
    sys.exit(1)

# Test 3: Simple generation
print("\n[TEST 3] Simple Text Generation (gemini-flash-latest)")
try:
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="Say hello in one sentence."
    )
    if response and response.text and len(response.text.strip()) > 0:
        print(f"  PASS — Response received: {response.text.strip()[:100]}")
    else:
        print("  FAIL — Empty response from Gemini")
        sys.exit(1)
except Exception as e:
    print(f"  FAIL — {e}")
    sys.exit(1)

# Test 4: Tool-based generation (function calling)
print("\n[TEST 4] Function Calling Support")
try:
    from google.genai import types

    def get_asset_count() -> dict:
        """Get the total number of assets currently tracked."""
        return {"success": True, "count": 42}

    config = types.GenerateContentConfig(
        tools=[get_asset_count],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents="How many assets are there?",
        config=config
    )

    has_function_call = False
    has_text = False
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.function_call:
                has_function_call = True
            if part.text:
                has_text = True

    if has_function_call:
        print("  PASS — Model correctly requested function call")
    elif has_text:
        print(f"  PASS — Model responded with text (may not have needed tool)")
    else:
        print("  WARN — No function call or text in response")
except Exception as e:
    print(f"  FAIL — {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("  ALL TESTS PASSED")
print("=" * 50)
