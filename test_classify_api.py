import json, urllib.request, base64, io, uuid
from PIL import Image

BASE = "http://127.0.0.1:8000/api"

# Create test images of different colors
colors = [
    ("red", (200, 30, 30), "Plastic"),
    ("blue", (30, 30, 200), "Plastic"),
    ("green", (30, 160, 30), "Organic"),
    ("brown", (140, 100, 50), "Organic"),
    ("grey", (128, 128, 128), "Metal"),
    ("white", (240, 240, 240), "Paper"),
]

# Login
login_data = json.dumps({'username': 'demo', 'password': 'DemoPass123!'}).encode()
req = urllib.request.Request(f'{BASE}/auth/login/', data=login_data, headers={'Content-Type': 'application/json'})
resp = json.loads(urllib.request.urlopen(req).read())
token = resp['access']
print(f"Login OK")

for name, rgb, expected in colors:
    img = Image.new('RGB', (200, 200), color=rgb)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    img_bytes = buf.getvalue()
    
    # Build multipart form data manually
    boundary = f'----WebKitFormBoundary{uuid.uuid4().hex[:16]}'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="test_{name}.jpg"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode() + img_bytes + f'\r\n--{boundary}--\r\n'.encode()
    
    req = urllib.request.Request(f'{BASE}/classify/', data=body, headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Authorization': f'Bearer {token}'
    })
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        print(f"  {name} ({rgb}) -> {result['category']} ({result['confidence']:.0%}) CO2:{result['co2_saved_kg']}kg XP:{result['xp_earned']} explain:{bool(result.get('explanation'))}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  {name}: FAIL {e.code} - {body[:200]}")
    except Exception as e:
        print(f"  {name}: ERROR {e}")

print("\nDone!")
