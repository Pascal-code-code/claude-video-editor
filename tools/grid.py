"""Standbilder mit 10er-Raster, um Positionen (Hand, Kopf, freie Wand) abzulesen.

    python3 tools/grid.py projekte/<name> 4.6 22.2 17.5 ...

Schreibt projekte/<name>/verify/grid.jpg. Rasterlinien liegen bei 0,1 / 0,2 / ... des Bildes,
die Werte gehen direkt als Anteile in config.json -> "positionen".
"""
import subprocess
import sys
from pathlib import Path

P = Path(sys.argv[1])
times = sys.argv[2:] or ["2", "5", "10", "15"]
tiles = []
for i, t in enumerate(times):
    out = P / "verify" / f"g{i}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", str(P / "assets" / "cut.mp4"), "-frames:v", "1", "-vf",
                    "scale=800:450,drawgrid=w=80:h=45:t=1:c=yellow@0.6,"
                    f"drawtext=text='{t}s':x=8:y=8:fontsize=26:fontcolor=red", str(out)], check=True)
    tiles.append(out)
cols = 2 if len(tiles) > 1 else 1
args = sum([["-i", str(t)] for t in tiles], [])
rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
flt, labels = [], []
for r, row in enumerate(rows):
    ins = "".join(f"[{r * cols + c}]" for c in range(len(row)))
    if len(row) < cols:
        flt.append(f"{ins}pad=iw*{cols}:ih[r{r}]" if len(row) == 1 else f"{ins}hstack={len(row)}[r{r}]")
    else:
        flt.append(f"{ins}hstack={cols}[r{r}]" if cols > 1 else f"{ins}null[r{r}]")
    labels.append(f"[r{r}]")
flt.append(f"{''.join(labels)}vstack={len(rows)}" if len(rows) > 1 else f"{labels[0]}null")
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(flt), str(P / "verify" / "grid.jpg")], check=True)
for t in tiles:
    t.unlink()
print(P / "verify" / "grid.jpg")
