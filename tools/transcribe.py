"""Sprech-Inseln finden, jede Insel mit WhisperX transkribieren und die Woerter ausrichten.

    uvx --python 3.12 --from whisperx --with numpy python tools/transcribe.py projekte/<name> [--lang de]

Liest  projekte/<name>/assets/source.*  (Original-Aufnahme)
Schreibt projekte/<name>/edit/source.wav, islands.json  (je Insel: Zeit, Text, Woerter mit Zeiten)

Warum Inseln statt ein Durchlauf: WhisperX dehnt Woerter ueber Pausen und verschluckt Fehlstarts.
Pro Insel sieht man jeden Anlauf einzeln und kann den letzten vollstaendigen waehlen.
"""
import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--lang", default="de")
ap.add_argument("--thr", type=float, default=None, help="Insel-Schwelle in dB (Standard: Rauschboden + 16)")
A = ap.parse_args()
P = Path(A.project)
E = P / "edit"
E.mkdir(parents=True, exist_ok=True)
src = next((p for p in (P / "assets").glob("source.*")), None)
if not src:
    sys.exit(f"keine Aufnahme unter {P}/assets/source.*")

wav = E / "source.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                "-af", "highpass=f=120,lowpass=f=7000", str(wav)], check=True)
w = wave.open(str(wav))
sr = w.getframerate()
a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
win = 0.02
k = int(win * sr)
m = len(a) // k
db = 20 * np.log10(np.maximum(np.sqrt((a[:m * k].reshape(m, k) ** 2).mean(axis=1)), 1e-9))
floor = float(np.percentile(db, 20))
thr = A.thr if A.thr is not None else float(np.clip(floor + 16, -64, -46))
print(f"Rauschboden {floor:.1f} dB, Sprache bis {db.max():.1f} dB, Insel-Schwelle {thr:.1f} dB")

on = db > thr
raw, i = [], 0
while i < m:
    if on[i]:
        j = i
        while j < m and on[j]:
            j += 1
        raw.append([i * win, j * win]); i = j
    else:
        i += 1
isl = []
for s, e in raw:
    if isl and s - isl[-1][1] < 0.30:
        isl[-1][1] = e
    else:
        isl.append([s, e])
isl = [x for x in isl if x[1] - x[0] > 0.25]
print(f"{len(isl)} Sprech-Inseln")

import whisperx  # noqa: E402

model = whisperx.load_model("large-v3-turbo", "cpu", compute_type="int8", language=A.lang)
am, meta = whisperx.load_align_model(language_code=A.lang, device="cpu")
out = []
for n, (s, e) in enumerate(isl):
    s2, e2 = max(0.0, s - 0.15), e + 0.30
    seg = a[int(s2 * sr):int(e2 * sr)]
    txt = " ".join(x["text"].strip() for x in model.transcribe(seg, batch_size=4, language=A.lang)["segments"]).strip()
    words = []
    if txt:
        res = whisperx.align([{"start": 0.0, "end": len(seg) / sr, "text": txt}], am, meta, seg, "cpu",
                             return_char_alignments=False)
        for sg in res["segments"]:
            for x in sg.get("words", []):
                if "start" in x:
                    words.append({"text": x["word"], "start": round(s2 + x["start"], 3), "end": round(s2 + x["end"], 3)})
    # RMS-Bloecke der Insel: zeigt Fehlstarts und Woerter, deren Zeit der Aligner falsch setzt
    i0, i1 = int(s2 / win), int(e2 / win)
    blocks, j = [], i0
    while j < i1:
        if on[j]:
            q = j
            while q < i1 and on[q]:
                q += 1
            blocks.append([round(j * win, 2), round(q * win, 2)]); j = q
        else:
            j += 1
    out.append({"i": n, "start": round(s2, 2), "end": round(e2, 2), "text": txt, "words": words, "rms_blocks": blocks})
    print(f"{n:3d} {s2:7.2f}-{e2:7.2f}  {txt}", flush=True)

(E / "islands.json").write_text(json.dumps({"threshold_db": thr, "islands": out}, ensure_ascii=False, indent=1))
print(f"-> {E / 'islands.json'}")
