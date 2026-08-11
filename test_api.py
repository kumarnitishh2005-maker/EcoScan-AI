import json, urllib.request

# Login
data = json.dumps({"username":"demo","password":"DemoPass123!"}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login/", data=data, headers={"Content-Type":"application/json"})
resp = json.loads(urllib.request.urlopen(req).read())
token = resp["access"]
headers = {"Authorization": f"Bearer {token}"}

# Test impact endpoint
r = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8000/api/users/me/impact/", headers=headers))
impact = json.loads(r.read())
print("Impact keys:", list(impact.keys()))
print("Level:", impact["level"], "LevelName:", impact["level_name"], "XP:", impact["xp"])
print("Trees:", impact["trees_equivalent"], "Water:", impact["water_saved_litres"])

# Test challenges endpoint
r2 = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8000/api/rewards/challenges/", headers=headers))
challenges = json.loads(r2.read())
print("Challenges:", len(challenges))
for c in challenges[:3]:
    print(f"  - {c['title']}: {c['current_count']}/{c['target_count']} ({c['frequency']})")

# Test leaderboard endpoint
r3 = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8000/api/rewards/leaderboard/", headers=headers))
lb = json.loads(r3.read())
print("Leaderboard:", len(lb["leaderboard"]), "users")

# Test weekly analytics
r4 = urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8000/api/analytics/weekly/", headers=headers))
weekly = json.loads(r4.read())
print("Weekly data points:", len(weekly))

# Test classify with explanation
import uuid
from PIL import Image
import io
img = Image.new("RGB", (200, 200), (34, 120, 40))
buf = io.BytesIO()
img.save(buf, format="PNG")
png = buf.getvalue()
boundary = uuid.uuid4().hex
body = (b"--" + boundary.encode() + b"\r\nContent-Disposition: form-data; name=\"image\"; filename=\"leaf.png\"\r\nContent-Type: image/png\r\n\r\n" + png + b"\r\n--" + boundary.encode() + b"--\r\n")
req5 = urllib.request.Request("http://127.0.0.1:8000/api/classify/", data=body,
    headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"})
result = json.loads(urllib.request.urlopen(req5).read())
print("Classify result keys:", list(result.keys()))
print("Category:", result["category"], "Explanation:", result.get("explanation", "")[:60])
print("XP earned:", result.get("xp_earned"), "Level up:", result.get("level_up"))
print("Equivalence:", result.get("equivalence"))
print("\nAll API tests PASSED!")
