"""Vẽ icon pixel 32x32 (phóng 32 lần = 1024 px) cho launcher: hoàng hôn, sông, xuồng, nón lá, cá lóc."""
from pathlib import Path
from PIL import Image, ImageDraw

N = 32
im = Image.new("RGBA", (N, N))
d = ImageDraw.Draw(im)
for y in range(14):  # trời hoàng hôn
    t = y / 13
    d.line([(0, y), (N, y)], fill=(int(255 - 60 * t), int(170 + 40 * t), int(90 + 110 * t)))
d.ellipse([20, 4, 27, 11], fill=(255, 226, 120))  # mặt trời
for y in range(14, N):  # sông phù sa
    t = (y - 14) / 18
    d.line([(0, y), (N, y)], fill=(int(70 - 30 * t), int(120 - 50 * t), int(110 - 40 * t)))
for x in range(0, N, 6):
    d.point([(x + 2, 17), (x + 5, 22), (x + 1, 27)], fill=(150, 200, 190))
d.polygon([(6, 16), (25, 16), (22, 19), (9, 19)], fill=(150, 82, 40))  # xuồng ba lá
d.line([(6, 16), (25, 16)], fill=(205, 130, 70))
d.rectangle([14, 11, 17, 15], fill=(50, 110, 160))  # người, áo bà ba
d.polygon([(10, 11), (21, 11), (15.5, 6)], fill=(236, 210, 130))  # nón lá
d.line([(10, 11), (21, 11)], fill=(180, 150, 80))
d.line([(24, 9), (24, 16)], fill=(110, 70, 40))  # cây bẹo
d.rectangle([22, 9, 23, 10], fill=(220, 70, 50)); d.rectangle([25, 10, 26, 11], fill=(250, 190, 60))
d.ellipse([8, 24, 16, 27], fill=(70, 80, 60)); d.polygon([(16, 25), (19, 23), (19, 28)], fill=(70, 80, 60))  # cá lóc
d.point((10, 25), fill=(240, 240, 220))
for x, y in [(2, 21), (27, 25)]:  # lục bình
    d.rectangle([x, y, x + 2, y + 1], fill=(60, 140, 70)); d.point((x + 1, y - 1), fill=(190, 140, 220))
out = Path(__file__).with_name("choinoi.png")
im.resize((1024, 1024), Image.NEAREST).save(out)
print(out)
