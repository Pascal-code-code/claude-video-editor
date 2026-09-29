"""Abschlusspruefung des fertigen Videos.

    python3 tools/check.py projekte/<name> [renders/final.mp4]

Prueft: Laenge/Format, Lautheit (Ziel -14 LUFS, True Peak <= -1), Sync oben/unten (gleiche Pose
an 4 Stellen ohne Effekt), Gesichtshelligkeit unten gegen den Rohschnitt, und schreibt einen
Kontaktbogen mit 12 Bildern nach verify/final-sheet.jpg (ANSEHEN!).
Zieht bei zu hohem True Peak den Ton mit einem Limiter nach (Bild bleibt unveraendert).
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

P = Path(sys.argv[1])
V = P / (sys.argv[2] if len(sys.argv) > 2 else "renders/final.mp4")


def run(*a):
    return subprocess.run(a, capture_output=True, text=True)


def loud(path):
    r = run("ffmpeg", "-hide_banner", "-i", str(path), "-vn", "-af", "loudnorm=I=-14:TP=-1.5:print_format=json", "-f", "null", "-")
    return json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])


def gray(path, t, vf="null", w=1080, h=1920):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1", "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w).astype(float)


dur = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(V)).stdout)
print(f"{V.name}: {dur:.2f}s")
m = loud(V)
print(f"Lautheit {m['input_i']} LUFS, True Peak {m['input_tp']} dBTP")
if float(m["input_tp"]) > -1.0:
    tmp = V.with_suffix(".tp.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(V), "-c:v", "copy", "-af", "alimiter=limit=0.85:level=false",
                    "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(tmp)], check=True)
    shutil.move(tmp, V)
    m = loud(V)
    print(f"   Limiter nachgezogen: {m['input_i']} LUFS, True Peak {m['input_tp']} dBTP")

edl = json.loads((P / "edit" / "edl.json").read_text())
cfg = json.loads((P / "config.json").read_text())
px = cfg["positionen"]["person_x"]
x0 = int(18 + px * 1044 - 150)
cut = P / "assets" / "cut.mp4"
for t in (dur * 0.35, dur * 0.62, dur * 0.97):
    f = gray(V, t)
    top, bot = f[453 + 60:453 + 360, x0:x0 + 300], f[1060 + 60:1060 + 360, x0:x0 + 300]
    c = gray(cut, t, "scale=1044:587", 1044, 587)[60:360, x0 - 18:x0 - 18 + 300]
    print(f"   {t:5.2f}s  oben/unten Abweichung {np.abs(top - bot).mean():5.1f}  |  unten/Rohschnitt Helligkeit "
          f"{(bot.mean() / max(c.mean(), 1) - 1) * 100:+.1f} %")
print("   (Abweichung unter ~5 = gleiche Pose; ueber 20 = oben laeuft gerade ein Effekt, dann Bild ansehen)")
times = [dur * (i + 0.5) / 12 for i in range(12)]
tiles = []
for i, t in enumerate(times):
    o = P / "verify" / f"s{i}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(V), "-frames:v", "1", "-vf",
                    f"scale=270:480,drawtext=text='{t:.1f}':x=6:y=6:fontsize=20:fontcolor=yellow", str(o)], check=True)
    tiles.append(o)
args = sum([["-i", str(t)] for t in tiles], [])
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex",
                "[0][1][2][3][4][5]hstack=6[a];[6][7][8][9][10][11]hstack=6[b];[a][b]vstack", str(P / "verify" / "final-sheet.jpg")], check=True)
for t in tiles:
    t.unlink()
print(f"Kontaktbogen: {P / 'verify' / 'final-sheet.jpg'}")
