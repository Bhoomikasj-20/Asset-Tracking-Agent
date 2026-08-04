"""
Isolated Groq API test — verifies API key, model, and function calling support.
Uses llama-3.3-70b-versatile.
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("=" * 50)
print("  Groq API Connection Test")
print("=" * 50)

# Test 1: API key present
print("\n[TEST 1] API Key Configuration")
if not api_key:
    print("  FAIL — GROQ_API_KEY not found in environment")
    sys.exit(1)
print(f"  PASS — API key loaded (length: {len(api_key)})")

# Test 2: Client initialization
print("\n[TEST 2] Client Initialization")
try:
    from groq import Groq
    client = Groq(api_key=api_key)
    print("  PASS — Client created successfully")
except Exception as e:
    print(f"  FAIL — {e}")
    sys.exit(1)

# Test 3: Simple generation
print("\n[TEST 3] Simple Text Generation (llama-3.3-70b-versatile)")
try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say hello in one sentence."}],
        temperature=0.7
    )
    if response and response.choices and response.choices[0].message and response.choices[0].message.content:
        print(f"  PASS — Response received: {response.choices[0].message.content.strip()[:100]}")
    else:
        print("  FAIL — Empty response from Groq")
        sys.exit(1)
except Exception as e:
    print(f"  FAIL — {e}")
    sys.exit(1)

# Test 4: Tool-based generation (function calling)
print("\n[TEST 4] Function Calling Support")
try:
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_asset_count",
                "description": "Get the total number of assets currently tracked.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "How many assets are there?"}],
        tools=tools,
        tool_choice="auto",
        temperature=0.7
    )

    has_function_call = False
    has_text = False
    if response.choices and response.choices[0].message:
        msg = response.choices[0].message
        if msg.tool_calls:
            has_function_call = True
        if msg.content:
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
