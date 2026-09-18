#!/usr/bin/env python3
"""Copy the owner-supplied project images + logo into the build assets.

Sources (authoritative):  "site images/*"
    logo.png                                      -> build/assets/logo.png (resized)
    mealprep/*.png            (14 UI screenshots)  -> build/assets/screenshots/mealprep/01.png…
    ledgerlens/LedgerLens.png                      -> .../ledger-lens/01.png
    "Connex-One-Data-Bridge/Connex-One Data Bridge.png" -> .../connex-one-data-bridge/01.png
    "docket leads OCR/DocketLeads AI.png"          -> .../docket-leads-ai/01.png
    "accident claims Intelligent Automation/Accident Claims Intelligent Automator.png" -> .../accident-claims-intelligent-automator/01.png

Outputs:
    build/assets/screenshots/<slug>/01.ext, 02.ext, ...
    build/assets/logo.png
    content/screenshots.json -> {slug: [{file, caption, alt}]}

MealPrep screen captions are keyed to the capture timestamps (the same files
ship with descriptive names upstream). Alt text derives from the caption.
"""
import json
import os
import shutil

from PIL import Image

ROOT = "/home/andrew/projects/aremu-consulting"
SRC = os.path.join(ROOT, "site images")
DEST_ROOT = os.path.join(ROOT, "build", "assets", "screenshots")
LOGO_OUT = os.path.join(ROOT, "build", "assets", "logo.png")
CONTENT = os.path.join(ROOT, "content")

# slug -> list of (relative source path, caption)
SHOTS = {
    "mealprep": [
        # (capture timestamp, caption)
        ("18-08-22", "Production dashboard"),
        ("18-08-29", "Client list"),
        ("18-08-42", "Edit client details"),
        ("18-08-56", "Saved meals"),
        ("18-09-18", "Weekly planner"),
        ("18-09-28", "Planning calendar"),
        ("18-10-00", "Orders management"),
        ("18-10-09", "Meal batch counts"),
        ("18-10-17", "Meal labels"),
        ("18-11-03", "Production planning"),
        ("18-11-22", "Shareable shopping list"),
        ("18-11-46", "Ingredients list"),
        ("18-11-56", "Add ingredient"),
        ("18-12-24", "Ingredient lookup"),
    ],
    "ledger-lens": [
        ("ledgerlens/LedgerLens.png", "LedgerLens overview"),
    ],
    "connex-one-data-bridge": [
        ("Connex-One-Data-Bridge/Connex-One Data Bridge.png", "Data bridge overview"),
    ],
    "docket-leads-ai": [
        ("docket leads OCR/DocketLeads AI.png", "DocketLeads AI overview"),
    ],
    "accident-claims-intelligent-automator": [
        ("accident claims Intelligent Automation/Accident Claims Intelligent Automator.png", "Claims automator overview"),
    ],
}


def mealprep_path(timestamp):
    return f"Screenshot From 2026-07-05 {timestamp}.png"


def copy_logo():
    src = os.path.join(SRC, "logo.png")
    if not os.path.exists(src):
        print("MISSING logo.png")
        return
    os.makedirs(os.path.dirname(LOGO_OUT), exist_ok=True)
    im = Image.open(src).convert("RGBA")
    im = im.resize((160, 160), Image.LANCZOS)
    im.save(LOGO_OUT, "PNG", optimize=True)
    print(f"logo.png -> {LOGO_OUT} ({os.path.getsize(LOGO_OUT)} bytes)")


if __name__ == "__main__":
    out = {}
    missing = []
    for slug, shots in SHOTS.items():
        dest_dir = os.path.join(DEST_ROOT, slug)
        if os.path.isdir(dest_dir):
            shutil.rmtree(dest_dir)  # drop stale frames when a gallery shrinks
        os.makedirs(dest_dir, exist_ok=True)
        entries = []
        for i, entry in enumerate(shots, 1):
            if slug == "mealprep":
                src_rel = os.path.join("mealprep", mealprep_path(entry[0]))
                caption = entry[1]
            else:
                src_rel, caption = entry
            src = os.path.join(SRC, src_rel)
            if not os.path.exists(src):
                missing.append(src)
                continue
            ext = os.path.splitext(src)[1].lower() or ".png"
            fname = f"{i:02d}{ext}"
            shutil.copy2(src, os.path.join(dest_dir, fname))
            entries.append({"file": fname, "caption": caption,
                            "alt": f"{caption}"})
        out[slug] = entries
        print(f"{slug}: {len(entries)} screenshots")

    copy_logo()

    if missing:
        print("\nMISSING SOURCES:")
        for m in missing:
            print("  ", m)

    os.makedirs(CONTENT, exist_ok=True)
    with open(os.path.join(CONTENT, "screenshots.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("wrote content/screenshots.json")