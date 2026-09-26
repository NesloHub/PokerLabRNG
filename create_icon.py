#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a professional, high-resolution Poker RNG icon (.ico and .png).
Multi-resolution icon: 256, 128, 64, 48, 32, 16 px.
"""

import math
from PIL import Image, ImageDraw, ImageFilter

def draw_spade(draw, cx, cy, size, fill_color):
    """Draw a mathematical smooth spade symbol at (cx, cy) of given size."""
    # Scale coordinates
    s = size / 100.0
    
    # Spade body: two lobes + pointed apex + stem
    # Apex at top (cx, cy - 45*s)
    # Right bulge: control points
    points = []
    # We can draw the spade using bezier or polygon arcs
    # Let's generate points along parametric curves
    
    # Apex
    points.append((cx, cy - 48 * s))
    
    # Right curve to right lobe
    for t in range(0, 101):
        rad = t / 100.0
        # Curve out and down to right lobe
        angle = -math.pi/2 + rad * (math.pi * 0.95)
        r = 38 * s * (1 - 0.2 * math.cos(angle))
        px = cx + r * math.cos(angle) + 12 * s * rad
        py = cy - 10 * s + r * math.sin(angle) + 18 * s * rad
        points.append((px, py))
        
    # Bottom center cusp
    points.append((cx, cy + 18 * s))
    
    # Left lobe (mirrored)
    for t in range(100, -1, -1):
        rad = t / 100.0
        angle = -math.pi/2 + rad * (math.pi * 0.95)
        r = 38 * s * (1 - 0.2 * math.cos(angle))
        px = cx - (r * math.cos(angle) + 12 * s * rad)
        py = cy - 10 * s + r * math.sin(angle) + 18 * s * rad
        points.append((px, py))

    draw.polygon(points, fill=fill_color)
    
    # Stem / base
    stem_poly = [
        (cx - 4 * s, cy + 15 * s),
        (cx + 4 * s, cy + 15 * s),
        (cx + 18 * s, cy + 42 * s),
        (cx - 18 * s, cy + 42 * s),
    ]
    draw.polygon(stem_poly, fill=fill_color)


def create_poker_icon(size=512):
    """Create a 512x512 master RGBA poker chip icon."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    r_outer = size * 0.46

    # 1. Subtle Outer Drop Shadow
    shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([cx - r_outer + 4, cy - r_outer + 8, cx + r_outer + 4, cy + r_outer + 8], fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    img.paste(shadow, (0, 0), shadow)

    # 2. Main Outer Poker Chip Body (Dark Slate with emerald rim)
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=(12, 18, 30, 255), outline=(16, 185, 129, 255), width=int(size * 0.024))

    # 3. Poker Chip Edge Dashes / Notches (8 classic casino notches)
    num_notches = 8
    notch_len = size * 0.05
    notch_width = int(size * 0.032)
    for i in range(num_notches):
        angle = (2 * math.pi / num_notches) * i
        nx1 = cx + (r_outer - notch_len) * math.cos(angle)
        ny1 = cy + (r_outer - notch_len) * math.sin(angle)
        nx2 = cx + (r_outer - 2) * math.cos(angle)
        ny2 = cy + (r_outer - 2) * math.sin(angle)
        draw.line([(nx1, ny1), (nx2, ny2)], fill=(16, 185, 129, 230), width=notch_width)

    # 4. Inner Circular Grooves
    r_mid = size * 0.35
    draw.ellipse([cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid], outline=(30, 45, 70, 255), width=int(size * 0.016))

    r_core = size * 0.30
    draw.ellipse([cx - r_core, cy - r_core, cx + r_core, cy + r_core], fill=(7, 10, 18, 255), outline=(16, 185, 129, 220), width=int(size * 0.018))

    # 5. Glowing Center Spade Emblem
    # Glow layer
    glow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    draw_spade(gdraw, cx, cy - 2, size * 0.36, (16, 185, 129, 180))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    img.paste(glow, (0, 0), glow)

    # Crisp Spade
    draw_spade(draw, cx, cy - 2, size * 0.34, (248, 250, 252, 255))

    # 6. Tiny Dice / RNG Accent Dots (Three small gold dots at bottom of inner ring)
    dot_r = size * 0.014
    for dx in [-24, 0, 24]:
        px = cx + dx * (size / 256)
        py = cy + size * 0.22
        draw.ellipse([px - dot_r, py - dot_r, px + dot_r, py + dot_r], fill=(245, 158, 11, 255))

    return img


def main():
    master = create_poker_icon(512)
    png_path = "icon.png"
    ico_path = "icon.ico"

    master.save(png_path, "PNG")
    print(f"Gemte PNG: {png_path}")

    # Generate multi-size ICO
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    master.save(ico_path, format="ICO", sizes=sizes)
    print(f"Gemte multi-resolution ICO: {ico_path}")


if __name__ == "__main__":
    main()
