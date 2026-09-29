"""Clean Plate (leere Wand ohne Person) aus Rohschnitt + gecachten Masken von tools/matte.py.

    .venv/bin/python tools/plate.py projekte/<name> [--colfill 0.67,0.07,0.27]

Median ueber alle Bilder, in denen das Pixel nicht Person ist (Maske grosszuegig geweitet).
Was nie frei war, wird zeilenweise zwischen den Randpixeln gefuellt. cv2-Inpaint (TELEA) hat
Hautpixel in die Wand verschmiert, deshalb nicht. --colfill y0,x0,x1 (Anteile 0-1): unterhalb y0
zwischen x0 und x1 den Wert der Zeile darueber senkrecht fortsetzen, fuer Zonen, in denen fast
immer ein Arm liegt. Danach verify/cleanplate-hole.png und das Ergebnis ANSEHEN.
"""
import argparse
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--colfill", default=None)
A = ap.parse_args()
PROJ = Path(A.project)
A.src = str(PROJ / "assets" / "cut.mp4")
A.masks = str(PROJ / "edit" / "matte" / "masks")
A.out = str(PROJ / "assets" / "cleanplate.jpg")

paths = sorted(Path(A.masks).glob("*.png"))
mw, mh = Image.open(paths[0]).size
W, H = mw // 2, mh // 2
idx = [int(p.stem) for p in paths][::2]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", A.src, "-vf", f"scale={W}:{H}:flags=area",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
allf = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
kk = max(15, (W // 16) | 1)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kk, kk))
imgs, pers = [], []
for n in idx:
    if n >= len(allf):
        continue
    m = cv2.resize(np.array(Image.open(Path(A.masks) / f"{n:04d}.png")), (W, H), interpolation=cv2.INTER_AREA)
    pers.append(cv2.dilate((m > 8).astype(np.uint8), k).astype(bool))
    imgs.append(allf[n].astype(np.float32))
P = np.stack(pers)
stack = np.where(P[..., None], np.nan, np.stack(imgs))
with np.errstate(all="ignore"):
    plate = np.nan_to_num(np.nanmedian(stack, axis=0))
hole = (~P).sum(0) < 3
print(f"{len(imgs)} Bilder, Loch {hole.mean() * 100:.1f} %")
out = plate.copy()
for y in range(H):
    xs = np.where(hole[y])[0]
    if not len(xs):
        continue
    for r in np.split(xs, np.where(np.diff(xs) > 1)[0] + 1):
        a, b = r[0] - 1, r[-1] + 1
        L = plate[y, max(a - 3, 0):a + 1].mean(0) if a >= 0 else None
        R = plate[y, b:b + 3].mean(0) if b < W else None
        L = R if L is None else L
        R = L if R is None else R
        t = np.linspace(0, 1, len(r) + 2)[1:-1, None]
        out[y, r] = L * (1 - t) + R * t
if A.colfill:
    y0, x0, x1 = [float(v) for v in A.colfill.split(",")]
    Y0, X0, X1 = int(y0 * H), int(x0 * W), int(x1 * W)
    out[Y0:, X0:X1] = out[Y0 - 6:Y0 - 1, X0:X1].mean(0)[None]
    hole[Y0:, X0:X1] = True
soft = cv2.GaussianBlur(cv2.dilate(hole.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 3)[..., None]
out = out * (1 - soft) + cv2.GaussianBlur(out, (0, 0), 2) * soft
out = cv2.resize(out.clip(0, 255).astype(np.uint8), (mw, mh), interpolation=cv2.INTER_CUBIC)
Image.fromarray(out).save(A.out, quality=92)
(PROJ / "verify").mkdir(exist_ok=True)
Image.fromarray((hole * 255).astype(np.uint8)).save(PROJ / "verify" / "cleanplate-hole.png")
print(f"{A.out} geschrieben ({mw}x{mh})")
