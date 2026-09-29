"""Schreibt projekte/<name>/index.html aus config.json + cut.words.json + edit/index.tpl.

    python3 tools/gen.py projekte/<name>

Jeder Effekt haengt an einem gesprochenen Wort (config.json -> "woerter"). Die Woerter werden der
Reihe nach gesucht: jedes nach dem vorherigen, Gross/Klein und Satzzeichen egal. Findet gen.py ein
Wort nicht, bricht es ab und nennt die Stelle; dann das Wort in config.json an das Transkript anpassen.
Am Ende stehen die Zeitfenster, fuer die tools/matte.py den Freisteller rechnen muss.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit(__doc__)
PROJ = Path(sys.argv[1]).resolve()
ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((PROJ / "config.json").read_text())
data = json.loads((PROJ / "cut.words.json").read_text())
edl = json.loads((PROJ / "edit" / "edl.json").read_text())
N_FRAMES = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                               "stream=nb_read_packets", "-of", "csv=p=0", str(PROJ / "assets" / "cut.mp4")],
                              capture_output=True, text=True, check=True).stdout.strip())
DUR = N_FRAMES / 30
ERS = CFG.get("untertitel", {}).get("ersetzen", {})
words = [dict(w, show=ERS.get(w["text"], w["text"])) for w in data["words"]]


def norm(t):
    return re.sub(r"[^\wäöüß\-]", "", t.lower())


def find(token, after):
    want = norm(token)
    for w in words:
        if w["start"] > after + 1e-3 and want in (norm(w["text"]), norm(w["show"])):
            return w
    ctx = " ".join(x["text"] for x in words if x["start"] > after)[:120]
    sys.exit(f"gen.py: Wort {token!r} nach {after:.2f}s nicht gefunden. Danach kommt: {ctx!r}")


# --- Trailer (erster Satz) ---
tr = CFG["trailer"]
cursor = -1.0
parts = []
for p in tr["teile"]:
    k = find(p["klein_bei"], cursor)
    g = find(p["gross_bei"], k["start"] - 1e-3)
    parts.append({"klein": p["klein"], "gross": p["gross"], "bg": p["bg"], "kAt": k["start"], "gAt": g["start"],
                  "start": max(0.0, k["start"] - 0.03) if parts else 0.0})
    cursor = g["start"]

# --- Effekt-Woerter in fester Reihenfolge ---
ORDER = ["zoom", "logo", "d3", "nice", "kamera", "okay", "zerlege", "ebenen", "hgrund", "mich", "text", "blend",
         "aus", "zurueck", "rahmen", "links", "headline", "reel", "vollbild", "reels", "oh", "komm", "edit",
         "kostenlose", "karte", "kreis"]
W = CFG["woerter"]
T = {}
for key in ORDER:
    w = find(W[key], cursor)
    T[key] = w["start"]
    cursor = w["start"]
trailer_end = round(T["zoom"] - 0.02, 3)
T_list = [round(T["reel"] + 0.29 + 0.3 * i, 3) for i in range(len(CFG["texte"]["liste"]))]

# Headline der Rahmen-Slide: ab "headline" so viele Woerter wie angegeben
i0 = next(i for i, w in enumerate(words) if abs(w["start"] - T["headline"]) < 1e-6)
HEAD = [{"t": w["show"].rstrip(","), "s": w["start"], "k": norm(w["text"]) == norm(W["reel"])}
        for w in words[i0:i0 + int(CFG.get("headline_woerter", 6))]]

# --- Untertitel ---
KEYS = {norm(k) for k in CFG.get("untertitel", {}).get("akzent", [])}
HIDE = [(0.0, trailer_end), (T["rahmen"] - 0.07, T["vollbild"] + 0.07)]
groups, cur = [], []
for i, w in enumerate(words):
    if any(a <= w["start"] < b for a, b in HIDE):
        if cur:
            groups.append(cur); cur = []
        continue
    cur.append(w)
    nxt = words[i + 1] if i + 1 < len(words) else None
    if (len(cur) >= 3 or re.search(r"[.,!?]$", w["text"]) or nxt is None or nxt["start"] - w["end"] > 0.3
            or len("".join(x["show"] for x in cur)) > 16):
        groups.append(cur); cur = []
if cur:
    groups.append(cur)
caps = []
for k, g in enumerate(groups):
    start = g[0]["start"] - 0.04
    nxt = groups[k + 1][0]["start"] - 0.04 if k + 1 < len(groups) else DUR
    end = min(nxt, g[-1]["end"] + 0.6)
    for a, b in HIDE:
        if start < a < end:
            end = a
    caps.append({"start": round(start, 3), "end": round(end, 3),
                 "words": [{"t": x["show"], "s": x["start"], "k": norm(x["text"]) in KEYS} for x in g]})

# --- Reel-Cover: eigene Bilder in assets/reels/, sonst Standbilder aus dem eigenen Video ---
rdir = PROJ / "assets" / "reels"
rdir.mkdir(exist_ok=True)
imgs = sorted(p for p in rdir.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
if not imgs:
    px = CFG["positionen"]["person_x"]
    for n in range(6):
        t = DUR * (0.12 + 0.13 * n)
        out = rdir / f"reel-{n + 1}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(PROJ / "assets" / "cut.mp4"),
                        "-frames:v", "1", "-vf",
                        f"crop=ih*9/16:ih:max(0\\,min(iw-ih*9/16\\,iw*{px}-ih*9/32)):0,scale=540:960", str(out)], check=True)
    imgs = sorted(rdir.glob("reel-*.jpg"))
    print(f"   Reel-Cover aus dem eigenen Video erzeugt ({len(imgs)}). Eigene Cover: Bilder nach {rdir} legen.")
REELS = [f"assets/reels/{p.name}" for p in imgs]

# --- Sounds (fehlende Dateien werden uebersprungen) ---
LAND = T["oh"] - 0.04
cues = [("riser", 0.0, 0.28, 2.58), ("impact", parts[-1]["gAt"] - 0.07, 0.30, 1.4), ("whoosh-2", T["zoom"], 0.18, 1.33),
        ("pop", T["logo"], 0.30, 0.3), ("whoosh-1", T["kamera"] - 0.26, 0.22, 1.2), ("glass-crack", T["kamera"], 0.42, 2.2),
        ("whoosh-2", T["ebenen"] - 0.07, 0.22, 1.33), ("pop", T["hgrund"], 0.24, 0.3), ("pop", T["mich"], 0.24, 0.3),
        ("pop", T["text"], 0.24, 0.3), ("click", T["aus"] - 0.05, 0.7, 0.05), ("click", T["zurueck"] - 0.08, 0.7, 0.05),
        ("whoosh-1", T["zurueck"] + 0.07, 0.18, 1.2), ("whoosh-2", T["rahmen"], 0.22, 1.33)]
cues += [("pop", t, 0.2, 0.3) for t in T_list]
cues += [("whoosh-1", T["vollbild"], 0.2, 1.2), ("whoosh-2", T["reels"] - 0.11, 0.2, 1.33), ("impact", LAND - 0.03, 0.34, 0.7),
         ("pop", T["edit"] - 0.05, 0.3, 0.3), ("pop", T["karte"], 0.24, 0.3)]
tags, n = [], 0
for name, at, vol, d in cues:
    if not (PROJ / "assets" / "sfx" / f"{name}.wav").exists():
        continue
    tags.append(f'<audio id="sfx{n:02d}" src="assets/sfx/{name}.wav" data-start="{max(0, at):.3f}" data-duration="{d}" '
                f'data-track-index="{10 + n}" data-volume="{vol}"></audio>')
    n += 1

# --- HTML ---
tpl = (PROJ / "edit" / "index.tpl").read_text()
svg = (PROJ / "assets" / "claude.svg").read_text()
star = re.search(r'<path d="([^"]+)"', svg).group(1)
D = {"T": T, "pos": CFG["positionen"], "txt": CFG["texte"], "caps": caps, "head": HEAD, "list_at": T_list,
     "reels": REELS, "dur": DUR, "trailer": {"parts": parts, "end": trailer_end}}
out = tpl.replace("__DUR__", f"{DUR:.3f}").replace("__DATA__", json.dumps(D, ensure_ascii=False))
out = out.replace("__STAR__", star).replace("__SFX__", "\n  ".join(tags))
for k, v in CFG["texte"].items():
    if isinstance(v, str):
        out = out.replace(f"__TXT_{k}__", html.escape(v))
left = re.findall(r"__TXT_\w+__", out)
if left:
    sys.exit(f"gen.py: in config.json fehlen Texte fuer {sorted(set(left))}")
(PROJ / "index.html").write_text(out)
orig = PROJ / "assets" / "cut-orig.mp4"
if orig.exists():
    orig.unlink()
orig.hardlink_to(PROJ / "assets" / "cut.mp4")

m1 = (max(0.0, T["ebenen"] - 0.6), T["zurueck"] + 0.9)
m2 = (max(0.0, T["reels"] - 0.6), T["komm"] + 0.1)
print(f"index.html: {DUR:.2f}s, {len(caps)} Untertitel-Gruppen, {len(tags)} Sounds")
print("Effekt-Zeiten:", ", ".join(f"{k} {v:.2f}" for k, v in T.items()))
print(f"Freisteller-Zeitfenster (--ranges): {m1[0]:.1f}-{m1[1]:.1f},{m2[0]:.1f}-{m2[1]:.1f}")
