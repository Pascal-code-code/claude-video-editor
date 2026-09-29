# Schnitt: Regeln und Fallen

Aus der Praxis mit echten Aufnahmen. Jede Regel hat schon einmal einen Fehler im fertigen Video verhindert.

## Takes wählen
- Pro Satz den **letzten vollständigen** Anlauf. Wer sich verspricht, sagt den Satz meist neu; der letzte ist der saubere.
- Prüfe jeden Anlauf Wort für Wort gegen das Skript. "Raben" statt "Rahmen" = Versprecher, nicht nehmen.
- Weicht der letzte Anlauf vom Skript ab, aber ist sauber gesprochen: nehmen und dem Nutzer sagen.
- Sätze, die in keiner Insel vorkommen, fehlen in der Aufnahme. Nicht erfinden, dem Nutzer melden.

## Wortzeiten (WhisperX) sind nicht immer richtig
- **Kurze Einwürfe** ("Nice.", "Au!", "Oh."): Der Aligner setzt sie oft 0,1 bis 0,2 s zu früh und viel zu kurz.
  In `islands.json` die `rms_blocks` der Insel ansehen: der Block ist die echte Lage. `hardin` = Blockbeginn - 0,02,
  `hardout` = Blockende + 0,06. `start` bleibt die Aligner-Zeit (sonst findet cut.py das Wort nicht).
- **Verschluckte Fehlstarts**: Ein Einzelwort, das länger als ~0,45 s dauert, oder ein Energie-Block
  deutlich vor dem ersten Wort (> 0,25 s) ist verdächtig. Dann liegt dort ein abgebrochener Anlauf. Span-Start
  hinter diesen Block legen (`hardin`) und im Zweifel `noext: true` setzen.
- **Gedehnte Wörter über Pausen**: cut.py findet Restpausen trotzdem und meldet sie bei `--edl`
  ("Restpausen ... als drops eintragen"). Alle eintragen, wenn der Nutzer "Pausen raus" will (Standard).

## Pausen und Tempo
- Standard: alle Sprechpausen raus (Restluft ~0,15 s), Tempo 1,1. Beides wirkt schneller und hält Zuschauer.
- Wer die Aufnahme ruhiger will: `speed: 1.0`, `drops: []`.
- Beide Fenster zeigen dieselbe Datei. Tempo und Schnitt gelten also automatisch oben und unten.

## Ton
- cut.py normalisiert auf -14 LUFS (Instagram/TikTok) und hebt mit `dynaudnorm` leise Stellen an.
- Ist der erste Satz nach verify_cut.py mehr als 3 dB leiser als der Rest: `intro_boost_db: 3.5`.

## Nach dem Rohschnitt
verify_cut.py hört den Schnitt neu ab. Echte Fehler: doppelte Wörter ("Also an Also an"), fehlende Silben
("Biss" statt "Business"), Pausen ≥ 0,2 s. Dann Span-Grenzen korrigieren und neu schneiden, bis sauber.
