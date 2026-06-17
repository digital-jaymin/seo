import json
import urllib.request
import urllib.error

# Load API key from config
try:
    with open("config/api-keys.json") as f:
        keys = json.load(f)
    api_key = keys.get("serper_key", "")
except FileNotFoundError:
    print("ERROR: config/api-keys.json not found.")
    exit(1)

if not api_key or api_key == "PASTE_SERPER_KEY_HERE":
    print("ERROR: Serper API key not set. Open config/api-keys.json and replace PASTE_SERPER_KEY_HERE with your real key.")
    exit(1)

# Build request
url = "https://google.serper.dev/search"
payload = json.dumps({
    "q": "Hp Desktop",
    "gl": "us",
    "hl": "en",
    "num": 10
}).encode("utf-8")

req = urllib.request.Request(
    url,
    data=payload,
    headers={
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    },
    method="POST"
)

# Make request
try:
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    organic = data.get("organic", [])
    first_title = organic[0]["title"] if organic else "No results found"

    print("Connection: successful")
    print(f"Organic results: {len(organic)}")
    print(f"First result:    {first_title}")

except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8") if e.fp else ""
    print(f"Connection: failed")
    print(f"HTTP error {e.code}: {e.reason}")
    if "invalid" in body.lower() or "unauthorized" in body.lower():
        print("Likely cause: API key is incorrect or not yet active.")
    else:
        print(f"Response: {body[:200]}")

except urllib.error.URLError as e:
    print("Connection: failed")
    print(f"Network error: {e.reason}")
    print("Likely cause: No internet connection or Serper is unreachable.")

except Exception as e:
    print("Connection: failed")
    print(f"Unexpected error: {e}")
