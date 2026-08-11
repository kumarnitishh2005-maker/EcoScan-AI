import json, urllib.request, io, uuid
from PIL import Image
import sys
sys.path.insert(0, r'C:\Users\Nitish\OneDrive\Desktop\climate\ecoscan_backend')
from classification.ml_model import _load_image_array, _extract_features, _score_categories, _tie_break

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
    buf.seek(0)
    arr = _load_image_array(buf)
    f = _extract_features(arr)
    scores = _score_categories(f)
    scores = _tie_break(f, scores)
    best = max(scores, key=scores.get)
    print(f"\n{name} ({rgb}):")
    print(f"  brightness={f['brightness']:.2f} sat={f['saturation']:.2f} sat_var={f['sat_var']:.4f}")
    print(f"  white={f['white_ratio']:.2f} grey={f['grey_ratio']:.2f} black={f['black_ratio']:.2f}")
    print(f"  red={f['red_ratio']:.2f} orange={f['orange_ratio']:.2f} green={f['green_ratio']:.2f}")
    print(f"  blue={f['blue_ratio']:.2f} cyan={f['cyan_ratio']:.2f} purple={f['purple_ratio']:.2f}")
    print(f"  brown={f['brown_ratio']:.2f} metallic={f['metallic_score']:.2f}")
    sorted_s = sorted(scores.items(), key=lambda x: -x[1])
    for cat, sc in sorted_s:
        print(f"  {cat:25} = {sc:.3f}")
    print(f"  -> {best} ({scores[best]:.3f})")
