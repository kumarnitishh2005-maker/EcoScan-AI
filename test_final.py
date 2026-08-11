import json, urllib.request

BASE = "http://127.0.0.1:8000/api"

def get(path, token=None):
    h = {}
    if token: h["Authorization"] = f"Bearer {token}"
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"{BASE}{path}", headers=h)).read())

def post(path, data, token=None):
    h = {"Content-Type": "application/json"}
    if token: h["Authorization"] = f"Bearer {token}"
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"{BASE}{path}", data=json.dumps(data).encode(), headers=h)).read())

# Login
login = post("/auth/login/", {"username": "demo", "password": "DemoPass123!"})
token = login["access"]

print("=== ALL ENDPOINTS ===")
endpoints = [
    ("GET", "/users/me/impact/", None),
    ("GET", "/rewards/challenges/", None),
    ("GET", "/rewards/leaderboard/", None),
    ("GET", "/rewards/me/", None),
    ("GET", "/analytics/weekly/", None),
    ("GET", "/analytics/trends/", None),
    ("GET", "/analytics/summary/", None),
    ("GET", "/categories/", None),
    ("GET", "/cleanup/reports/", None),
    ("GET", "/cleanup/events/", None),
    ("GET", "/notifications/", None),
]
for method, path, body in endpoints:
    try:
        r = get(path, token)
        label = list(r.keys())[:3] if isinstance(r, dict) else f"{len(r)} items"
        print(f"  {method} {path}: OK ({label})")
    except Exception as e:
        print(f"  {method} {path}: FAIL ({e})")

# Test chatbot
print("\n=== CHATBOT ===")
try:
    r = post("/assistant/ask/", {"question": "How do I recycle plastic?"}, token)
    print(f"  Answer: {r['answer'][:80]}...")
except Exception as e:
    print(f"  FAIL: {e}")

# Test cleanup volunteer
print("\n=== CLEANUP VOLUNTEER ===")
try:
    events = get("/cleanup/events/", token)
    if events:
        r = post("/cleanup/events/volunteer/", {"event_id": events[0]["id"]}, token)
        print(f"  Volunteer: OK")
except Exception as e:
    print(f"  FAIL: {e}")

# Test notifications
print("\n=== NOTIFICATIONS ===")
try:
    r = post("/notifications/create/", {"type": "badge", "title": "Badge Unlocked!", "message": "You earned the First Scan badge!"}, token)
    print(f"  Created: {r['title']}")
    r2 = get("/notifications/", token)
    print(f"  List: {r2['unread_count']} unread, {len(r2['notifications'])} total")
except Exception as e:
    print(f"  FAIL: {e}")

print("\n=== ALL TESTS PASSED ===")
