# claude-video-editor

Dieses Repo schneidet Talking-Head-Videos im Stil "Claude hat 100 % dieses Videos editiert".
Die Arbeitsanweisung steht im Skill `.claude/skills/claude-video-editor/SKILL.md`. Lade ihn, sobald der
Nutzer ein Video bearbeiten, das Setup starten oder ein Skript schreiben will, auch ohne Slash-Befehl.

- Sprich Deutsch, per du, in kurzen Sätzen. Der Nutzer ist meist kein Entwickler.
- Aufnahmen liegen in `input/` und werden nie verändert. Ergebnisse gehen nach `output/`.
- Jedes Video bekommt einen Ordner unter `projekte/<name>/`.
- Pfade können Leerzeichen enthalten: immer in Anführungszeichen setzen.
