"""Freisteller (person.webm, VP9 mit Alpha) aus einem Rohschnitt, fuer jedes Format.

Laeuft mit der .venv aus dem Setup, im Repo-Ordner:
    .venv/bin/python -u tools/matte.py projekte/<name> \
        --ranges 7-16.2,19-23.2 [--size 1280x720 | 720x1280] [--model u2net_human_seg]

Masken nur in --ranges (sonst transparent), plus jedes 6. Bild fuer die Clean Plate (tools/plate.py).
Masken werden in edit/matte/masks/ gecacht, ein Neustart rechnet nur fehlende Bilder.
u2net_human_seg: ~1,3 s/Bild auf der CPU. birefnet-portrait ist sauberer, aber ~50 s/Bild.
"""
import argparse
import subprocess
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--ranges", required=True, help="z. B. 7-16.2,19-23.2 (Sekunden im Schnitt)")
ap.add_argument("--size", default=None, help="BxH der Maske, Standard: 1280 auf der langen Seite")
ap.add_argument("--model", default="u2net_human_seg")
ARGS = ap.parse_args()
PROJ = Path(ARGS.project)
SRC = PROJ / "assets" / "cut.mp4"
ARGS.out = PROJ / "assets" / "person.webm"
MASKS = PROJ / "edit" / "matte" / "masks"; MASKS.mkdir(parents=True, exist_ok=True)
_p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                     "stream=width,height,r_frame_rate,nb_read_packets", "-of", "csv=p=0", str(SRC)],
                    capture_output=True, text=True, check=True).stdout.strip().split(",")
SW, SH, _fr, N = int(_p[0]), int(_p[1]), _p[2], int(_p[3])
FPS = round(eval(_fr))
if ARGS.size:
    W, H = map(int, ARGS.size.split("x"))
else:
    k = 1280 / max(SW, SH); W, H = round(SW * k / 2) * 2, round(SH * k / 2) * 2
RANGES = [tuple(map(float, r.split("-"))) for r in ARGS.ranges.split(",")]
MODEL = ARGS.model


def needed(n):
    t = n / FPS
    return any(a <= t < b for a, b in RANGES)


def frames():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(SRC), "-vf", f"scale={W}:{H}:flags=area",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = 0
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        yield n, np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        n += 1
    p.wait()


def main():
    session = new_session(MODEL)
    todo = [n for n in range(N) if (needed(n) or n % 6 == 0) and not (MASKS / f"{n:04d}.png").exists()]
    print(f"{MODEL}: {len(todo)} Masken zu rechnen", flush=True)
    t0 = time.time(); done = 0
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
                            "-auto-alt-ref", "0", "-b:v", "0", "-crf", "30", "-row-mt", "1",
                            "-metadata:s:v:0", "alpha_mode=1", str(ARGS.out)],
                           stdin=subprocess.PIPE)
    empty = np.zeros((H, W, 4), np.uint8).tobytes()
    for n, img in frames():
        mp = MASKS / f"{n:04d}.png"
        m = None
        if needed(n) or n % 6 == 0:
            if not mp.exists():
                m = np.array(remove(Image.fromarray(img), session=session, only_mask=True))
                Image.fromarray(m).save(mp)
                done += 1
                if done % 20 == 0:
                    el = time.time() - t0
                    print(f"  {done}/{len(todo)}  {el / done:.2f} s/Bild, Rest {el / done * (len(todo) - done) / 60:.1f} min", flush=True)
            else:
                m = np.array(Image.open(mp))
        if needed(n):
            a = cv2.GaussianBlur(m, (3, 3), 0)
            enc.stdin.write(np.dstack([img, a]).tobytes())
        else:
            enc.stdin.write(empty)
    enc.stdin.close(); enc.wait()
    print(f"{ARGS.out} geschrieben: {N} Bilder, {W}x{H}, {FPS} fps ({time.time() - t0:.0f} s)", flush=True)

if __name__ == "__main__":
    main()
