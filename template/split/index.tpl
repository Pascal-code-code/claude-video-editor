<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>Claude edited 100%</title>
<script src="assets/gsap.min.js"></script>
<style>
:root{
  --bg:#0B0B0C; --claude:#D97757; --claude-rgb:217,119,87; --white:#FFFFFF;
  --glass:rgba(12,12,14,.72); --line:rgba(255,255,255,.18);
  --font:"Inter",system-ui,sans-serif; --mono:"JetBrains Mono","SF Mono",ui-monospace,monospace;
  --W:1044px; --H:587px;
}
*{box-sizing:border-box}
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:var(--bg)}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:var(--bg);font-family:var(--font)}

/* ---------- Buehne ---------- */
#glow{position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(60% 32% at 92% 4%,rgba(var(--claude-rgb),.30) 0%,rgba(var(--claude-rgb),.10) 45%,transparent 75%),
             radial-gradient(90% 60% at 50% 55%,transparent 55%,rgba(0,0,0,.55) 100%)}
.pill{position:absolute;left:50%;transform:translateX(-50%);height:76px;padding:0 26px;border-radius:12px;background:#fff;
  display:flex;align-items:center;gap:14px;white-space:nowrap;font-weight:800;font-size:44px;letter-spacing:-.02em;color:#0B0B0C;
  box-shadow:0 10px 30px rgba(0,0,0,.35)}
.pill svg{width:44px;height:44px}
#pill1{top:228px}
#pill2{top:316px}

.win{position:absolute;left:18px;width:var(--W);height:var(--H);border-radius:21px;overflow:hidden;background:#0d0d10;
  box-shadow:0 0 0 1.5px var(--line),0 24px 60px rgba(0,0,0,.5)}
#winT{top:453px;background:radial-gradient(70% 90% at 80% 10%,rgba(var(--claude-rgb),.16),transparent 70%),#0d0d10}
#winB{top:1060px}
.vid{position:absolute;left:0;top:0;width:var(--W);height:var(--H);object-fit:cover;filter:brightness(1.045)}
.badge{position:absolute;left:24px;top:24px;z-index:40;height:46px;padding:0 18px 0 12px;border-radius:23px;background:var(--glass);
  border:1px solid rgba(255,255,255,.14);display:flex;align-items:center;gap:10px;font-weight:800;font-size:22px;
  letter-spacing:.08em;color:#fff;backdrop-filter:blur(10px)}
.badge svg{width:24px;height:24px}
#winB .badge{padding-left:18px}

/* ---------- oberes Fenster: Kamera ---------- */
#cam{position:absolute;inset:0;transform-origin:56% 72%}
#starWrap{position:absolute;left:0;top:0;width:var(--W);height:var(--H);perspective:900px;pointer-events:none}
#star{position:absolute;left:510px;top:285px;width:150px;height:150px;transform-style:preserve-3d;opacity:0}
#star .sl{position:absolute;inset:0;width:150px;height:150px}
#star .sl path{fill:#9c4a31}
#star .sl.front path{fill:var(--claude)}
#star .sl.front{filter:drop-shadow(0 0 18px rgba(var(--claude-rgb),.55))}
#starShadow{position:absolute;left:520px;top:420px;width:130px;height:26px;border-radius:50%;
  background:radial-gradient(closest-side,rgba(0,0,0,.45),transparent);opacity:0}

/* Trailer */
#tr{position:absolute;inset:0;z-index:20;pointer-events:none}
#trBlack{position:absolute;inset:0;background:#050505;opacity:0}
.bar{position:absolute;left:0;width:100%;height:0;background:#000}
#barT{top:0}#barB{bottom:0}
.trs{position:absolute;left:0;width:100%;text-align:center;font-weight:700;font-size:26px;letter-spacing:.5em;color:#cfcfcf;
  text-transform:uppercase;opacity:0;text-shadow:0 2px 12px rgba(0,0,0,.6)}
.trb{position:absolute;left:0;width:100%;text-align:center;font-weight:900;text-transform:uppercase;letter-spacing:-.02em;line-height:1;
  background:linear-gradient(180deg,#ffffff 0%,#f2f2f2 38%,#8f8f8f 62%,#dcdcdc 100%);-webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 18px rgba(255,255,255,.25));opacity:0}
#streak{position:absolute;top:0;left:-700px;width:520px;height:100%;opacity:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.0) 30%,rgba(255,255,255,.55) 50%,rgba(255,255,255,0) 70%,transparent);
  mix-blend-mode:screen;transform:skewX(-18deg)}
#flare{position:absolute;width:900px;height:6px;border-radius:3px;background:radial-gradient(closest-side,#fff,rgba(255,235,210,.4) 40%,transparent);
  filter:blur(2px);opacity:0}
#flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:30}

/* Ebenen */
#layers{position:absolute;inset:0;perspective:1300px;perspective-origin:45% 40%;z-index:5;pointer-events:none}
#stack{position:absolute;inset:0;transform-style:preserve-3d;opacity:0}
.plane{position:absolute;left:0;top:0;width:var(--W);height:var(--H)}
#pBG{background:url(assets/cleanplate.jpg) center/cover;filter:brightness(1.045);opacity:0}
#pME{opacity:0}
#pME video{position:absolute;left:0;top:0;width:var(--W);height:var(--H);filter:brightness(1.045)}
#pTX{opacity:1}
.pf{position:absolute;inset:0;border-radius:18px;border:2.5px solid rgba(255,255,255,.75);opacity:0;
  box-shadow:0 0 50px rgba(var(--claude-rgb),.35),inset 0 0 40px rgba(255,255,255,.06);background:rgba(255,255,255,.035)}
#txTitle{position:absolute;left:640px;top:70px;width:380px}
#txTitle div{font-weight:900;font-size:62px;line-height:.98;letter-spacing:-.03em;text-transform:uppercase;color:#fff;
  text-shadow:0 4px 24px rgba(0,0,0,.35)}
#txTitle div.o{color:var(--claude)}
.chip{position:absolute;left:26px;top:26px;padding:12px 20px;border-radius:14px;background:var(--glass);border:1.5px solid rgba(255,255,255,.2);
  display:flex;align-items:baseline;gap:14px;white-space:nowrap;opacity:0}
.chip b{font-family:var(--mono);font-size:30px;color:var(--claude);font-weight:700}
.chip span{font-size:40px;font-weight:800;color:#fff}
.chip i{font-style:normal;font-family:var(--mono);font-size:22px;letter-spacing:.14em;color:rgba(255,255,255,.7)}
#chipTX{left:640px;top:330px}
#chipME{left:40px;top:420px}
#hidTag{position:absolute;left:330px;top:250px;padding:14px 26px;border-radius:12px;background:var(--claude);color:#111;
  font-weight:900;font-size:44px;letter-spacing:.08em;opacity:0}

#panel{position:absolute;left:800px;top:96px;width:222px;z-index:12;padding:14px 12px;border-radius:16px;background:rgba(18,18,22,.86);
  border:1px solid rgba(255,255,255,.14);box-shadow:0 20px 50px rgba(0,0,0,.5);opacity:0}
#panel h4{margin:2px 6px 10px;font-size:18px;font-weight:800;color:rgba(255,255,255,.85);letter-spacing:.02em}
.row{position:relative;display:flex;align-items:center;gap:10px;height:50px;padding:0 8px;border-radius:10px;font-size:21px;font-weight:700;color:#fff}
.row .hl{position:absolute;inset:0;border-radius:10px;background:rgba(var(--claude-rgb),.22);box-shadow:inset 0 0 0 1.5px rgba(var(--claude-rgb),.8);opacity:0}
.row .eye{position:relative;width:24px;height:24px;flex-shrink:0}
.row .eye svg{position:absolute;inset:0;width:24px;height:24px;stroke:#fff;fill:none;stroke-width:2;stroke-linecap:round}
.row .eye .off{opacity:0}
.row .th{position:relative;width:46px;height:28px;border-radius:5px;flex-shrink:0;background:#333 center/cover;border:1px solid rgba(255,255,255,.25)}
.row span{position:relative}
#cursor{position:absolute;left:640px;top:470px;width:34px;height:34px;z-index:14;opacity:0;filter:drop-shadow(0 3px 6px rgba(0,0,0,.5))}

/* Rahmen-Slide */
#cardFrame{position:absolute;left:690px;top:48px;width:320px;height:491px;border-radius:18px;z-index:8;pointer-events:none;opacity:0;
  box-shadow:0 0 0 2px rgba(255,255,255,.8),0 20px 60px rgba(0,0,0,.55)}
#nameTag{position:absolute;left:14px;right:14px;bottom:14px;padding:10px 14px;border-radius:12px;background:var(--glass);border:1px solid rgba(255,255,255,.16)}
#nameTag b{display:block;font-size:24px;font-weight:800;color:#fff}
#nameTag i{display:block;font-style:normal;font-family:var(--mono);font-size:15px;letter-spacing:.18em;color:var(--claude);margin-top:3px}
#slide{position:absolute;left:44px;top:78px;width:610px;z-index:8;pointer-events:none}
#kick{font-family:var(--mono);font-size:19px;font-weight:700;letter-spacing:.2em;color:var(--claude);opacity:0}
#headl{margin-top:14px;font-size:54px;font-weight:900;line-height:1.02;letter-spacing:-.03em;color:#fff}
#headl span{display:inline-block;margin-right:.24em;opacity:0}
#headl span.o{color:var(--claude)}
#list{margin-top:30px;display:flex;flex-direction:column;gap:14px}
.li{display:flex;align-items:center;gap:16px;padding:12px 16px;border-radius:14px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);opacity:0}
.li .ck{width:34px;height:34px;border-radius:50%;background:var(--claude);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.li .ck svg{width:20px;height:20px;stroke:#111;stroke-width:3.2;fill:none;stroke-linecap:round;stroke-linejoin:round}
.li b{font-family:var(--mono);font-size:20px;color:var(--claude)}
.li div{font-size:27px;font-weight:800;color:#fff;line-height:1.1}
.li div i{display:block;font-style:normal;font-weight:500;font-size:20px;color:rgba(255,255,255,.66)}

/* Reels */
.reels{position:absolute;inset:0;perspective:1200px;pointer-events:none}
#reelsBack{z-index:4}
#reelsFront{z-index:7}
.rc{position:absolute;width:150px;height:267px;margin:-133px 0 0 -75px;border-radius:14px;background:#222 center/cover;opacity:0;
  box-shadow:0 0 0 1.5px rgba(255,255,255,.55),0 18px 40px rgba(0,0,0,.55)}

/* CTA */
#ctaScrim{position:absolute;inset:0;z-index:9;opacity:0;pointer-events:none;
  background:radial-gradient(50% 90% at 100% 40%,rgba(8,8,10,.62) 0%,rgba(8,8,10,.35) 55%,transparent 100%)}
#cta{position:absolute;left:612px;top:84px;width:420px;z-index:10;pointer-events:none}
#ctaK{white-space:nowrap;font-size:50px;font-weight:900;letter-spacing:-.02em;color:#fff;opacity:0;text-shadow:0 4px 20px rgba(0,0,0,.5)}
#ctaBarW{position:relative;margin-top:10px;width:330px;height:112px}
#ctaBar{position:absolute;inset:0;background:var(--claude);border-radius:6px;transform-origin:0 50%;transform:scaleX(0)}
#ctaEdit{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:88px;font-weight:900;color:#111;letter-spacing:-.01em}
#ctaEdit span{display:inline-block;opacity:0}
#ctaRing{position:absolute;left:-34px;top:-26px;width:398px;height:164px;overflow:visible}
#ctaRing path{fill:none;stroke:#fff;stroke-width:5;stroke-linecap:round}
#ctaBand{margin-top:22px;display:inline-block;white-space:nowrap;padding:10px 16px;background:rgba(255,255,255,.16);border-radius:6px;
  font-size:26px;font-weight:800;letter-spacing:.06em;color:#fff;opacity:0}
#guide{margin-top:18px;width:380px;padding:16px 18px;border-radius:14px;background:#fff;display:flex;gap:14px;align-items:center;
  box-shadow:0 18px 40px rgba(0,0,0,.45);opacity:0}
#guide svg{width:48px;height:48px;flex-shrink:0}
#guide b{display:block;white-space:nowrap;font-size:24px;font-weight:900;color:#111;line-height:1.1}
#guide i{display:block;font-style:normal;font-family:var(--mono);font-size:14px;letter-spacing:.14em;color:#9c4a31;margin-top:4px}

/* Untertitel */
#caps{position:absolute;left:0;right:0;bottom:44px;z-index:25;text-align:center;pointer-events:none}
.cg{position:absolute;left:0;right:0;bottom:0;opacity:0;white-space:nowrap}
.cg span{display:inline-block;margin:0 .13em;font-size:40px;font-weight:800;letter-spacing:-.01em;color:#fff;opacity:0;
  text-shadow:0 2px 14px rgba(0,0,0,.75),0 1px 3px rgba(0,0,0,.6)}
.cg span.k{color:var(--claude)}

/* ausbrechende Elemente */
#crack{position:absolute;left:0;top:0;width:1080px;height:1920px;z-index:60;pointer-events:none;opacity:0}
#crack path{fill:none;stroke-linecap:round;stroke-linejoin:round}
#shards{position:absolute;inset:0;z-index:61;pointer-events:none}
.sh{position:absolute;opacity:0}
#drop{position:absolute;left:456px;top:421px;width:150px;height:267px;margin:-133px 0 0 -75px;border-radius:14px;z-index:62;opacity:0;
  background:url(assets/reels/reel-6.jpg) center/cover;box-shadow:0 0 0 1.5px rgba(255,255,255,.7),0 18px 40px rgba(0,0,0,.6)}
#bonk{position:absolute;left:456px;top:545px;width:0;height:0;z-index:63;pointer-events:none}
#bonk i{position:absolute;left:0;top:0;width:34px;height:4px;border-radius:2px;background:#fff;transform-origin:0 50%;opacity:0}
</style>
</head>
<body>
<div id="root" data-composition-id="claude-video" data-start="0" data-duration="__DUR__" data-width="1080" data-height="1920">
  <div id="glow"></div>

  <div id="pill1" class="pill"><svg viewBox="0 0 100 100"><path fill="#D97757" d="__STAR__"/></svg>__TXT_titel1__</div>
  <div id="pill2" class="pill">__TXT_titel2__</div>

  <!-- ================= oberes Fenster: EDIT ================= -->
  <div id="winT" class="win">
    <div id="cam">
      <video id="vTop" class="vid" src="assets/cut.mp4" data-start="0" data-duration="__DUR__" data-track-index="0" muted playsinline></video>
      <div id="starShadow"></div>
      <div id="starWrap"><div id="star"></div></div>
    </div>

    <div id="reelsBack" class="reels"></div>

    <div id="layers">
      <div id="stack">
        <div id="pBG" class="plane"><div class="pf"></div>
          <div id="chipBG" class="chip"><b>01</b><i>EBENE</i><span>__TXT_ebene1__</span></div></div>
        <div id="pME" class="plane">
          <video id="vMe" src="assets/person.webm" data-start="0" data-duration="__DUR__" data-track-index="1" muted playsinline></video>
          <div class="pf"></div>
          <div id="chipME" class="chip"><b>02</b><i>EBENE</i><span>__TXT_ebene2__</span></div></div>
        <div id="pHID" class="plane"><div id="hidTag">__TXT_ausgeblendet__</div></div>
        <div id="pTX" class="plane"><div class="pf"></div>
          <div id="txTitle"></div>
          <div id="chipTX" class="chip"><b>03</b><i>EBENE</i><span>__TXT_ebene3__</span></div></div>
      </div>
    </div>

    <div id="reelsFront" class="reels"></div>

    <div id="panel"><h4>Ebenen</h4>
      <div class="row" id="rowTX"><div class="hl"></div><div class="eye"><svg class="on" viewBox="0 0 24 24"><path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6S2 12 2 12z"/><circle cx="12" cy="12" r="2.6"/></svg></div><div class="th" style="background:linear-gradient(135deg,#fff 0 40%,#D97757 40% 70%,#333 70%)"></div><span>__TXT_ebene3__</span></div>
      <div class="row" id="rowME"><div class="hl"></div><div class="eye"><svg class="on" viewBox="0 0 24 24"><path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6S2 12 2 12z"/><circle cx="12" cy="12" r="2.6"/></svg><svg class="off" viewBox="0 0 24 24"><path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6S2 12 2 12z"/><path d="M4 20L20 4"/></svg></div><div class="th" style="background-image:url(assets/reels/reel-1.jpg)"></div><span>__TXT_ebene2__</span></div>
      <div class="row" id="rowBG"><div class="hl"></div><div class="eye"><svg class="on" viewBox="0 0 24 24"><path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6S2 12 2 12z"/><circle cx="12" cy="12" r="2.6"/></svg></div><div class="th" style="background-image:url(assets/cleanplate.jpg)"></div><span>__TXT_ebene1__</span></div>
    </div>
    <svg id="cursor" viewBox="0 0 24 24"><path d="M4 2l15 11-6.5 1.2L16 21l-3 1.4-3.4-6.9L4 20z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>

    <div id="cardFrame"><div id="nameTag"><b>__TXT_name__</b><i>__TXT_rolle__</i></div></div>
    <div id="slide">
      <div id="kick">__TXT_kicker__</div>
      <div id="headl"></div>
      <div id="list"></div>
    </div>

    <div id="ctaScrim"></div>
    <div id="cta">
      <div id="ctaK">__TXT_cta_klein__</div>
      <div id="ctaBarW"><div id="ctaBar"></div><div id="ctaEdit"></div>
        <svg id="ctaRing" viewBox="0 0 398 164"><path id="ring" d="M40 96 C 20 40, 150 8, 250 14 C 350 20, 392 60, 380 104 C 368 146, 250 160, 150 152 C 70 146, 16 120, 36 78"/></svg></div>
      <div id="ctaBand">__TXT_cta_band__</div>
      <div id="guide"><svg viewBox="0 0 100 100"><path fill="#D97757" d="__STAR__"/></svg><div><b>__TXT_karte1__</b><i>__TXT_karte2__</i></div></div>
    </div>

    <div id="tr">
      <div id="barT" class="bar"></div><div id="barB" class="bar"></div>
      <div id="trBlack"></div>
      <div id="streak"></div>
      <div id="flare"></div>
    </div>
    <div id="flash"></div>
    <div id="caps"></div>
    <div class="badge"><svg viewBox="0 0 100 100"><path fill="#D97757" d="__STAR__"/></svg>__TXT_badge__</div>
  </div>

  <!-- ================= unteres Fenster: ORIGINAL ================= -->
  <div id="winB" class="win">
    <video id="vBot" class="vid" src="assets/cut-orig.mp4" data-start="0" data-duration="__DUR__" data-track-index="2" muted playsinline></video>
    <div class="badge">__TXT_original__</div>
  </div>

  <!-- ================= ausbrechende Effekte (Buehnen-Koordinaten) ================= -->
  <svg id="crack" viewBox="0 0 1080 1920"></svg>
  <div id="shards"></div>
  <div id="drop"></div>
  <div id="bonk"></div>

  <!-- ================= Ton ================= -->
  <audio id="voice" src="assets/cut.mp4" data-start="0" data-duration="__DUR__" data-track-index="3" data-volume="1"></audio>
  __SFX__
</div>

<script>
(function(){
  const D = __DATA__;
  const T = D.T, P = D.pos, C = D.txt;
  const W = 1044, H = 587;
  const tl = gsap.timeline({paused:true});
  function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
  const rnd = mulberry32(444);
  const $ = (id) => document.getElementById(id);

  // Positionen aus config.json (Anteile des 16:9-Bildes)
  const HX = P.hand[0] * W, HY = P.hand[1] * H;            // Handflaeche
  const KX = P.kopf[0] * W, KY = P.kopf[1] * H;            // Kopf beim Aufprall: Mitte x, Oberkante y
  const PX = P.person_x * W;                               // Koerpermitte (Rahmen, Reels)
  const WX = P.wurf_hand[0] * W, WY = P.wurf_hand[1] * H;  // Hand beim Werfen
  $('cam').style.transformOrigin = (P.hand[0] * 100).toFixed(1) + '% ' + (P.hand[1] * 100 - 4).toFixed(1) + '%';
  $('star').style.left = (HX - 75) + 'px'; $('star').style.top = (HY - 161) + 'px';
  $('starShadow').style.left = (HX - 65) + 'px'; $('starShadow').style.top = (HY - 26) + 'px';
  const DROP_X = 18 + KX, DROP_Y = 453 + KY - 120;
  $('drop').style.left = DROP_X + 'px'; $('drop').style.top = DROP_Y + 'px';
  $('bonk').style.left = DROP_X + 'px'; $('bonk').style.top = (453 + KY + 4) + 'px';
  $('drop').style.backgroundImage = 'url(' + D.reels[D.reels.length - 1] + ')';

  /* ================= 1 · Trailer (erster Satz) ================= */
  const LB = 62, GREY = 'grayscale(0.85) contrast(1.15) brightness(0.82)';
  const tr = $('tr');
  tl.set('#cam', {filter: GREY}, 0);
  D.trailer.parts.forEach((p, i) => {
    const end = i + 1 < D.trailer.parts.length ? D.trailer.parts[i + 1].start : D.trailer.end;
    const last = i === D.trailer.parts.length - 1;
    const k = document.createElement('div'); k.className = 'trs'; k.textContent = p.klein;
    const g = document.createElement('div'); g.className = 'trb'; g.textContent = p.gross;
    const size = Math.min(last ? 210 : 128, Math.round(980 / Math.max(3, p.gross.length * 0.62)));
    g.style.fontSize = size + 'px';
    k.style.top = (last ? 150 : 176) + 'px';
    g.style.top = (last ? 196 : 232) + 'px';
    tr.appendChild(k); tr.appendChild(g);
    if (p.bg === 'schwarz') {
      tl.set('#trBlack', {opacity: 1}, p.start);
      tl.set(['#barT', '#barB'], {height: 0}, p.start);
      tl.fromTo('#streak', {x: 0, opacity: 1}, {x: 1900, opacity: 1, duration: 0.55, ease: 'power1.inOut'}, p.gAt);
    } else {
      tl.set('#trBlack', {opacity: 0}, p.start);
      tl.set(['#barT', '#barB'], {height: LB}, p.start);
      tl.fromTo('#cam', {scale: 1.08}, {scale: 1.0, duration: Math.max(0.2, end - p.start), ease: 'none'}, p.start);
    }
    if (i === 0) {
      tl.fromTo(k, {opacity: 0, scaleX: 1.25}, {opacity: 1, scaleX: 1, duration: 0.5, ease: 'power2.out'}, Math.max(0.02, p.kAt - 0.02));
      tl.fromTo('#flare', {opacity: 0, x: -200, y: 300}, {opacity: 0.9, x: 300, duration: 0.28, ease: 'power2.out'}, p.gAt + 0.05);
      tl.to('#flare', {opacity: 0, x: 600, duration: 0.25, ease: 'power2.in'}, p.gAt + 0.35);
    } else {
      tl.fromTo(k, {opacity: 0, y: 10}, {opacity: 1, y: 0, duration: 0.28, ease: 'power2.out'}, Math.max(p.start, p.kAt - 0.02));
    }
    if (last) {
      tl.fromTo(g, {opacity: 0, scale: 0.7}, {opacity: 1, scale: 1, duration: 0.14, ease: 'power3.out'}, p.gAt - 0.05);
      tl.to([k, g], {opacity: 0, scale: 1.5, filter: 'blur(18px)', duration: 0.16, ease: 'power2.in'}, D.trailer.end - 0.12);
    } else {
      tl.fromTo(g, {opacity: 0, scale: 1.18, filter: 'blur(14px)'}, {opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.38, ease: 'expo.out'}, p.gAt - 0.03);
      tl.set([k, g, '#streak'], {opacity: 0}, end);
    }
  });
  tl.set('#trBlack', {opacity: 0}, D.trailer.end);
  tl.to(['#barT', '#barB'], {height: 0, duration: 0.14, ease: 'power2.in'}, D.trailer.end - 0.12);
  tl.set('#cam', {filter: 'none', scale: 1.0}, D.trailer.end);

  /* ================= 2 · Hand + 3D-Logo ================= */
  const star = $('star');
  for (let i = 11; i >= 0; i--) {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('viewBox', '0 0 100 100');
    s.setAttribute('class', 'sl' + (i === 0 ? ' front' : ''));
    s.style.transform = 'translateZ(' + (-i * 1.6) + 'px)';
    s.innerHTML = '<path d="__STAR__"/>';
    star.appendChild(s);
  }
  const THROW = T.kamera - 0.86;
  tl.fromTo('#cam', {scale: 1.0}, {scale: 1.38, duration: 1.0, ease: 'power2.inOut'}, T.zoom);
  tl.fromTo('#star', {opacity: 0, scale: 0, y: 40}, {opacity: 1, scale: 1, y: 0, duration: 0.55, ease: 'expo.out'}, T.logo - 0.02);
  tl.fromTo('#starShadow', {opacity: 0, scale: 0.3}, {opacity: 1, scale: 1, duration: 0.5, ease: 'power2.out'}, T.logo);
  tl.fromTo('#star', {rotationY: -40}, {rotationY: 720, duration: Math.max(0.6, T.kamera - 0.31 - T.logo), ease: 'sine.inOut'}, T.logo);
  tl.to('#star', {rotationX: 16, duration: 0.5, ease: 'sine.inOut'}, T.d3 - 0.1);
  tl.to('#star', {y: -14, duration: 0.5, ease: 'sine.inOut', yoyo: true, repeat: 1}, T.nice - 0.1);
  tl.to('#cam', {scale: 1.0, duration: 0.55, ease: 'power2.inOut'}, THROW);
  tl.to('#starShadow', {opacity: 0, duration: 0.2}, THROW + 0.15);
  tl.to('#star', {x: WX - HX, y: WY - (HY - 86) - 6, rotationX: 0, duration: 0.5, ease: 'power2.inOut'}, THROW + 0.15);
  tl.to('#star', {x: W / 2 - HX, y: H / 2 - (HY - 86) - 40, scale: 7.5, duration: 0.19, ease: 'power3.in'}, T.kamera - 0.19);
  tl.set('#star', {opacity: 0}, T.kamera);
  tl.set('#flash', {opacity: 1}, T.kamera);
  tl.set('#flash', {opacity: 0}, T.kamera + 0.034);

  /* ================= 3 · Glassprung ueber die ganze Buehne ================= */
  const svgNS = 'http://www.w3.org/2000/svg';
  const crack = $('crack');
  const CX = 560, CY = 690, N = 17, rays = [], paths = [];
  for (let i = 0; i < N; i++) {
    let a = (i / N) * Math.PI * 2 + (rnd() - 0.5) * 0.25, x = CX, y = CY, d = 'M' + x + ' ' + y;
    const pts = [[x, y]];
    while (x > -40 && x < 1120 && y > -40 && y < 1960) {
      const step = 55 + rnd() * 110;
      a += (rnd() - 0.5) * 0.28;
      x += Math.cos(a) * step; y += Math.sin(a) * step;
      d += ' L' + x.toFixed(1) + ' ' + y.toFixed(1);
      pts.push([x, y]);
    }
    rays.push({d: d, pts: pts});
  }
  function addPath(d, w) {
    [['rgba(0,0,0,0.35)', w + 2.5], ['rgba(255,255,255,0.92)', w]].forEach(([c, sw]) => {
      const p = document.createElementNS(svgNS, 'path');
      p.setAttribute('d', d); p.setAttribute('stroke', c); p.setAttribute('stroke-width', sw);
      crack.appendChild(p); paths.push(p);
    });
  }
  rays.forEach(r => addPath(r.d, 2.2));
  [1, 2, 4].forEach(k => {
    for (let i = 0; i < N; i++) {
      const A = rays[i].pts, B = rays[(i + 1) % N].pts;
      if (A[k] && B[k] && rnd() > 0.2) {
        const mx = (A[k][0] + B[k][0]) / 2 + (rnd() - 0.5) * 30, my = (A[k][1] + B[k][1]) / 2 + (rnd() - 0.5) * 30;
        addPath('M' + A[k][0].toFixed(1) + ' ' + A[k][1].toFixed(1) + ' L' + mx.toFixed(1) + ' ' + my.toFixed(1) + ' L' + B[k][0].toFixed(1) + ' ' + B[k][1].toFixed(1), 1.5);
      }
    }
  });
  const ci = document.createElementNS(svgNS, 'circle');
  ci.setAttribute('cx', CX); ci.setAttribute('cy', CY); ci.setAttribute('r', 22); ci.setAttribute('fill', 'rgba(255,255,255,0.55)');
  crack.appendChild(ci);
  paths.forEach(p => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
  tl.set('#crack', {opacity: 1}, T.kamera);
  tl.to(paths, {strokeDashoffset: 0, duration: 0.16, ease: 'power2.out'}, T.kamera);
  const shards = $('shards');
  for (let i = 0; i < 12; i++) {
    const s = document.createElement('div');
    s.className = 'sh';
    const w = 26 + rnd() * 50, h = 26 + rnd() * 60;
    s.style.left = (CX - 120 + rnd() * 240) + 'px';
    s.style.top = (CY - 90 + rnd() * 180) + 'px';
    s.innerHTML = '<svg width="' + w + '" height="' + h + '" viewBox="0 0 10 10"><polygon points="0,' + (rnd() * 4).toFixed(1) + ' 10,' + (rnd() * 3).toFixed(1) + ' ' + (3 + rnd() * 5).toFixed(1) + ',10" fill="rgba(255,255,255,0.22)" stroke="rgba(255,255,255,0.9)" stroke-width="0.35"/></svg>';
    shards.appendChild(s);
    tl.set(s, {opacity: 1}, T.kamera + 0.04);
    tl.to(s, {opacity: 0, duration: 0.25, ease: 'power1.in'}, T.kamera + 1.25);
    tl.to(s, {y: 900 + rnd() * 500, x: (rnd() - 0.5) * 300, rotation: (rnd() - 0.5) * 540, duration: 1.1 + rnd() * 0.4, ease: 'power2.in'}, T.kamera + 0.06 + rnd() * 0.1);
  }
  tl.to('#crack', {opacity: 0, duration: 0.3, ease: 'power2.in'}, T.okay + 0.15);

  /* ================= 4 · Ebenen ================= */
  const txT = $('txTitle');
  C.ebene_titel.forEach((t, i) => {
    const d = document.createElement('div');
    d.textContent = t;
    if (i >= Math.ceil(C.ebene_titel.length / 2)) d.className = 'o';
    txT.appendChild(d);
  });
  tl.set('#stack', {opacity: 1}, T.zerlege - 0.1);
  tl.from('#txTitle div', {opacity: 0, y: 26, filter: 'blur(6px)', duration: 0.4, ease: 'power3.out', stagger: 0.14}, T.zerlege);
  tl.set(['#pBG', '#pME'], {opacity: 1}, T.ebenen - 0.12);
  tl.set('#vTop', {opacity: 0}, T.ebenen - 0.12);
  tl.to('#stack', {rotationY: -40, rotationX: 12, scale: 0.54, x: -95, y: 14, duration: 0.9, ease: 'power3.inOut'}, T.ebenen);
  tl.to('#pBG', {z: -330, x: -40, duration: 0.9, ease: 'power3.inOut'}, T.ebenen);
  tl.to('#pTX', {z: 330, x: 40, duration: 0.9, ease: 'power3.inOut'}, T.ebenen);
  tl.to('.pf', {opacity: 1, duration: 0.5, ease: 'power2.out'}, T.ebenen + 0.2);
  tl.fromTo('#panel', {opacity: 0, x: 40}, {opacity: 1, x: 0, duration: 0.45, ease: 'power3.out'}, T.hgrund - 0.3);
  [['#chipBG', '#rowBG', T.hgrund], ['#chipME', '#rowME', T.mich], ['#chipTX', '#rowTX', T.text]].forEach(([c, r, at], k) => {
    tl.fromTo(c, {opacity: 0, scale: 0.85}, {opacity: 1, scale: 1, duration: 0.3, ease: k === 1 ? 'expo.out' : 'power3.out'}, at - 0.04);
    tl.to(r + ' .hl', {opacity: 1, duration: 0.2}, at - 0.04);
    tl.to(r + ' .hl', {opacity: 0, duration: 0.25}, at + 0.5);
  });
  const eyeX = 800 + 12 + 8 + 12 - 6, eyeY = 96 + 14 + 18 + 10 + 50 + 25 - 4;
  tl.fromTo('#cursor', {opacity: 0, x: 0, y: 0}, {opacity: 1, duration: 0.2}, T.blend - 0.3);
  tl.to('#cursor', {x: eyeX - 640, y: eyeY - 470, duration: 0.5, ease: 'power3.inOut'}, T.blend - 0.25);
  tl.to('#cursor', {scale: 0.82, duration: 0.06, yoyo: true, repeat: 1}, T.aus - 0.08);
  tl.to('#rowME .hl', {opacity: 1, duration: 0.1}, T.aus - 0.06);
  tl.set('#rowME .eye .on', {opacity: 0}, T.aus - 0.05);
  tl.set('#rowME .eye .off', {opacity: 1}, T.aus - 0.05);
  tl.to('#pME', {opacity: 0, duration: 0.25, ease: 'power2.out'}, T.aus - 0.05);
  tl.fromTo('#hidTag', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: 0.3, ease: 'power3.out'}, T.aus + 0.08);
  const BACKT = T.zurueck - 0.08;
  tl.to('#cursor', {scale: 0.82, duration: 0.06, yoyo: true, repeat: 1}, BACKT);
  tl.set('#rowME .eye .on', {opacity: 1}, BACKT + 0.03);
  tl.set('#rowME .eye .off', {opacity: 0}, BACKT + 0.03);
  tl.to('#hidTag', {opacity: 0, duration: 0.15}, BACKT + 0.01);
  tl.to('#pME', {opacity: 1, duration: 0.2, ease: 'power2.out'}, BACKT + 0.03);
  tl.to('#rowME .hl', {opacity: 0, duration: 0.2}, BACKT + 0.15);
  tl.to(['#panel', '#cursor'], {opacity: 0, x: '+=30', duration: 0.3, ease: 'power2.in'}, BACKT + 0.17);
  tl.to(['.pf', '.chip', '#txTitle'], {opacity: 0, duration: 0.25, ease: 'power2.in'}, BACKT + 0.15);
  tl.to('#stack', {rotationY: 0, rotationX: 0, scale: 1, x: 0, y: 0, duration: 0.5, ease: 'power3.inOut'}, BACKT + 0.15);
  tl.to(['#pBG', '#pTX'], {z: 0, x: 0, duration: 0.5, ease: 'power3.inOut'}, BACKT + 0.15);
  tl.set('#vTop', {opacity: 1}, BACKT + 0.67);
  tl.set(['#pBG', '#pME'], {opacity: 0}, BACKT + 0.67);

  /* ================= 5 · Rahmen rechts, Slide links ================= */
  const S = 0.86, CARD = {x: 690, y: 48, w: 320, h: 491};
  const TX = CARD.x + CARD.w / 2 - PX * S, TY = 52;
  const cl = {l: (CARD.x - TX) / S, r: W - (CARD.x + CARD.w - TX) / S, t: Math.max(0, (CARD.y - TY) / S), b: H - (CARD.y + CARD.h - TY) / S};
  const ins = (a) => 'inset(' + (cl.t * a).toFixed(1) + 'px ' + (cl.r * a).toFixed(1) + 'px ' + (cl.b * a).toFixed(1) + 'px ' + (cl.l * a).toFixed(1) + 'px round ' + (21 * a).toFixed(1) + 'px)';
  tl.set('#cam', {transformOrigin: '0% 0%'}, T.rahmen - 0.1);
  tl.fromTo('#cam', {clipPath: ins(0), x: 0, y: 0, scale: 1}, {clipPath: ins(1), x: TX, y: TY, scale: S, duration: 0.7, ease: 'power3.inOut', immediateRender: false}, T.rahmen - 0.05);
  tl.fromTo('#cardFrame', {opacity: 0, scale: 0.97}, {opacity: 1, scale: 1, duration: 0.35, ease: 'power2.out'}, T.rahmen + 0.55);
  tl.from('#nameTag', {y: 16, opacity: 0, duration: 0.35, ease: 'power3.out'}, T.rahmen + 0.7);
  tl.fromTo('#kick', {opacity: 0, x: -20}, {opacity: 1, x: 0, duration: 0.35, ease: 'power3.out'}, T.links - 0.05);
  const headl = $('headl');
  D.head.forEach((w) => {
    const s = document.createElement('span');
    s.textContent = w.t;
    if (w.k) s.className = 'o';
    headl.appendChild(s);
    tl.fromTo(s, {opacity: 0, y: 16}, {opacity: 1, y: 0, duration: 0.22, ease: 'power3.out'}, w.s - 0.03);
  });
  const list = $('list');
  const EASES = ['power3.out', 'expo.out', 'power2.out'];
  C.liste.forEach((row, i) => {
    const li = document.createElement('div');
    li.className = 'li';
    li.innerHTML = '<div class="ck"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div><b>0' + (i + 1) + '</b><div></div>';
    const txt = li.lastChild;
    txt.appendChild(document.createTextNode(row[0]));
    const sub = document.createElement('i'); sub.textContent = row[1]; txt.appendChild(sub);
    list.appendChild(li);
    const at = D.list_at[i];
    tl.fromTo(li, {opacity: 0, x: -24}, {opacity: 1, x: 0, duration: 0.3, ease: EASES[i % 3]}, at);
    tl.from(li.querySelector('.ck'), {scale: 0, duration: 0.25, ease: 'power3.out'}, at + 0.1);
  });
  tl.to(['#slide', '#cardFrame'], {opacity: 0, duration: 0.25, ease: 'power2.in'}, T.vollbild - 0.12);
  tl.to('#cam', {clipPath: ins(0), x: 0, y: 0, scale: 1, duration: 0.6, ease: 'power3.inOut'}, T.vollbild - 0.05);
  tl.set('#cam', {clipPath: 'none'}, T.vollbild + 0.56);

  /* ================= 6 · Reels schweben + Karte auf den Kopf ================= */
  const R = D.reels;
  const BACK = [
    {x: PX - 320, y: 190, ry: 28, r: -8}, {x: PX - 170, y: 120, ry: 16, r: 5},
    {x: PX + 180, y: 115, ry: -16, r: 6}, {x: PX + 360, y: 190, ry: -28, r: -6},
  ];
  const FRONT = [{x: 110, y: 470, ry: 22, r: -12}, {x: 950, y: 440, ry: -24, r: 10}];
  const RISE = T.reels - 0.1, GONE = T.komm - 0.21, LAND = T.oh - 0.04;
  tl.set('#stack', {opacity: 1}, RISE - 0.1);
  tl.set('#pME', {opacity: 1}, RISE - 0.1);
  tl.set(['#pBG', '#pTX', '#pHID'], {opacity: 0}, RISE - 0.1);
  let ri = 0;
  [[BACK, '#reelsBack'], [FRONT, '#reelsFront']].forEach(([items, sel], g) => {
    const host = document.querySelector(sel);
    items.forEach((c, i) => {
      const el = document.createElement('div');
      el.className = 'rc';
      el.style.left = c.x + 'px'; el.style.top = c.y + 'px';
      el.style.backgroundImage = 'url(' + R[ri++ % R.length] + ')';
      if (g === 1) el.style.transform = 'scale(1.12)';
      host.appendChild(el);
      const at = RISE + (g * 4 + i) * 0.08;
      tl.fromTo(el, {opacity: 0, y: 380, rotationY: c.ry * 2, rotation: c.r * 2},
        {opacity: 1, y: 0, rotationY: c.ry, rotation: c.r, duration: 0.7, ease: 'expo.out'}, at);
      const len = GONE - at - 0.7;
      if (len > 0.5) tl.to(el, {y: (i % 2 ? -12 : 12), rotationY: c.ry * 0.7, duration: 0.9, ease: 'sine.inOut', yoyo: true, repeat: Math.max(0, Math.ceil(len / 0.9) - 1)}, at + 0.7);
      tl.to(el, {opacity: 0, y: '+=40', duration: 0.2, ease: 'power2.in'}, GONE);
    });
  });
  tl.fromTo('#drop', {opacity: 1, y: -560, x: -40, rotation: -34}, {opacity: 1, y: 0, x: 0, rotation: 12, duration: 0.42, ease: 'power2.in'}, LAND - 0.42);
  tl.to('#drop', {y: -22, rotation: 20, duration: 0.12, ease: 'power2.out'}, LAND);
  tl.to('#drop', {y: 0, rotation: 17, duration: 0.14, ease: 'power2.in'}, LAND + 0.12);
  const bonk = $('bonk');
  [-150, -115, -65, -30, 20].forEach((deg, i) => {
    const l = document.createElement('i');
    l.style.transform = 'rotate(' + deg + 'deg) translateX(' + (70 + (i % 2) * 10) + 'px)';
    bonk.appendChild(l);
    tl.fromTo(l, {opacity: 0, scaleX: 0.2}, {opacity: 1, scaleX: 1, duration: 0.1, ease: 'power2.out'}, LAND + 0.01);
    tl.to(l, {opacity: 0, duration: 0.2, ease: 'power1.in'}, LAND + 0.28);
  });
  tl.to('#drop', {opacity: 0, y: 60, rotation: 30, duration: 0.25, ease: 'power2.in'}, T.komm - 0.27);
  tl.set('#stack', {opacity: 0}, T.komm - 0.04);

  /* ================= 7 · CTA ================= */
  const ce = $('ctaEdit');
  ('„' + C.cta_wort + '“').split('').forEach((ch) => { const s = document.createElement('span'); s.textContent = ch; ce.appendChild(s); });
  ce.style.fontSize = Math.min(88, Math.round(300 / Math.max(3, (C.cta_wort.length + 2) * 0.62))) + 'px';
  tl.to('#ctaScrim', {opacity: 1, duration: 0.3, ease: 'power1.out'}, T.komm - 0.1);
  tl.fromTo('#ctaK', {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: 0.3, ease: 'power3.out'}, T.komm - 0.02);
  tl.to('#ctaBar', {scaleX: 1, duration: 0.32, ease: 'expo.out'}, T.edit - 0.12);
  tl.to('#ctaEdit span', {opacity: 1, duration: 0.08, stagger: 0.045, ease: 'none'}, T.edit - 0.02);
  tl.fromTo('#ctaBand', {opacity: 0, x: -20}, {opacity: 1, x: 0, duration: 0.3, ease: 'power2.out'}, T.kostenlose - 0.04);
  tl.fromTo('#guide', {opacity: 0, y: 30}, {opacity: 1, y: 0, duration: 0.45, ease: 'expo.out'}, T.karte - 0.08);
  const ring = $('ring');
  const RL = ring.getTotalLength();
  ring.style.strokeDasharray = RL; ring.style.strokeDashoffset = RL;
  tl.to(ring, {strokeDashoffset: 0, duration: 0.55, ease: 'power2.inOut'}, T.kreis - 0.25);

  /* ================= Untertitel ================= */
  const capHost = $('caps');
  D.caps.forEach((g) => {
    const el = document.createElement('div');
    el.className = 'cg';
    g.words.forEach((w) => {
      const s = document.createElement('span');
      s.textContent = w.t;
      if (w.k) s.className = 'k';
      el.appendChild(s);
      tl.fromTo(s, {opacity: 0, y: 6}, {opacity: 1, y: 0, duration: 0.07, ease: 'power1.out', immediateRender: false}, Math.max(0, w.s - 0.03));
    });
    capHost.appendChild(el);
    tl.set(el, {opacity: 1}, g.start);
    tl.set(el, {opacity: 0}, g.end);
  });

  tl.to({}, {duration: D.dur}, 0);
  window.__timelines = window.__timelines || {};
  window.__timelines['claude-video'] = tl;
})();
</script>
</body>
</html>
