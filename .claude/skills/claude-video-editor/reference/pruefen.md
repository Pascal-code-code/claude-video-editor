# Prüf-Befehle

Freisteller über Magenta (3 Zeitpunkte aus den --ranges):
```bash
P=projekte/<name>; i=0
for t in 12.5 14.8 21.5; do
  ffmpeg -v error -y -f lavfi -i color=c=magenta:s=1280x720 -c:v libvpx-vp9 -ss $t -i $P/assets/person.webm \
    -filter_complex "[0][1]overlay=shortest=1,scale=640:360" -frames:v 1 $P/verify/m$i.png; i=$((i+1))
done
ffmpeg -v error -y -i $P/verify/m0.png -i $P/verify/m1.png -i $P/verify/m2.png -filter_complex hstack=3 $P/verify/matte-check.jpg
```
Ansehen: Haare sauber? Hände/Arme vollständig? Kein Hintergrund-Rest?

Frame-Zahl muss passen (sonst driftet der Freisteller):
```bash
ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $P/assets/person.webm
ffprobe -v error -count_packets -select_streams v -show_entries stream=nb_read_packets -of csv=p=0 $P/assets/cut.mp4
```

Typische Lint-Fehler und Lösung:
- `missing_local_asset person.webm` → matte.py noch nicht gelaufen.
- `overlapping_gsap_tweens` → zwei Effekt-Wörter liegen zu dicht; anderes Wort in `woerter` wählen.

Wenn im Render das Gesicht dunkler wirkt als im Rohschnitt: check.py zeigt die Abweichung; über ±3 % in
`edit/index.tpl` bei `.vid{... filter:brightness(1.045)}` nachregeln.
