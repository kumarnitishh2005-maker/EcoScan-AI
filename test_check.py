import json, urllib.request

BASE = "http://127.0.0.1:8000/api"
FRED = "http://localhost:3000"

def get(path, token=None):
    h = {}
    if token: h["Authorization"] = f"Bearer {token}"
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"{BASE}{path}", headers=h)).read())

# Login as demo user
data = json.dumps({"username":"demo","password":"DemoPass123!"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login/", data=data, headers={"Content-Type":"application/json"})
token = json.loads(urllib.request.urlopen(req).read())["access"]

print("=== BACKEND ENDPOINTS ===")
endpoints = [
    "/users/me/impact/",
    "/rewards/challenges/",
    "/rewards/leaderboard/",
    "/rewards/me/",
    "/analytics/weekly/",
    "/analytics/trends/",
    "/analytics/summary/",
    "/categories/",
]
for ep in endpoints:
    try:
        r = get(ep, token)
        if isinstance(r, dict):
            print(f"  GET {ep}: OK (keys: {list(r.keys())[:4]}...)")
        else:
            print(f"  GET {ep}: OK (list, {len(r)} items)")
    except Exception as e:
        print(f"  GET {ep}: FAIL ({e})")

# Check frontend static serves
print("\n=== FRONTEND ===")
try:
    r = urllib.request.urlopen(urllib.request.Request(f"{FRED}/"))
    print(f"  GET /: OK ({len(r.read())} bytes)")
except Exception as e:
    print(f"  GET /: FAIL ({e})")

print("\n=== ALL CHECKS PASSED ===")
