# Claude Video Editor

Claude hat 100% von meinem Reel geschnitten: oben Split Screen mit 3D-Effekten auf jedes Wort, unten die unbearbeitete Aufnahme. Dieses Repo baut dir das Gleiche mit deiner eigenen Aufnahme, über Claude Code.

Jeder Satz, den du sprichst, ist ein Befehl an Claude, und der Effekt landet genau auf dem Schlüsselwort. Die Anleitung Schritt für Schritt liegt in [`docs/Installation.pdf`](docs/Installation.pdf).

## Quick Start

1. Grüner Button "Code" auf GitHub, "Download ZIP", entpacken. Oder per Terminal:
   ```
   git clone https://github.com/Pascal-code-code/claude-video-editor.git
   ```
2. Ordner in Claude Code öffnen. Nach dem ZIP-Download heißt er "claude-video-editor-main", nach git clone "claude-video-editor" (Desktop-App: Ordner wählen. Terminal: in den Ordner wechseln, dann `claude`).
3. Einmal einrichten:
   ```
   /claude-video-editor setup
   ```
   Installiert ffmpeg, Node.js, die Python-Pakete, HyperFrames, das Freistell-Modell und Soundeffekte von Mixkit. Dauert 10 bis 20 Minuten, Claude fragt vor jedem Befehl um Erlaubnis. Fehlt Homebrew auf deinem Mac, gibt dir Claude einen Befehl: den fügst du im Programm Terminal ein, tippst dein Mac-Passwort (man sieht es nicht) und startest das Setup danach nochmal.
4. Skript vorbereiten: `skript-vorlage.md` öffnen und nehmen wie es ist, oder Claude bitten: "Schreib mir das Skript zum Thema X im Format der Vorlage".
5. Aufnehmen: Handy quer auf Stativ, du leicht links von der Mitte, rechts freie Wand, HDR-Video aus, gutes Licht von vorne. Am Stück sprechen, bei Versprechern den Satz einfach wiederholen.
6. Videodatei (.mov oder .mp4) in den Ordner `input/` legen.
7. Schneiden lassen:
   ```
   /claude-video-editor
   ```
   Claude transkribiert, wählt die besten Takes, entfernt Versprecher und Pausen und zeigt dir zuerst den Rohschnitt (`output/rohschnitt.mp4`). Nach deinem Okay baut Claude die Effekte und rendert das fertige Video nach `output/`. Rechne mit 30 bis 60 Minuten Maschinenzeit für 30 Sekunden Reel.
8. Nachträglich ändern geht in normalen Worten, z.B. "Mach den Titel oben: Claude hat mein Video geschnitten" oder "Nimm meine eigenen Reel-Cover aus input/reels" (Bilder vorher dort ablegen).

## Was im Repo liegt

- `.claude/skills/claude-video-editor/`: der Skill, der die ganze Pipeline steuert
- `tools/`: Hilfsskripte für Transkription, Schnitt, Freistellen
- `template/`: Vorlage für die Motion-Graphics-Komposition
- `setup/`: Setup-Skripte für `/claude-video-editor setup`
- `input/`: hier legst du deine Aufnahme ab
- `output/`: hier landen Rohschnitt und fertiges Video
- `projekte/`: deine Projekte, ein Ordner pro Video
- `skript-vorlage.md`: mein Skript mit 13 Befehlen und Gesten-Notizen
- `docs/Installation.pdf`: die Anleitung Schritt für Schritt

## Voraussetzungen

- Mac, Apple Silicon oder Intel (Windows ungetestet)
- Claude Code installiert, mit Pro- oder Max-Plan
- ~5 GB freier Speicher
- iPhone oder Kamera plus Stativ

## Troubleshooting

- "Befehl nicht gefunden" / command not found: `/claude-video-editor setup` nochmal laufen lassen.
- Claude Code zeigt "skill not found": du hast einen übergeordneten Ordner geöffnet statt den Repo-Ordner selbst (der mit README.md und skript-vorlage.md darin).
- Render sehr langsam: andere Programme schließen, das läuft alles auf der CPU.
- Gesicht wirkt verwaschen: HDR war an. Claude wandelt es um, oder du nimmst mit HDR aus neu auf.

## Credits & Lizenzen

- [HyperFrames](https://github.com/heygen-com/hyperframes) von HeyGen, Apache-2.0
- GSAP
- WhisperX
- rembg / u2net
- Soundeffekte von Mixkit, werden bei der Einrichtung auf deinem eigenen Rechner geladen, unter der Mixkit Free License, nicht Teil dieses Repos

Claude ist eine Marke von Anthropic. Dieses Projekt steht in keiner Verbindung zu Anthropic.

Code steht unter der MIT-Lizenz, © 2026 Pascal Frey.
