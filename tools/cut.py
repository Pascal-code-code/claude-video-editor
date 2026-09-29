"""Rohschnitt aus der Aufnahme: bester Anlauf je Satz, Versprecher und Pausen raus, Tempo nach Wunsch.

    python3 tools/cut.py projekte/<name> [--edl]

Liest  projekte/<name>/assets/source.*, edit/islands.json (tools/transcribe.py), edit/spans.json
Schreibt assets/cut.mp4 (Basis fuer alle Effekte), cut.words.json (Woerter in Reel-Zeit),
         edit/edl.json, edit/script.txt und ../../output/rohschnitt.mp4

edit/spans.json (legt Claude nach dem Transkript an):
{
  "speed": 1.1,                      # 1.0 = Originaltempo
  "spans": [                         # Reihenfolge = Reihenfolge im Video
    {"label": "intro", "start": 3.41, "end": 6.82, "note": "#0 einziger Take"},
    {"label": "nice",  "start": 58.59, "end": 59.24, "hardin": 58.72, "hardout": 59.30}
  ],                                 # start = Beginn erstes Wort, end = Ende letztes Wort (islands.json)
  "drops": [[72.86, 73.12]],         # Pausen, die trotzdem stehen bleiben (siehe Skill)
  "intro_boost_db": 0                # Anfang lauter, falls der erste Satz leise ist
}
Kern (extend_edges, tighten, drop_gaps) aus Pascals abgenommener Reel-Pipeline.
"""
from __future__ import annotations

import array, json, math, re, shutil, subprocess, sys, wave
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit(__doc__)
PROJ = Path(sys.argv[1]).resolve()
EDIT = PROJ / "edit"
ROOT = Path(__file__).resolve().parents[1]
SRC = next((p for p in (PROJ / "assets").glob("source.*")), None)
if not SRC:
    sys.exit(f"keine Aufnahme unter {PROJ}/assets/source.*")
CFG = json.loads((EDIT / "spans.json").read_text())
FPS = 30
SPEED = float(CFG.get("speed", 1.1))
PAD_IN = 0.030
PAD_OUT = 0.080
FADE = 0.006
TARGET = -14.0
SPANS = {s["label"]: (s["start"], s["end"]) for s in CFG["spans"]}
ORDER = [s["label"] for s in CFG["spans"]]
if len(SPANS) != len(ORDER):
    sys.exit("spans.json: jedes label nur einmal")
NOEXT: set[str] = {s["label"] for s in CFG["spans"] if s.get("noext")}
HARDIN: dict[str, float] = {s["label"]: s["hardin"] for s in CFG["spans"] if s.get("hardin") is not None}
HARDOUT: dict[str, float] = {s["label"]: s["hardout"] for s in CFG["spans"] if s.get("hardout") is not None}
DROPS: list[tuple[float, float]] = [tuple(d) for d in CFG.get("drops", [])]
INTRO_BOOST = float(CFG.get("intro_boost_db", 0))

SIL = 0.002
SIL_SOFT = 0.0007   # weiche An-/Auslaute liegen unter SIL, aber ueber dem iPhone-Gate
MIN_SIL = 0.15
HOP = 0.01
_RMS: dict[str, list[float]] = {}


def probe() -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,pix_fmt,color_transfer:stream_side_data=rotation", "-of", "json", str(SRC)],
                       capture_output=True, text=True, check=True)
    s = json.loads(r.stdout)["streams"][0]
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    w, h = s["width"], s["height"]
    if abs(rot) in (90, 270):
        w, h = h, w
    return {"w": w, "h": h, "pix": s.get("pix_fmt", ""), "trc": s.get("color_transfer", "")}


def video_chain() -> str:
    p = probe()
    long_side = max(p["w"], p["h"])
    k = min(1.0, 2880 / long_side)                     # 4K -> 2880 (Platz fuer Push-ins), sonst Original
    W, H = round(p["w"] * k / 2) * 2, round(p["h"] * k / 2) * 2
    if p["trc"] in ("arib-std-b67", "smpte2084"):      # iPhone-HDR: ohne Tonemap brennt das Gesicht aus
        tm = ("zscale=t=linear:npl=400,format=gbrpf32le,zscale=p=bt709,"
              "tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,")
        print("   HDR erkannt, rechne auf SDR um")
        return f"{tm}scale={W}:{H}:flags=lanczos,format=yuv420p"
    rng = "in_range=full:out_range=tv:" if p["pix"].startswith("yuvj") else ""
    return f"scale={W}:{H}:{rng}flags=lanczos,format=yuv420p"


def rms10() -> list[float]:
    if "x" not in _RMS:
        vals: list[float] = []
        with wave.open(str(EDIT / "source.wav"), "rb") as wf:
            sr = wf.getframerate()
            samples = array.array("h")
            samples.frombytes(wf.readframes(wf.getnframes()))
        hop, win = int(sr * HOP), int(sr * 0.02)
        for i in range(0, len(samples) - win, hop):
            chunk = samples[i : i + win]
            vals.append(math.sqrt(sum(x * x for x in chunk) / win) / 32768.0)
        _RMS["x"] = vals
    return _RMS["x"]


def load_words() -> list[dict]:
    data = json.loads((EDIT / "islands.json").read_text())
    out = [{"text": w["text"], "start": w["start"], "end": w["end"]} for isl in data["islands"] for w in isl["words"]]
    out.sort(key=lambda w: w["start"])
    return out


def kept_words(all_words: list[dict], spans: list[str]) -> list[list[dict]]:
    blocks = []
    for label in spans:
        a, b = SPANS[label]
        ws = [dict(w, span=label) for w in all_words if a - 0.02 <= w["start"] < b]
        if not ws:
            raise SystemExit(f"{label}: keine Woerter in {a}-{b}")
        blocks.append(ws)
    return blocks


def extend_edges(a: float, b: float) -> tuple[float, float]:
    rms = rms10()
    i = int(a / HOP)
    back = 0
    while i - 1 >= 0 and rms[i - 1] >= SIL and back < 12:
        i -= 1
        back += 1
    a2 = max(0.0, i * HOP - 0.02) if back else a
    j0 = j = int(b / HOP)
    last = j0
    quiet = 0
    while j < len(rms) and j - j0 < 60:
        if rms[j] >= SIL:
            last = j + 1
            quiet = 0
        else:
            quiet += 1
            if quiet > 8:
                break
        j += 1
    b2 = max(b, last * HOP + 0.03) if last > j0 else b
    return a2, b2


def tighten(cuts: list[dict]) -> list[dict]:
    """Stillen >= MIN_SIL innerhalb eines Cuts raus, nie mitten in einem Wort."""
    rms = rms10()
    out = []
    for c in cuts:
        a, b = c["inFrame"] / FPS, c["outFrame"] / FPS
        pieces: list[list[float]] = []
        start = last = None
        quiet = 0
        for i in range(int(a / HOP), min(len(rms), int(b / HOP))):
            t = i * HOP
            if rms[i] >= SIL:
                if start is None:
                    start = t
                last = t + HOP
                quiet = 0
            elif start is not None:
                quiet += 1
                if quiet * HOP >= MIN_SIL:
                    pieces.append([start, last])
                    start = None
                    quiet = 0
        if start is not None:
            pieces.append([start, last])
        if not pieces:
            continue
        for piece in pieces:
            for w in c["words"]:
                if w["end"] - w["start"] < 0.05:
                    continue
                if w["start"] < piece[0] < w["end"]:
                    i = int(piece[0] / HOP)
                    while i - 1 >= 0 and (i - 1) * HOP >= w["start"] - 0.03 and rms[i - 1] >= SIL_SOFT:
                        i -= 1
                    piece[0] = max(a, min(piece[0], i * HOP - 0.02))
                if w["start"] < piece[1] < w["end"]:
                    j = int(piece[1] / HOP)
                    last = j
                    while j < len(rms) and j * HOP <= w["end"] + 0.03:
                        if rms[j] < SIL_SOFT:
                            break
                        last = j + 1
                        j += 1
                    piece[1] = min(b, max(piece[1], last * HOP + 0.02))
        merged: list[list[float]] = []
        for piece in pieces:
            if merged and any(w["start"] < merged[-1][1] - 0.03 and w["end"] > piece[0] + 0.03
                              and w["end"] - w["start"] > 0.05 for w in c["words"]):
                merged[-1][1] = piece[1]
            else:
                merged.append(list(piece))
        bounds = [[max(a, p0 - PAD_IN), min(b, p1 + 0.06)] for p0, p1 in merged]
        words_in: list[list[dict]] = [[] for _ in bounds]
        for w in c["words"]:
            mid = (w["start"] + min(w["end"], w["start"] + 0.3)) / 2
            k = min(range(len(bounds)), key=lambda j: 0 if bounds[j][0] <= mid <= bounds[j][1]
                    else min(abs(mid - bounds[j][0]), abs(mid - bounds[j][1])))
            words_in[k].append(w)
        for (p0, p1), ws in zip(bounds, words_in):
            if not ws:
                print(f"   ! {c['label']}: Stueck {p0:.2f}-{p1:.2f} ohne Wort verworfen")
                continue
            in_f, out_f = int(round(p0 * FPS)), int(round(p1 * FPS))
            if out and out[-1]["label"] == c["label"] and in_f <= out[-1]["outFrame"] + 1:
                out[-1]["outFrame"] = max(out[-1]["outFrame"], out_f)
                out[-1]["words"].extend(ws)
                continue
            if out_f > in_f + 1:
                out.append({"label": c["label"], "inFrame": in_f, "outFrame": out_f, "words": ws})
    return [c for c in out if c["outFrame"] > c["inFrame"] + 1]


def drop_gaps(cuts: list[dict]) -> list[dict]:
    """Feste Pausen rausschneiden, die tighten() nicht findet (gedehnte Wortzeiten)."""
    out = []
    for c in cuts:
        a, b = c["inFrame"] / FPS, c["outFrame"] / FPS
        inner = [d for d in DROPS if a < d[0] and d[1] < b]
        if not inner:
            out.append(c)
            continue
        pos = a
        for d0, d1 in sorted(inner):
            out.append({"label": c["label"], "inFrame": int(round(pos * FPS)),
                        "outFrame": int(round(d0 * FPS)),
                        "words": [w for w in c["words"] if pos - 0.02 <= w["start"] < d0]})
            pos = d1
        out.append({"label": c["label"], "inFrame": int(round(pos * FPS)),
                    "outFrame": c["outFrame"],
                    "words": [w for w in c["words"] if w["start"] >= pos - 0.06]})
    return [c for c in out if c["outFrame"] > c["inFrame"] + 1]


def group_segments(blocks: list[list[dict]], all_words: list[dict]) -> list[dict]:
    cuts = []
    for bi, g in enumerate(blocks):
        label = g[0]["span"]
        hard_a, hard_b = SPANS[label]
        a = max(0.0, g[0]["start"] - (0.040 if bi == 0 else PAD_IN))
        b = hard_b + PAD_OUT
        a2, b = extend_edges(a, b)
        a = max(a2, hard_a - 0.12) if label not in NOEXT else max(a, hard_a - 0.01)
        if label in HARDIN:
            a = HARDIN[label]
        last = g[-1]
        nxt = next((w["start"] for w in all_words if w["start"] > last["start"] + 1e-3), None)
        if nxt is not None:
            b = min(b, max(nxt - 0.02, last["start"] + 0.05))
        b = min(b, hard_b + 0.20)
        b = HARDOUT.get(label, b)
        cuts.append({"label": label, "inFrame": int(round(a * FPS)),
                     "outFrame": max(int(round(a * FPS)) + 2, int(round(b * FPS))), "words": g})
    cuts = tighten(cuts)
    cuts = drop_gaps(cuts)
    return restack(cuts)


def restack(cuts: list[dict]) -> list[dict]:
    pos = 0
    for c in cuts:
        c["sourceStart"] = c["inFrame"] / FPS
        c["sourceEnd"] = c["outFrame"] / FPS
        c["timelineStart"] = pos / FPS
        pos += c["outFrame"] - c["inFrame"]
        c["timelineEnd"] = pos / FPS
    return cuts



def write_filter(cuts: list[dict], path: Path) -> None:
    lines = []
    n = len(cuts)
    grade = video_chain()
    for i, c in enumerate(cuts):
        a, b = c["sourceStart"], c["sourceEnd"]
        fade_out = max(0.0, (b - a) - FADE)
        lines.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,fps=30[v{i}]")
        lines.append(f"[0:a:0]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:st=0:d={FADE},afade=t=out:st={fade_out}:d={FADE}[a{i}]")
    vcat = "".join(f"[v{i}]" for i in range(n))
    acat = "".join(f"[a{i}]" for i in range(n))
    intro_end = cuts[0]["timelineEnd"] / SPEED
    boost = f"volume={INTRO_BOOST}dB:enable='between(t,0,{intro_end:.3f})'," if INTRO_BOOST else ""
    lines.append(f"{vcat}concat=n={n}:v=1:a=0,setpts=PTS/{SPEED},fps=30,{grade}[v]")
    lines.append(f"{acat}concat=n={n}:v=0:a=1,atempo={SPEED},dynaudnorm=f=200:g=15:p=0.9:m=8:b=1,{boost}"
                 f"highpass=f=100,acompressor=threshold=-26dB:ratio=2.5:attack=8:release=160:makeup=2,"
                 f"afade=t=in:st=0:d=0.06,aresample=48000[a]")
    path.write_text(";\n".join(lines) + "\n")


ENC = ["-map_metadata", "-1", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", "30",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
       "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]


def loudness(path: Path) -> dict:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vn", "-af",
                        f"loudnorm=I={TARGET}:TP=-1.5:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    return json.loads(re.findall(r"\{[^{}]*\}", p.stderr)[-1])


def main() -> None:
    all_words = load_words()
    cuts = group_segments(kept_words(all_words, ORDER), all_words)
    dur = math.floor(cuts[-1]["timelineEnd"] / SPEED * FPS) / FPS
    print(f"{len(cuts)} Stuecke, {dur:.2f}s fertig")
    for c in cuts:
        print(f"   {c['label']:10} {c['sourceStart']:7.2f}-{c['sourceEnd']:7.2f}  Reel {c['timelineStart'] / SPEED:6.2f} | "
              f"{' '.join(w['text'] for w in c['words'])}")
    words = []
    for c in cuts:
        off = c["timelineStart"] - c["sourceStart"]
        for w in c["words"]:
            s = max(c["sourceStart"], w["start"]); e = min(c["sourceEnd"], w["end"])
            words.append({"text": w["text"], "start": round((s + off) / SPEED, 3), "end": round((e + off) / SPEED, 3)})
    edl = [{k: x for k, x in c.items() if k != "words"} | {"quote": " ".join(w["text"] for w in c["words"])} for c in cuts]
    (EDIT / "edl.json").write_text(json.dumps({"duration": dur, "speed": SPEED, "cuts": edl}, ensure_ascii=False, indent=1))
    (PROJ / "cut.words.json").write_text(json.dumps({"duration": dur, "words": words}, ensure_ascii=False, indent=1))
    (EDIT / "script.txt").write_text(" ".join(w["text"] for w in words) + "\n")
    # Restpausen innerhalb der Stuecke (RMS unter -50 dB, >= 0,2 s): Kandidaten fuer "drops" in spans.json
    rms = rms10()
    sugg = []
    for c in cuts:
        s0, s1 = c["sourceStart"], c["sourceEnd"]
        i, j0 = int(s0 / HOP), int(s1 / HOP)
        while i < j0:
            if rms[i] < 0.00316:
                j = i
                while j < j0 and rms[j] < 0.00316:
                    j += 1
                if (j - i) * HOP >= 0.2 and i > int(s0 / HOP) and j < j0:
                    sugg.append([round(i * HOP + 0.07, 2), round(j * HOP - 0.07, 2)])
                i = j
            else:
                i += 1
    if sugg:
        print(f"   Restpausen >= 0,2 s (als drops eintragen, falls Pausen raus sollen): {sugg}")
    if "--edl" in sys.argv:
        return
    filt = EDIT / "cut.filter"
    write_filter(cuts, filt)
    raw = EDIT / "cut-raw.mp4"
    print("   rendere ...", flush=True)
    with (EDIT / "cut.log").open("w") as log:
        subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", str(SRC),
                        "-filter_complex_script", str(filt), "-map", "[v]", "-map", "[a]", *ENC, str(raw)],
                       check=True, stdout=log, stderr=subprocess.STDOUT)
    m = loudness(raw)
    gain = TARGET - float(m["input_i"])
    out = PROJ / "assets" / "cut.mp4"
    tmp = EDIT / "cut-norm.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", str(raw),
                    "-af", f"volume={gain:.2f}dB,alimiter=limit=0.85:level=false", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", "-t", f"{dur:.6f}",
                    "-movflags", "+faststart", str(tmp)], check=True)
    # Rotations-Flag sicher entfernen (sonst dreht der Player das fertige Bild ein zweites Mal)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-display_rotation", "0", "-i", str(tmp), "-c", "copy", str(out)], check=True)
    tmp.unlink()
    after = loudness(out)
    (ROOT / "output").mkdir(exist_ok=True)
    shutil.copy2(out, ROOT / "output" / "rohschnitt.mp4")
    print(f"   cut.mp4: {m['input_i']} -> {after['input_i']} LUFS, TP {after['input_tp']}")
    print(f"   -> {out}  und  output/rohschnitt.mp4")


if __name__ == "__main__":
    main()
