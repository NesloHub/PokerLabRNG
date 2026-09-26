#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw

source_jpg = r"C:\Users\Neslo\.gemini\antigravity-ide\brain\f662214f-0c24-41d9-8c41-f0583701fbc8\poker_rng_icon_1790241633513.jpg"
out_dir = r"C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng"

img = Image.open(source_jpg).convert("RGBA")
width, height = img.size

# Create a smooth circular mask so the icon floats cleanly without square corners
mask = Image.new('L', (width, height), 0)
draw = ImageDraw.Draw(mask)
# The chip diameter is roughly 88% of image
margin = int(width * 0.06)
draw.ellipse([margin, margin, width - margin, height - margin], fill=255)

# Apply mask
chip_rgba = Image.new("RGBA", (width, height), (0, 0, 0, 0))
chip_rgba.paste(img, (0, 0), mask)

# Save high-res PNG
png_path = os.path.join(out_dir, "icon.png")
chip_rgba.save(png_path, "PNG")
print("Saved PNG to", png_path)

# Generate multi-size ICO
ico_path = os.path.join(out_dir, "icon.ico")
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
chip_rgba.save(ico_path, format="ICO", sizes=sizes)
print("Saved multi-resolution ICO to", ico_path)
