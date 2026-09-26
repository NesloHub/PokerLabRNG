#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a clean, distributable release zip file for PokerLab RNG.
"""

import os
import shutil
import zipfile

base_dir = r"C:\Users\Neslo\.gemini\antigravity-ide\scratch\poker-rng"
desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")

zip_filename = "PokerLab_RNG_v1.0.zip"
zip_output_path = os.path.join(base_dir, zip_filename)
desktop_output_path = os.path.join(desktop_dir, zip_filename)

# Files to include in the release
files_to_pack = {
    os.path.join(base_dir, "PokerLabRNG.exe"): "PokerLab_RNG/PokerLabRNG.exe",
    os.path.join(base_dir, "icon.ico"): "PokerLab_RNG/icon.ico",
    os.path.join(base_dir, "icon.png"): "PokerLab_RNG/icon.png",
    os.path.join(base_dir, "release_files", "README.txt"): "PokerLab_RNG/README.txt",
    os.path.join(base_dir, "release_files", "Start.bat"): "PokerLab_RNG/Start.bat",
}

print("Creating release zip package:", zip_output_path)

with zipfile.ZipFile(zip_output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
    for src, arcname in files_to_pack.items():
        if os.path.exists(src):
            zipf.write(src, arcname)
            print(f"  + Added {arcname} ({os.path.getsize(src):,} bytes)")
        else:
            print(f"  ! ERROR: Could not find {src}")

# Test archive integrity
with zipfile.ZipFile(zip_output_path, "r") as zipf:
    bad_file = zipf.testzip()
    if bad_file:
        raise Exception(f"Corrupt file in zip archive: {bad_file}")
    print("Zip integrity test: 100% OK")

# Copy to Desktop
shutil.copy2(zip_output_path, desktop_output_path)
print(f"Copied to Desktop: {desktop_output_path} ({os.path.getsize(desktop_output_path):,} bytes)")
