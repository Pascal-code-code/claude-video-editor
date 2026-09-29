#!/usr/bin/env bash
# Einmaliges Setup fuer claude-video-editor (macOS). Laeuft mehrfach ohne Schaden.
# Aufruf aus dem Repo-Ordner:  bash setup/setup.sh
# Exit 2 = Homebrew fehlt (muss der Nutzer selbst im Terminal installieren, braucht sein Passwort).
set -u
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
ok()   { printf "  \033[32m✓\033[0m %s\n" "$1"; }
warn() { printf "  \033[33m!\033[0m %s\n" "$1"; }
fail() { printf "  \033[31m✗\033[0m %s\n" "$1"; }
step() { printf "\n\033[1m%s\033[0m\n" "$1"; }

step "1/7 System"
if [[ "$(uname)" != "Darwin" ]]; then
  warn "Kein macOS erkannt. Getestet ist nur der Mac; unter Linux/WSL kann es klappen, Pakete dann selbst installieren."
fi
if ! command -v brew >/dev/null 2>&1; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [[ -x $b ]] && eval "$($b shellenv)"; done
fi
if ! command -v brew >/dev/null 2>&1; then
  fail "Homebrew fehlt. Bitte im Programm Terminal (nicht in Claude Code) einfügen und Passwort eingeben:"
  echo '    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  echo "  Danach dieses Setup erneut starten."
  exit 2
fi
ok "Homebrew $(brew --version | head -1 | awk '{print $2}')"

step "2/7 ffmpeg, Node.js, uv"
for pkg in ffmpeg node uv; do
  bin=$pkg; [[ $pkg == uv ]] && bin=uv
  if command -v "$bin" >/dev/null 2>&1; then ok "$pkg vorhanden"; else
    echo "  installiere $pkg ..."; brew install "$pkg" >/dev/null && ok "$pkg installiert" || { fail "$pkg ließ sich nicht installieren"; exit 1; }
  fi
done
NODE_MAJOR=$(node -p 'process.versions.node.split(".")[0]')
if (( NODE_MAJOR < 22 )); then echo "  Node $NODE_MAJOR ist zu alt, aktualisiere ..."; brew upgrade node >/dev/null || brew install node >/dev/null; fi
ok "Node $(node --version)"
if ffmpeg -hide_banner -filters 2>/dev/null | grep -q zscale; then ok "ffmpeg mit zscale (HDR-Umrechnung)"; else warn "ffmpeg ohne zscale: iPhone-HDR-Videos lassen sich nicht umrechnen. Beim Filmen HDR ausschalten."; fi

step "3/7 HyperFrames + GSAP"
npm install --no-audit --no-fund --loglevel=error >/dev/null 2>&1 && ok "npm-Pakete installiert" || { fail "npm install fehlgeschlagen"; exit 1; }
cp node_modules/gsap/dist/gsap.min.js template/fx/gsap.min.js && ok "gsap.min.js bereit"
npx hyperframes browser ensure >/dev/null 2>&1 && ok "Render-Browser bereit" || warn "Render-Browser noch nicht geladen, passiert beim ersten Render"

step "4/7 Python-Umgebung für den Freisteller"
if [[ ! -x .venv/bin/python ]]; then uv venv .venv --python 3.12 -q || { fail "uv venv fehlgeschlagen"; exit 1; }; fi
uv pip install -q --python .venv/bin/python rembg onnxruntime opencv-python-headless pillow numpy \
  && ok ".venv mit rembg + opencv" || { fail "Python-Pakete fehlgeschlagen"; exit 1; }
.venv/bin/python -c "from rembg import new_session; new_session('u2net_human_seg')" >/dev/null 2>&1 \
  && ok "Freisteller-Modell geladen (u2net_human_seg)" || warn "Freisteller-Modell wird beim ersten Lauf geladen"

step "5/7 WhisperX (Transkription, lädt ~2 GB beim ersten Mal)"
uvx --python 3.12 --from whisperx --with numpy python -c "
import whisperx
whisperx.load_model('large-v3-turbo', 'cpu', compute_type='int8', language='de')
whisperx.load_align_model(language_code='de', device='cpu')
" >/dev/null 2>&1 && ok "WhisperX + deutsches Alignment bereit" || warn "WhisperX-Vorladen fehlgeschlagen, wird beim ersten Transkript erneut versucht"

step "6/7 Soundeffekte von Mixkit"
mkdir -p template/fx/sfx
cp template/fx/click.wav template/fx/sfx/click.wav
python3 - <<'PY'
import json, subprocess, urllib.request, tempfile, os
cfg = json.load(open("setup/sfx.json"))
for s in cfg["sounds"]:
    out = os.path.join("template/fx/sfx", s["file"])
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print(f"  \033[32m✓\033[0m {s['file']} vorhanden"); continue
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(s["url"])[1]).name
        req = urllib.request.Request(s["url"], headers={"User-Agent": "Mozilla/5.0"})
        open(tmp, "wb").write(urllib.request.urlopen(req, timeout=60).read())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", f"volume={s['gain_db']}dB",
                        "-ar", "48000", "-ac", "2", out], check=True)
        print(f"  \033[32m✓\033[0m {s['file']}")
    except Exception as e:
        print(f"  \033[33m!\033[0m {s['file']} nicht geladen ({e}); Video läuft dann ohne diesen Sound")
PY

step "7/7 Ordner"
mkdir -p input output projekte
ok "input/  (hier dein Video ablegen)"
ok "output/ (hier landen Rohschnitt und fertiges Video)"
printf "\n\033[1mFertig.\033[0m Nächster Schritt: Video nach input/ legen und in Claude Code /claude-video-editor tippen.\n"
