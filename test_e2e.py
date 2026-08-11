import json, urllib.request, uuid, io
from PIL import Image

BASE = "http://localhost:3000/api"

def api(method, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# 1. REGISTER
print("=== REGISTER ===")
uname = f"testuser_{uuid.uuid4().hex[:6]}"
code, data = api("POST", "/auth/register/", {
    "username": uname, "email": f"{uname}@test.com", "password": "TestPass123!"
})
print(f"  Status: {code}")
if code == 201:
    token = data["tokens"]["access"]
    print(f"  Token: {token[:30]}...")
    print(f"  User: {data['user']['username']}")
else:
    print(f"  Error: {data}")
    exit(1)

# 2. LOGIN (fresh user)
print("\n=== LOGIN ===")
code, data = api("POST", "/auth/login/", {"username": uname, "password": "TestPass123!"})
print(f"  Status: {code}")
if code == 200:
    token = data["access"]
    print(f"  Token OK")
else:
    print(f"  Error: {data}")
    exit(1)

# 3. CLASSIFY
print("\n=== CLASSIFY ===")
img = Image.new('RGB', (200, 200), color=(200, 30, 30))
buf = io.BytesIO()
img.save(buf, format='JPEG')
img_bytes = buf.getvalue()

boundary = f'----FormBoundary{uuid.uuid4().hex[:16]}'
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="image"; filename="test.jpg"\r\n'
    f'Content-Type: image/jpeg\r\n\r\n'
).encode() + img_bytes + f'\r\n--{boundary}--\r\n'.encode()

req = urllib.request.Request(f"{BASE}/classify/", data=body, headers={
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Authorization': f'Bearer {token}'
})
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f"  Status: {resp.status}")
    print(f"  Category: {result['category']}")
    print(f"  Confidence: {result['confidence']:.0%}")
    print(f"  CO2 saved: {result['co2_saved_kg']}kg")
    print(f"  XP earned: {result['xp_earned']}")
    print(f"  Explanation: {bool(result.get('explanation'))}")
    print(f"  Equivalence: {bool(result.get('equivalence'))}")
except urllib.error.HTTPError as e:
    print(f"  Status: {e.code}")
    print(f"  Error: {e.read().decode()[:300]}")

# 4. USER IMPACT
print("\n=== USER IMPACT ===")
code, data = api("GET", "/users/me/impact/", token=token)
print(f"  Status: {code}")
if code == 200:
    print(f"  Username: {data['username']}")
    print(f"  Points: {data['points']}")
    print(f"  Level: {data['level_name']}")

print("\n=== ALL PASSED ===")
