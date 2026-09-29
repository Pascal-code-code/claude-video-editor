# Effekte und Schlüsselwörter

Jeder Effekt startet auf einem gesprochenen Wort (`config.json` → `woerter`). Reihenfolge ist fest,
gen.py sucht die Wörter nacheinander.

| # | Satz (Vorlage) | Wort-Schlüssel | Effekt oben |
|---|---|---|---|
| 1 | Erster Satz | `trailer.teile` | Kino-Trailer: Schwarz ↔ graues Bild mit Kinobalken, kleine gesperrte Zeile + großes Chrom-Wort, Lichtstreifen, letztes Wort füllt das Bild und fliegt mit Unschärfe raus. Riser + Aufprall-Sound. |
| 2 | "Zoom auf meine Hand …" | `zoom`, `logo`, `d3` | Push-in auf die Hand (`positionen.hand`), 3D-Claude-Logo wächst auf der Hand und dreht sich. |
| 3 | "Nice." | `nice` | Logo wippt. |
| 4 | "… wirf's in die Kamera." | `kamera` | Logo folgt der Hand (`wurf_hand`), fliegt in die Linse, 1 Frame Weißblitz, Glassprung über beide Fenster und Titel, Splitter fallen ins Original. |
| 5 | "Okay, …" | `okay` | Sprünge verblassen. |
| 6 | "Zerleg das Bild in Ebenen" | `zerlege`, `ebenen` | Titel erscheint an der Wand (`texte.ebene_titel`), dann kippt das Bild in 3D und fächert auf: leere Wand / Person (Freisteller) / Text. |
| 7 | "den Hintergrund, mich und den Text" | `hgrund`, `mich`, `text` | Ebenen-Panel rechts, Chip an jeder Ebene, Zeile leuchtet auf dem Wort. |
| 8 | "Jetzt blend mich aus." | `blend`, `aus` | Mauszeiger klickt das Auge, Person verschwindet, Tag "AUSGEBLENDET". |
| 9 | "… hol mich zurück." | `zurueck` | Person kommt zurück, Ebenen fahren zusammen. |
| 10 | "Pack mich rechts in einen Rahmen, zeig links, wie …" | `rahmen`, `links`, `headline`, `reel` | Bild schrumpft zur Karte rechts (Namensschild), links Kicker, Headline Wort für Wort, 3 Listenpunkte mit Haken. |
| 11 | "Zurück ins Vollbild. Lass meine Reels hinter mir schweben." | `vollbild`, `reels` | Vollbild, 6 Reel-Cover steigen hinter und vor der Person auf. |
| 12 | "Au!" | `oh` | Eine Karte fällt auf den Kopf (`positionen.kopf`), ragt über den Fensterrand, Aufprall-Linien. |
| 13 | CTA "Kommentier EDIT …" | `komm`, `edit`, `kostenlose`, `karte`, `kreis` | KOMMENTIERE, oranger Balken legt das Stichwort frei, Band, Anleitungs-Karte, gezeichneter Kreis. |

Untertitel: nur oben, 1 bis 3 Wörter, Wörter aus `untertitel.akzent` in Orange. Keine Untertitel im Trailer und in der Rahmen-Slide.

## Freisteller
Die Person wird für Block 6 bis 9 und 11 bis 12 vom Hintergrund getrennt (`tools/matte.py`, Modell u2net_human_seg).
Die leere Wand (`tools/plate.py`) entsteht aus allen Bildern, in denen die Person gerade woanders steht.

## Eigene Effekte bauen
`assets/pascal-fx.js` enthält die Bausteine als Funktionen (`PFX.textBehind`, `PFX.cards`, `PFX.drop`,
`PFX.logo3D`, `PFX.crack`, `PFX.flash`, `PFX.pushIn`, `PFX.explode`, `PFX.frameCard`, `PFX.chip`, `PFX.captions`).
Kopf der Datei beschreibt den Ebenen-Aufbau (Grafik hinter der Person: `.pfx-back` unter dem Freisteller).
Regeln: Effekt nur mit gesprochenem Anlass, eine Akzentfarbe (#D97757), nie zweimal derselbe Trick hintereinander.
