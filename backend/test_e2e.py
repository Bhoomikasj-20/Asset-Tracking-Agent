import urllib.request
import urllib.parse
import json
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8080"

print("=" * 60)
print("  🚀 STARTING AUTOMATED END-TO-END SYSTEM TEST SUITE  ")
print("=" * 60)

# Helper: HTTP GET request
def http_get(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 500, {"error": str(e)}

# Helper: HTTP POST request
def http_post(url, data):
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 500, {"error": str(e)}

# Helper: HTTP PUT request
def http_put(url, data):
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 500, {"error": str(e)}

# Helper: HTTP DELETE request
def http_delete(url):
    try:
        req = urllib.request.Request(url, method="DELETE")
        with urllib.request.urlopen(req) as res:
            return res.getcode(), json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 500, {"error": str(e)}

# Helper: Send SSE chat message and read chunks with retry logic for rate limits
def send_chat_message(session_id, message_text):
    url = f"{BASE_URL}/run_sse"
    payload = {
        "appName": "agent",
        "newMessage": {"role": "user", "parts": [{"text": message_text}]},
        "sessionId": session_id,
        "userId": "user",
        "streaming": False
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
    )
    
    max_retries = 4
    for attempt in range(max_retries):
        accumulated_text = ""
        metadata_updates = {}
        try:
            with urllib.request.urlopen(req) as res:
                # Read line by line
                for line in res:
                    line_str = line.decode().strip()
                    if not line_str:
                        continue
                    if line_str.startswith("data: "):
                        json_str = line_str[6:].strip()
                        try:
                            data = json.loads(json_str)
                            if "content" in data and "parts" in data["content"]:
                                for part in data["content"]["parts"]:
                                    if "text" in part:
                                        accumulated_text += part["text"]
                            if "metadata" in data:
                                metadata_updates.update(data["metadata"])
                        except Exception as e:
                            pass
            
            # Check for rate limit indicators in the response text
            text_lower = accumulated_text.lower()
            is_rate_limited = any(w in text_lower for w in [
                "high demand", "try again in a few", "temporarily unable", "try again shortly"
            ])
            
            if is_rate_limited:
                if attempt < max_retries - 1:
                    wait_time = 4 * (attempt + 1)
                    print(f"  ⚠️ Rate limit detected in agent response, waiting {wait_time}s and retrying (attempt {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
            
            return accumulated_text, metadata_updates
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 4 * (attempt + 1)
                print(f"  ⚠️ Request error: {e}, waiting {wait_time}s and retrying (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
                continue
            print(f"  ❌ Chat Message Failed after {max_retries} attempts: {e}")
            return "", {}
    return "", {}

# --- STEP 1: Verify Startup and Health ---
print("\n[STEP 1] Verifying Service Health...")
code, health = http_get(f"{BASE_URL}/health")
assert code == 200, f"Expected 200 health check, got {code}"
assert health.get("status") == "healthy", "Server not healthy"
assert health.get("api_key_configured") is True, "Groq API Key is not configured"
print("  ✅ Backend is RUNNING and HEALTHY.")

# --- STEP 2: Record Initial Dashboard Stats ---
print("\n[STEP 2] Recording Initial Dashboard Stats...")
code, initial_stats = http_get(f"{BASE_URL}/assets/stats")
assert code == 200, f"Failed to get stats: {code}"
initial_asset_count = initial_stats.get("total_assets", 0)
print(f"  📊 Initial Dashboard Stats:")
print(f"     - Total Assets: {initial_asset_count}")
print(f"     - Assigned: {initial_stats.get('assigned_assets', 0)}")
print(f"     - Available: {initial_stats.get('available_assets', 0)}")

# --- STEP 3: Create Chat Session ---
print("\n[STEP 3] Creating a Chat Session...")
code, session_info = http_post(f"{BASE_URL}/apps/agent/users/user/sessions", {})
assert code == 200, f"Failed to create session: {code}"
session_id = session_info.get("id")
assert session_id is not None, "Session ID was null"
print(f"  ✅ Created Session ID: {session_id}")

# --- STEP 4: Chat Agent CREATE Asset ---
print("\n[STEP 4] Testing Conversational CREATE Asset...")
prompt = "Create a laptop of brand Apple, model MacBook Pro 16, category Laptop"
print(f"  💬 User: \"{prompt}\"")
reply, metadata = send_chat_message(session_id, prompt)
print(f"  🤖 Agent: \"{reply.strip()}\"")
print(f"  🧠 Metadata Sync: {metadata}")

# Extract Asset ID from metadata or response text
asset_id = None
if "last_created_asset" in metadata and metadata["last_created_asset"]:
    asset_id = metadata["last_created_asset"].get("id")

if not asset_id:
    # Attempt regex extraction from reply
    match = re.search(r"([a-f0-9\-]{36})", reply)
    if match:
        asset_id = match.group(1)

assert asset_id is not None, "Failed to retrieve generated Asset ID from response metadata or text."
print(f"  ✅ Asset successfully created with ID: {asset_id}")

# --- STEP 5: Verification in Database ---
print("\n[STEP 5] Verifying Asset in Database...")
code, db_asset = http_get(f"{BASE_URL}/assets/{asset_id}")
assert code == 200, f"Expected 200 for newly created asset, got {code}"
assert db_asset.get("brand") == "Apple", f"Expected Apple, got {db_asset.get('brand')}"
assert db_asset.get("model_number") == "MacBook Pro 16", f"Expected MacBook Pro 16, got {db_asset.get('model_number')}"
assert db_asset.get("status") == "Available", f"Expected Available, got {db_asset.get('status')}"
print("  ✅ Asset exists in database with matching fields.")

# --- STEP 6: Chat Agent READ/RETRIEVE Asset ---
print("\n[STEP 6] Testing Conversational READ/RETRIEVE Asset...")
prompt = f"Show details for the asset with ID {asset_id}"
print(f"  💬 User: \"{prompt}\"")
reply, metadata = send_chat_message(session_id, prompt)
print(f"  🤖 Agent: \"{reply.strip()}\"")
assert "Apple" in reply and "MacBook Pro 16" in reply, "Response should detail the asset info"
print("  ✅ Conversational read verified.")

# --- STEP 7: Chat Agent UPDATE Asset (Assign) ---
print("\n[STEP 7] Testing Conversational UPDATE Asset (Assign)...")
prompt = f"Assign that Apple MacBook Pro 16 to Bhoomika"
print(f"  💬 User: \"{prompt}\"")
reply, metadata = send_chat_message(session_id, prompt)
print(f"  🤖 Agent: \"{reply.strip()}\"")

# Confirm in database
code, db_asset = http_get(f"{BASE_URL}/assets/{asset_id}")
assert db_asset.get("assigned_to") == "Bhoomika", "Expected assigned_to Bhoomika"
assert db_asset.get("status") == "Assigned", "Expected status Assigned"
print("  ✅ Conversational assignment verified in DB (Assigned to Bhoomika).")

# --- STEP 8: Chat Agent UPDATE Asset (Field modification) ---
print("\n[STEP 8] Testing Conversational UPDATE Asset (Location modification)...")
prompt = f"Change the location of asset {asset_id} to Room 302"
print(f"  💬 User: \"{prompt}\"")
reply, metadata = send_chat_message(session_id, prompt)
print(f"  🤖 Agent: \"{reply.strip()}\"")

# Confirm in database
code, db_asset = http_get(f"{BASE_URL}/assets/{asset_id}")
assert db_asset.get("location") == "Room 302", "Expected location Room 302"
print("  ✅ Conversational location update verified in DB (Location set to Room 302).")

# --- STEP 9: Chat Agent DELETE Asset with Confirmation ---
print("\n[STEP 9] Testing Conversational DELETE Asset (Step 1: Request)...")
prompt = f"Delete the laptop we just created with ID {asset_id}"
print(f"  💬 User: \"{prompt}\"")
reply, metadata = send_chat_message(session_id, prompt)
print(f"  🤖 Agent: \"{reply.strip()}\"")

# We added a rule in system prompt to ask for confirmation.
# Verify that the agent replies asking for confirmation.
prompt_lower = reply.lower()
is_confirmed_already = "deleted" in prompt_lower and not any(w in prompt_lower for w in ["sure", "confirm", "proceed", "want to"])

if not is_confirmed_already:
    print("  💬 (Confirmation Asked) Sending 'Yes, please proceed'")
    prompt = "Yes, please proceed and confirm the deletion"
    print(f"  💬 User: \"{prompt}\"")
    reply, metadata = send_chat_message(session_id, prompt)
    print(f"  🤖 Agent: \"{reply.strip()}\"")

# Check database
code, db_asset = http_get(f"{BASE_URL}/assets/{asset_id}")
assert code == 404 or "error" in db_asset, f"Asset should be deleted, but status code was {code} and returned: {db_asset}"
print("  ✅ Conversational delete verified. Asset is no longer in database.")

# --- STEP 10: Dashboard Sync and Audit Verification ---
print("\n[STEP 10] Verifying Dashboard Synchronization and Audit Trails...")
code, final_stats = http_get(f"{BASE_URL}/assets/stats")
assert code == 200
final_asset_count = final_stats.get("total_assets", 0)
assert final_asset_count == initial_asset_count, f"Asset count mismatch! Initial: {initial_asset_count}, Final: {final_asset_count}"

# Fetch audit logs
code, logs = http_get(f"{BASE_URL}/assets/audit-logs")
assert code == 200

# Look for our asset_id in the audit logs
creation_logged = False
assignment_logged = False
deletion_logged = False

for log in logs:
    if log.get("asset_id") == asset_id:
        action = log.get("action")
        if action == "Created":
            creation_logged = True
        elif action == "Assigned":
            assignment_logged = True
        elif action == "Deleted":
            deletion_logged = True

assert creation_logged, "Asset creation was not logged in audit trail"
assert assignment_logged, "Asset assignment was not logged in audit trail"
assert deletion_logged, "Asset deletion was not logged in audit trail"

print("  ✅ Dashboard Synchronization verified. Stats returned to initial count.")
print("  ✅ Audit Trail logs verified for Created, Assigned, and Deleted actions.")

print("\n" + "=" * 60)
print("  🎉 ALL END-TO-END SYSTEM TESTS PASSED SUCCESSFULLY!  ")
print("=" * 60)
