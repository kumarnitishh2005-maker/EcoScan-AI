import json, urllib.request

BASE = "http://localhost:3000/api"

# Login
data = json.dumps({"username": "demo", "password": "DemoPass123!"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login/", data=data, headers={"Content-Type": "application/json"})
token = json.loads(urllib.request.urlopen(req).read())["access"]

h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Get impact (check location field)
req = urllib.request.Request(f"{BASE}/users/me/impact/", headers=h)
impact = json.loads(urllib.request.urlopen(req).read())
print(f"Current location: '{impact['location']}'")

# Set location
data = json.dumps({"location": "12.9716,77.5946"}).encode()
req = urllib.request.Request(f"{BASE}/users/me/location/", data=data, headers=h, method="PATCH")
resp = json.loads(urllib.request.urlopen(req).read())
print(f"After set: '{resp['location']}'")

# Verify
req = urllib.request.Request(f"{BASE}/users/me/impact/", headers=h)
impact2 = json.loads(urllib.request.urlopen(req).read())
print(f"Verified: '{impact2['location']}'")

print("\nAll OK!")
