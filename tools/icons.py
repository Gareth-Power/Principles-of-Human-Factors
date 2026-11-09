# The app icon: a plain blue square with "HF" (the user's design, 2026-11-09).
# Usage: python tools/icons.py icons
import sys
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]
BLUE = (0, 113, 227)   # --accent
FONT = r"C:\Windows\Fonts\segoeuib.ttf"
def icon(size, name, rounded=False, text_scale=0.42):
    s = size * 4                                   # draw large, scale down: smooth edges
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if rounded: d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * .22), fill=BLUE)
    else: d.rectangle([0, 0, s, s], fill=BLUE)
    f = ImageFont.truetype(FONT, int(s * text_scale))
    d.text((s / 2, s / 2), "HF", font=f, fill="white", anchor="mm")
    im.resize((size, size), Image.LANCZOS).save(f"{out}/{name}")
icon(192, "icon-192.png")
icon(512, "icon-512.png")
icon(512, "icon-maskable-512.png", text_scale=0.34)   # Android crops to a circle: keep text in the middle
icon(180, "apple-touch-icon.png")                      # iOS rounds the corners itself
icon(32, "favicon-32.png", rounded=True, text_scale=0.5)
icon(256, "logo.png", rounded=True)
