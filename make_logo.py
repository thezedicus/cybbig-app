from PIL import Image, ImageDraw
import math, os

size = 512
img = Image.new("RGBA", (size, size), (6, 14, 25, 255))
d = ImageDraw.Draw(img)

cx = size // 2

# Rocket (top)
d.polygon([(cx, 40), (cx-28, 110), (cx+28, 110)], fill=(53, 214, 240))
d.rectangle([cx-28, 110, cx+28, 170], fill=(14, 165, 196))
d.polygon([(cx-28, 140), (cx-52, 180), (cx-28, 170)], fill=(37, 99, 235))
d.polygon([(cx+28, 140), (cx+52, 180), (cx+28, 170)], fill=(37, 99, 235))
d.ellipse([cx-10, 70, cx+10, 90], fill=(231, 238, 249))
d.polygon([(cx-16, 170), (cx, 205), (cx+16, 170)], fill=(251, 146, 60))

# Electron atom (middle)
nucleus_y = 260

def ellipse_points(cx, cy, a, b, rot_deg, n=72):
    pts = []
    for i in range(n):
        t = 2*math.pi*i/n
        x = a*math.cos(t)
        y = b*math.sin(t)
        r = math.radians(rot_deg)
        xr = x*math.cos(r) - y*math.sin(r)
        yr = x*math.sin(r) + y*math.cos(r)
        pts.append((cx+xr, cy+yr))
    return pts

for rot in (0, 60, 120):
    pts = ellipse_points(cx, nucleus_y, 110, 38, rot)
    d.line(pts + [pts[0]], fill=(53, 214, 240), width=3)

for rot, phase in ((0, 0.2), (60, 0.7), (120, 0.4)):
    pts = ellipse_points(cx, nucleus_y, 110, 38, rot)
    idx = int(len(pts)*phase)
    ex, ey = pts[idx]
    d.ellipse([ex-7, ey-7, ex+7, ey+7], fill=(52, 211, 153))

d.ellipse([cx-18, nucleus_y-18, cx+18, nucleus_y+18], fill=(53, 214, 240))
d.ellipse([cx-8, nucleus_y-8, cx+8, nucleus_y+8], fill=(231, 238, 249))

# Robot (bottom)
ry = 360
d.rounded_rectangle([cx-42, ry, cx+42, ry+52], radius=10, fill=(16, 31, 51), outline=(53, 214, 240), width=2)
d.ellipse([cx-26, ry+16, cx-10, ry+32], fill=(53, 214, 240))
d.ellipse([cx+10, ry+16, cx+26, ry+32], fill=(53, 214, 240))
d.rectangle([cx-12, ry+38, cx+12, ry+44], fill=(52, 211, 153))
d.rounded_rectangle([cx-34, ry+58, cx+34, ry+118], radius=8, fill=(12, 25, 41), outline=(53, 214, 240), width=2)
d.rectangle([cx-58, ry+68, cx-34, ry+78], fill=(53, 214, 240))
d.rectangle([cx+34, ry+68, cx+58, ry+78], fill=(53, 214, 240))
d.rectangle([cx-22, ry+118, cx-8, ry+145], fill=(53, 214, 240))
d.rectangle([cx+8, ry+118, cx+22, ry+145], fill=(53, 214, 240))

os.makedirs("desktop", exist_ok=True)
img.save(os.path.join("desktop", "icon.png"))
print("saved")