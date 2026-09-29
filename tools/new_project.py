"""Legt ein neues Projekt aus einer Aufnahme in input/ an.

    python3 tools/new_project.py input/meine-aufnahme.mov [name]

Erzeugt projekte/<name>/ mit:
  assets/source.<ext>   Link auf die Aufnahme (nichts wird kopiert oder veraendert)
  assets/               Effekt-Bibliothek, gsap, Logo, Sounds
  edit/index.tpl        Vorlage (Split: oben Effekte, unten ORIGINAL), pro Projekt anpassbar
  config.json           Texte, Effekt-Woerter, Positionen (Standard = Skript-Vorlage)
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) < 2:
    sys.exit(__doc__)
src = Path(sys.argv[1]).resolve()
if not src.exists():
    sys.exit(f"nicht gefunden: {src}")
name = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"[^a-z0-9]+", "-", src.stem.lower()).strip("-")
P = ROOT / "projekte" / name
if P.exists():
    sys.exit(f"{P} gibt es schon. Anderen Namen angeben oder den Ordner loeschen.")
(P / "assets" / "sfx").mkdir(parents=True)
(P / "edit").mkdir()
(P / "verify").mkdir()
(P / "assets" / f"source{src.suffix.lower()}").symlink_to(src)
fx = ROOT / "template" / "fx"
if not (fx / "gsap.min.js").exists():
    sys.exit("template/fx/gsap.min.js fehlt: zuerst das Setup laufen lassen (bash setup/setup.sh)")
for f in ("gsap.min.js", "pascal-fx.js", "pascal-fx.css", "claude.svg"):
    shutil.copy2(fx / f, P / "assets" / f)
for f in (fx / "sfx").glob("*.wav") if (fx / "sfx").exists() else []:
    shutil.copy2(f, P / "assets" / "sfx" / f.name)
shutil.copy2(ROOT / "template" / "split" / "index.tpl", P / "edit" / "index.tpl")
shutil.copy2(ROOT / "template" / "split" / "config.json", P / "config.json")
(P / "hyperframes.json").write_text(json.dumps({
    "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
    "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}}, indent=2))
(P / "meta.json").write_text(json.dumps({"id": "claude-video", "name": name, "width": 1080, "height": 1920, "fps": 30}, indent=2))
print(f"Projekt angelegt: {P.relative_to(ROOT)}")
print(f"Naechster Schritt: uvx --python 3.12 --from whisperx --with numpy python tools/transcribe.py {P.relative_to(ROOT)}")
