import json, urllib.request, io, uuid
from PIL import Image

BASE='http://127.0.0.1:8000/api'
d=json.dumps({'username':'demo','password':'DemoPass123!'}).encode()
req=urllib.request.Request(BASE+'/auth/login/',data=d,headers={'Content-Type':'application/json'})
token=json.loads(urllib.request.urlopen(req).read())['access']

tests = [
    ('green_banana', (34, 139, 34)),
    ('clear_bottle', (200, 220, 230)),
    ('cardboard', (180, 150, 100)),
    ('red_coke_can', (200, 20, 20)),
    ('black_phone', (30, 30, 35)),
    ('grey_can', (160, 160, 160)),
    ('blue_plastic', (30, 80, 200)),
    ('white_paper', (240, 240, 240)),
    ('orange_peel', (210, 130, 30)),
]

for name, rgb in tests:
    img = Image.new('RGB', (300, 300), color=rgb)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    img_bytes = buf.getvalue()
    boundary = f'----FB{uuid.uuid4().hex[:16]}'
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{name}.jpg"\r\nContent-Type: image/jpeg\r\n\r\n').encode() + img_bytes + f'\r\n--{boundary}--\r\n'.encode()
    req = urllib.request.Request(BASE+'/classify/', data=body, headers={'Content-Type': f'multipart/form-data; boundary={boundary}', 'Authorization': f'Bearer {token}'})
    try:
        r = json.loads(urllib.request.urlopen(req).read())
        expected = {'green_banana':'Organic','cardboard':'Paper/Cardboard','red_coke_can':'Metal','black_phone':'E-Waste','grey_can':'Metal','white_paper':'Paper/Cardboard','orange_peel':'Organic','clear_bottle':'Glass','blue_plastic':'Recyclable Plastic'}
        exp = expected.get(name, '?')
        ok = 'OK' if r['category'] == exp else 'WRONG'
        print(f'{name:20} -> {r["category"]:25} conf={r["confidence"]} expected={exp:25} [{ok}]')
    except Exception as e:
        print(f'{name:20} -> ERROR {e}')
