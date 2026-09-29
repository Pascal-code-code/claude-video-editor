"""Rohschnitt zuruecktranskribieren: Schnitt im Wort, doppelte Saetze, Fehlstarts, Luecken, leiser Anfang.

    uvx --python 3.12 --from whisperx --with numpy python tools/verify_cut.py projekte/<name>

Vergleicht das Gehoerte mit edit/script.txt (Woerter des Schnitts laut Transkript). Abweichungen,
die nur Schreibweise sind (Claude/Cloud), sind kein Fehler. Doppelte Woerter oder fehlende Wortteile schon.
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import whisperx

P = Path(sys.argv[1])
lang = sys.argv[2] if len(sys.argv) > 2 else "de"


def words(t):
    return [w for w in re.sub(r"[^\wäöüß ]", " ", t.lower()).split() if w]


model = whisperx.load_model("large-v3-turbo", "cpu", compute_type="int8", language=lang)
want = words((P / "edit" / "script.txt").read_text())
path = P / "assets" / "cut.mp4"
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
k = 160
db = 20 * np.log10(np.maximum(np.sqrt((a[:len(a) // k * k].reshape(-1, k) ** 2).mean(1)), 1e-9))
q = db < -45
gaps, i = [], 0
while i < len(q):
    if q[i]:
        j = i
        while j < len(q) and q[j]:
            j += 1
        if (j - i) * 0.01 >= 0.2 and i > 0 and j < len(q):
            gaps.append((round(i * 0.01, 2), round((j - i) * 0.01, 2)))
        i = j
    else:
        i += 1
heard_txt = " ".join(s["text"].strip() for s in model.transcribe(a, batch_size=4, language=lang)["segments"])
heard = words(heard_txt)
sm = difflib.SequenceMatcher(a=want, b=heard, autojunk=False)
med = np.median(db[db > -45])
first = [round(float(np.mean(db[i * 50:(i + 1) * 50]) - med), 1) for i in range(8)]
print(f"{path.name}: {len(a) / 16000:.2f}s, {sm.ratio() * 100:.1f}% gleich")
print(f"Pausen >= 0,2 s (Start, Laenge): {gaps or 'keine'}")
print(f"Anfang, 0,5-s-Fenster gegen Median (dB): {first}  (unter -5 = zu leise)")
print(f"gehoert: {heard_txt}")
for op, a0, a1, b0, b1 in sm.get_opcodes():
    if op != "equal":
        print(f"   {op:7} Transkript {' '.join(want[a0:a1])!r:35} gehoert {' '.join(heard[b0:b1])!r}")
