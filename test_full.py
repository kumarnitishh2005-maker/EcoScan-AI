import json, urllib.request, uuid
from PIL import Image
import io

BASE = "http://127.0.0.1:8000/api"

def api_get(path, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"{BASE}{path}", headers=headers)).read())

def api_post(path, data, token=None, content_type="application/json"):
    headers = {"Content-Type": content_type}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = data.encode() if isinstance(data, str) else data
    return json.loads(urllib.request.urlopen(urllib.request.Request(f"{BASE}{path}", data=body, headers=headers)).read())

# --- 1. Register a fresh test user ---
print("=== 1. Register ===")
try:
    reg = api_post("/auth/register/", json.dumps({"username":"testcheck","email":"test@test.com","password":"TestPass123!"}))
    token = reg["tokens"]["access"]
    print(f"  Registered: {reg['user']['username']}, Level: {reg['user']['level']}, XP: {reg['user']['xp']}")
except Exception as e:
    # User might exist, just login
    login = api_post("/auth/login/", json.dumps({"username":"testcheck","password":"TestPass123!"}))
    token = login["access"]
    print(f"  Logged in: testcheck")

# --- 2. Check impact (new fields) ---
print("\n=== 2. Impact Endpoint ===")
impact = api_get("/users/me/impact/", token)
for k in ["level","level_name","xp","xp_in_current_level","xp_for_next_level","trees_equivalent","water_saved_litres","energy_saved_kwh","fuel_saved_litres","waste_diverted_kg"]:
    print(f"  {k}: {impact[k]}")

# --- 3. Classify multiple images ---
print("\n=== 3. Classify 5 images ===")
test_images = [
    ("Green organic", (34, 120, 40)),
    ("Blue plastic", (30, 100, 200)),
    ("Silver metal", (160, 160, 165)),
    ("White paper", (240, 240, 235)),
    ("Brown cardboard", (140, 100, 60)),
]

for name, rgb in test_images:
    img = Image.new("RGB", (200, 200), rgb)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png = buf.getvalue()
    boundary = uuid.uuid4().hex
    body = (b"--" + boundary.encode() + b"\r\nContent-Disposition: form-data; name=\"image\"; filename=\"test.png\"\r\nContent-Type: image/png\r\n\r\n" + png + b"\r\n--" + boundary.encode() + b"--\r\n")
    result = api_post("/classify/", body, token, f"multipart/form-data; boundary={boundary}")
    print(f"  {name} -> {result['category']} ({result['confidence']:.0%}) | +{result['xp_earned']}XP | explanation: {result['explanation'][:50]}...")
    if result.get("equivalence"):
        eq = result["equivalence"]
        print(f"    Equiv: trees={eq['trees_equivalent']}, water={eq['water_saved_litres']}L, energy={eq['energy_saved_kwh']}kWh")

# --- 4. Check impact after scans ---
print("\n=== 4. Impact after scans ===")
impact2 = api_get("/users/me/impact/", token)
print(f"  Level: {impact2['level']} ({impact2['level_name']}) | XP: {impact2['xp']} | Points: {impact2['points']}")
print(f"  Scans: {impact2['total_items_classified']} | CO2: {impact2['total_co2_saved_kg']}kg")
print(f"  Trees: {impact2['trees_equivalent']} | Water: {impact2['water_saved_litres']}L")

# --- 5. Challenges ---
print("\n=== 5. Challenges ===")
challenges = api_get("/rewards/challenges/", token)
for c in challenges:
    status = "DONE" if c["completed"] else f"{c['current_count']}/{c['target_count']}"
    print(f"  {c['title']} ({c['frequency']}): {status} | +{c['xp_reward']}XP")
    if c.get("challenges_completed"):
        print(f"    Completed: {c['challenges_completed']}")

# --- 6. Leaderboard ---
print("\n=== 6. Leaderboard ===")
lb = api_get("/rewards/leaderboard/", token)
for entry in lb["leaderboard"][:5]:
    print(f"  #{entry['rank']} {entry['username']}: {entry['xp']}XP, Lv{entry['level']} ({entry['level_name']}), {entry['total_scans']} scans")

# --- 7. Rewards ---
print("\n=== 7. Rewards/Badges ===")
rewards = api_get("/rewards/me/", token)
for r in rewards:
    print(f"  {r['badge_name']} (earned {r['earned_on'][:10]})")

# --- 8. Weekly analytics ---
print("\n=== 8. Weekly Analytics ===")
weekly = api_get("/analytics/weekly/", token)
for d in weekly:
    print(f"  {d['day']}: {d['count']} scans")

# --- 9. CO2 trends ---
print("\n=== 9. CO2 Trends ===")
trends = api_get("/analytics/trends/", token)
print(f"  Data points: {len(trends)}")
for t in trends[:3]:
    print(f"  {t['date']}: {t['scans']} scans, {t['co2_saved_kg']}kg CO2")

# --- 10. Municipal summary ---
print("\n=== 10. Municipal Summary ===")
summary = api_get("/analytics/summary/")
print(f"  Total scans: {summary['total_items_classified']}")
print(f"  Total CO2: {summary['total_co2_saved_kg']}kg")
print(f"  Active users: {summary['active_users_count']}")
print(f"  Categories: {len(summary['category_distribution'])}")

print("\n=== ALL ENDPOINTS VERIFIED ===")
