---
name: claude-video-editor
description: Schneidet ein Talking-Head-Video im Stil "Claude hat 100 % dieses Videos editiert" – 9:16-Split, oben 16:9 mit Motion Graphics (Kino-Trailer, 3D-Logo auf der Hand, Glassprung, Ebenen-Explosion mit Freisteller, Ausblenden, Rahmen-Slide, schwebende Reels, Karte auf den Kopf, CTA), unten das Original. Nutzen bei "/claude-video-editor", "schneide mein Video", "Video aus input bearbeiten", "setup", "Skript schreiben" oder wenn ein Video in input/ liegt.
---

# Claude Video Editor

Du arbeitest im Repo `claude-video-editor`. Der Nutzer ist meist kein Entwickler: kurze Sätze auf Deutsch,
per du, jeder Schritt mit Zeitangabe, keine Fachbegriffe ohne Erklärung. Frag nur, wenn eine Entscheidung
wirklich beim Nutzer liegt. Alle Befehle laufen im Repo-Ordner.

Modus nach Aufruf:
- `/claude-video-editor setup` → **Setup**
- `/claude-video-editor skript <thema>` oder "schreib mir ein Skript" → **Skript**
- sonst → **Video schneiden** (Video liegt in `input/`)

## Setup

1. `bash setup/setup.sh` ausführen (Timeout 30 min). Endet es mit Exit 2, fehlt Homebrew: dem Nutzer den
   ausgegebenen Befehl zeigen und sagen, dass er ihn im Programm **Terminal** (nicht in Claude Code) einfügt,
   Enter drückt und sein Mac-Passwort eingibt (man sieht beim Tippen nichts). Danach Setup erneut starten.
2. Jede Zeile mit ✗ klären; Zeilen mit ! erklären, aber nicht blockieren.
3. Abschluss: sagen, dass alles bereit ist, und auf `skript-vorlage.md` und die Aufnahme-Regeln verweisen
   (siehe `reference/aufnahme.md`).

## Skript

Vorlage: `skript-vorlage.md`. Jeder Satz ist ein Befehl an Claude mit einer Geste. Die Effekte hängen an
Schlüsselwörtern (Tabelle in `reference/effekte.md`). Beim Umschreiben auf ein neues Thema:
- Reihenfolge der 12 Blöcke behalten, Schlüsselwörter möglichst behalten (oder in `config.json` nachziehen).
- Der erste Satz wird der Kino-Trailer: 8 bis 16 Wörter, in 4 Teile teilbar.
- Satz nach "zeig links, wie …" liefert die Slide-Headline, dazu 3 Listenpunkte (`texte.liste`).
- Ende: CTA mit einem Stichwort zum Kommentieren.
Skript als Datei `skript.md` im Repo speichern und dem Nutzer zeigen.

## Video schneiden

Zeitbedarf ansagen: ~10 min Transkript, ~5 min Schnitt, 10 bis 30 min Freisteller, ~5 min Render.

### 1. Projekt
- Aufnahme in `input/` suchen (.mov/.mp4). Mehrere → fragen, welche.
- `python3 tools/new_project.py input/<datei> <kurzer-name>` → `projekte/<name>/`.

### 2. Transkript
- `uvx --python 3.12 --from whisperx --with numpy python tools/transcribe.py projekte/<name>` (Timeout 30 min, im Hintergrund).
- Ergebnis `edit/islands.json`: je Sprech-Insel Zeit, Text, Wörter, `rms_blocks`.

### 3. Takes wählen → `edit/spans.json`
Leg die Inseln gegen `skript.md` bzw. `skript-vorlage.md`. Pro Satz den **letzten vollständigen** Anlauf.
Regeln und Fallen (wichtig): `reference/schnitt.md`. Kurz:
- `start` = Start erstes Wort, `end` = Ende letztes Wort des gewählten Anlaufs.
- Aufeinanderfolgende Sätze aus demselben Durchgang dürfen eigene Spans sein; die Pause dazwischen fällt weg.
- Kurze Einwürfe ("Nice.", "Au!") setzt der Aligner oft falsch: mit `rms_blocks` vergleichen, dann
  `hardin`/`hardout` setzen und `start` auf die Aligner-Zeit lassen.
- Fehlt ein Satz komplett in der Aufnahme: dem Nutzer sagen, weiter ohne ihn.
- `speed`: Standard 1.1 (10 % schneller). Nutzer kann 1.0 wollen.
Dann `python3 tools/cut.py projekte/<name> --edl`: Schnittliste prüfen, gemeldete Restpausen als `drops` eintragen, erneut `--edl`.

### 4. Rohschnitt
- `python3 tools/cut.py projekte/<name>` → `assets/cut.mp4`, Kopie `output/rohschnitt.mp4`.
- Prüfen: `uvx --python 3.12 --from whisperx --with numpy python tools/verify_cut.py projekte/<name>`.
  Keine Pause ≥ 0,2 s, kein doppelter Satzanfang, kein fehlendes Wortende. Schreibweisen (Claude/Cloud) sind egal.
  Anfang unter -5 dB gegen Median → `intro_boost_db` 3 bis 4 setzen und neu schneiden.
- **STOPP:** Dem Nutzer Schnittliste (Satz, Quelle von-bis, Grund) und `output/rohschnitt.mp4` zeigen.
  Erst nach seinem OK weiter. Änderungswünsche in spans.json umsetzen.

### 5. Positionen und Texte → `config.json`
- `python3 tools/grid.py projekte/<name> <t_logo> <t_wurf> <t_rahmen> <t_au>` (Zeiten aus cut.words.json),
  `verify/grid.jpg` ANSEHEN. Rasterlinien = Anteile 0,1 … 0,9.
- `positionen.hand`: Handfläche beim Logo. `wurf_hand`: Hand beim Wurf. `kopf`: Kopfmitte x und Kopf-Oberkante y
  beim "Au". `person_x`: Körpermitte.
- `texte`: `name`, `rolle` (Namensschild), CTA-Wort, Titel. Den Nutzer nach Name, Rolle und CTA-Stichwort fragen,
  falls unbekannt. `trailer.teile`: erster Satz in 4 Teile (klein/groß, Wort für den Einsatz).
- `woerter`: Schlüsselwort je Effekt, so wie es im Transkript steht (`cut.words.json`).
- Eigene Reel-Cover: liegen Bilder in `input/reels/`, nach `projekte/<name>/assets/reels/` kopieren (hochkant, ~540x960). Sonst erzeugt gen.py Standbilder aus dem Video.

### 6. HTML erzeugen
- `python3 tools/gen.py projekte/<name>` → `index.html`. Fehlt ein Wort, nennt gen.py die Stelle: `woerter` anpassen.
- Die letzte Zeile nennt die Freisteller-Zeitfenster.

### 7. Freisteller und leere Wand
- `.venv/bin/python -u tools/matte.py projekte/<name> --ranges <aus gen.py>` (Hintergrund, ~1,5 bis 3 s pro Bild).
- `.venv/bin/python tools/plate.py projekte/<name>`, danach `assets/cleanplate.jpg` und
  `verify/cleanplate-hole.png` ANSEHEN. Hautfarbene Schlieren, wo meist ein Arm liegt → `--colfill y0,x0,x1`
  (Anteile: ab Höhe y0 zwischen x0 und x1 senkrecht auffüllen).
- Freisteller prüfen: 3 Bilder über Magenta (Befehl in `reference/pruefen.md`).

### 8. Prüfen und rendern (im Projektordner)
- `cd projekte/<name> && npx hyperframes lint` → 0 Fehler.
- `npx hyperframes snapshot --at <je Effekt 1 Zeitpunkt> --no-end --describe false -o verify/snap .`,
  Kontaktbogen ANSEHEN: Text lesbar, nichts im Gesicht, Ebenen sichtbar getrennt, Karte trifft den Kopf.
  Korrekturen in `config.json` bzw. `edit/index.tpl`, dann gen.py erneut.
- `npx hyperframes render -q high -o renders/final.mp4 .` (~3 bis 5 min, Hintergrund).
- `cd ../.. && .venv/bin/python tools/check.py projekte/<name>`; `verify/final-sheet.jpg` ANSEHEN.
- Kopie nach `output/<name>.mp4`. Dem Nutzer: Pfad, Länge, was er wo ändern kann (in normalen Worten).

## Änderungen später
Nutzer sagt z. B. "Titel oben: …", "Name ändern", "Logo später" → `config.json` ändern, `gen.py`, rendern.
Effekt-Zeiten verschieben: anderes Schlüsselwort in `woerter`. Neue Effekte: `reference/effekte.md` (Bibliothek `assets/pascal-fx.js`).

## Nicht tun
- Nie die Aufnahme in `input/` verändern oder löschen.
- Unten (ORIGINAL) nichts verändern: kein Zoom, keine Untertitel.
- Keine Grafik ins Gesicht. Kein Render, bevor der Rohschnitt abgenommen ist.
- Nicht als fertig melden, ohne Kontaktbogen und check.py angesehen zu haben.
