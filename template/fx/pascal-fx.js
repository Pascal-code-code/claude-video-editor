/* pascal-fx.js: Pascals Reel-Effekte fuer HyperFrames (abgenommen am IMG_0444-Reel, 29.09.2026).
 *
 * Tiefen-Aufbau im HTML (von hinten nach vorn, alle in einem Container mit position:relative):
 *   .pfx-cam      > <video> (Rohschnitt, muted)       Kamera-Ebene, fuer Push-ins und Rahmen
 *   .pfx-back                                          Grafik HINTER der Person (Text, Karten)
 *   .pfx-person   > <video src="assets/person.webm">   Freisteller (edit: fx/matte.py)
 *   .pfx-front                                         Grafik VOR der Person
 *   .pfx-caps                                          Untertitel
 * Videos und <audio> muessen im HTML stehen (HyperFrames findet dynamisch erzeugte Medien nicht).
 * Alle Funktionen bauen DOM synchron und haengen Tweens an die uebergebene Timeline.
 * Koordinaten sind Pixel im jeweiligen Host-Container.
 */
(function () {
  const PFX = {};
  const SVGNS = 'http://www.w3.org/2000/svg';

  PFX.rng = function (seed) {
    let a = seed | 0;
    return function () {
      a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  };

  function el(tag, cls, parent, style) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (style) Object.assign(e.style, style);
    if (parent) parent.appendChild(e);
    return e;
  }
  PFX.el = el;
  const $ = (h) => (typeof h === 'string' ? document.querySelector(h) : h);

  /* Freisteller nur in bestimmten Zeitfenstern zeigen (ausserhalb ist person.webm transparent,
     aber so bleibt die Absicht im Code lesbar). spans: [[a,b],...] */
  PFX.personSpans = function (tl, person, spans) {
    gsap.set($(person), {opacity: 0});
    spans.forEach(([a, b]) => { tl.set($(person), {opacity: 1}, a); tl.set($(person), {opacity: 0}, b); });
  };

  /* Text hinter der Person. lines: [{t, size, color, weight, font, italic, tracking}]
     opts: {x, y, w, align:'left'|'center'|'right', at, out, stagger, gap} */
  PFX.textBehind = function (tl, host, lines, o) {
    const box = el('div', 'pfx-tb', $(host), {left: o.x + 'px', top: o.y + 'px', width: (o.w || 900) + 'px', textAlign: o.align || 'center'});
    const els = lines.map((L) => {
      const d = el('div', 'pfx-tb-line', box, {
        fontSize: (L.size || 160) + 'px', color: L.color || '#fff', fontWeight: L.weight || 900,
        fontFamily: L.font || 'Inter, system-ui, sans-serif', fontStyle: L.italic ? 'italic' : 'normal',
        letterSpacing: (L.tracking != null ? L.tracking : -0.03) + 'em', marginTop: (o.gap || 0) + 'px',
      });
      d.textContent = L.t;
      return d;
    });
    const st = o.stagger != null ? o.stagger : 0.12;
    els.forEach((d, i) => {
      const at = Array.isArray(o.at) ? o.at[i] : o.at + i * st;
      tl.fromTo(d, {opacity: 0, y: 40, filter: 'blur(10px)'}, {opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.45, ease: 'power3.out', immediateRender: true}, at);
    });
    if (o.out != null) tl.to(els, {opacity: 0, y: -20, duration: 0.3, ease: 'power2.in', stagger: 0.04}, o.out);
    return box;
  };

  /* Karten (Reel-Cover, Screenshots) steigen auf und schweben. items: [{x,y,w,h,img,ry,r,scale}]
     x/y = Mittelpunkt. opts: {at, stagger, until, float, from:'below'|'above'} */
  PFX.cards = function (tl, host, items, o) {
    const hostEl = $(host);
    hostEl.style.perspective = hostEl.style.perspective || '1200px';
    const out = [];
    items.forEach((c, i) => {
      const w = c.w || 150, h = c.h || Math.round((c.w || 150) * 16 / 9);
      const e = el('div', 'pfx-card', hostEl, {left: (c.x - w / 2) + 'px', top: (c.y - h / 2) + 'px', width: w + 'px', height: h + 'px',
        backgroundImage: c.img ? 'url(' + c.img + ')' : 'none'});
      if (c.html) e.innerHTML = c.html;
      const at = o.at + i * (o.stagger != null ? o.stagger : 0.08);
      const dy = o.from === 'above' ? -420 : 420;
      tl.fromTo(e, {opacity: 0, y: dy, rotationY: (c.ry || 0) * 2, rotation: (c.r || 0) * 2, scale: c.scale || 1},
        {opacity: 1, y: 0, rotationY: c.ry || 0, rotation: c.r || 0, scale: c.scale || 1, duration: 0.7, ease: 'expo.out', immediateRender: true}, at);
      if (o.float !== false && o.until) {
        const len = o.until - at - 0.7;
        if (len > 0.4) {
          const cyc = 0.9, rep = Math.max(0, Math.ceil(len / cyc) - 1);
          tl.to(e, {y: i % 2 ? -12 : 12, rotationY: (c.ry || 0) * 0.7, duration: cyc, ease: 'sine.inOut', yoyo: true, repeat: rep}, at + 0.7);
        }
      }
      if (o.until) tl.to(e, {opacity: 0, y: '+=40', duration: 0.2, ease: 'power2.in'}, o.until);
      out.push(e);
    });
    return out;
  };

  /* Karte faellt von oben auf den Kopf und ragt ueber den Rand. opts: {img, x, y (Mittelpunkt bei Landung),
     w, h, land, rot, out, bonkY (Kopfoberkante)} */
  PFX.drop = function (tl, host, o) {
    const w = o.w || 150, h = o.h || 267;
    const e = el('div', 'pfx-card pfx-drop', $(host), {left: (o.x - w / 2) + 'px', top: (o.y - h / 2) + 'px', width: w + 'px', height: h + 'px',
      backgroundImage: 'url(' + o.img + ')'});
    const rot = o.rot != null ? o.rot : 12;
    tl.fromTo(e, {opacity: 1, y: -700, x: -40, rotation: -34}, {opacity: 1, y: 0, x: 0, rotation: rot, duration: 0.42, ease: 'power2.in', immediateRender: false}, o.land - 0.42);
    tl.set(e, {opacity: 0}, 0);
    tl.set(e, {opacity: 1}, o.land - 0.42);
    tl.to(e, {y: -22, rotation: rot + 8, duration: 0.12, ease: 'power2.out'}, o.land);
    tl.to(e, {y: 0, rotation: rot + 5, duration: 0.14, ease: 'power2.in'}, o.land + 0.12);
    const bonk = el('div', 'pfx-bonk', $(host), {left: o.x + 'px', top: (o.bonkY != null ? o.bonkY : o.y + h / 2 - 20) + 'px'});
    [-150, -115, -65, -30, 20].forEach((deg, i) => {
      const l = el('i', '', bonk);
      l.style.transform = 'rotate(' + deg + 'deg) translateX(' + (70 + (i % 2) * 10) + 'px)';
      tl.fromTo(l, {opacity: 0, scaleX: 0.2}, {opacity: 1, scaleX: 1, duration: 0.1, ease: 'power2.out', immediateRender: true}, o.land + 0.01);
      tl.to(l, {opacity: 0, duration: 0.2, ease: 'power1.in'}, o.land + 0.28);
    });
    if (o.out != null) tl.to(e, {opacity: 0, y: 60, rotation: rot + 18, duration: 0.25, ease: 'power2.in'}, o.out);
    return e;
  };

  /* 3D-Logo aus gestapelten SVG-Scheiben. Liefert das Element; Drehen/Fliegen per tl.
     opts: {path (SVG-Pfad, viewBox 0 0 100 100), x, y (links oben), size, color, depth, slices} */
  PFX.logo3D = function (host, o) {
    const wrap = el('div', 'pfx-logo-wrap', $(host));
    const star = el('div', 'pfx-logo', wrap, {left: o.x + 'px', top: o.y + 'px', width: (o.size || 150) + 'px', height: (o.size || 150) + 'px'});
    const n = o.slices || 12;
    for (let i = n - 1; i >= 0; i--) {
      const s = document.createElementNS(SVGNS, 'svg');
      s.setAttribute('viewBox', '0 0 100 100');
      s.setAttribute('class', 'pfx-slice' + (i === 0 ? ' front' : ''));
      s.style.transform = 'translateZ(' + (-i * (o.step || 1.6)) + 'px)';
      s.innerHTML = '<path fill="' + (i === 0 ? (o.color || '#D97757') : (o.depth || '#9c4a31')) + '" d="' + o.path + '"/>';
      star.appendChild(s);
    }
    gsap.set(star, {opacity: 0});
    return star;
  };

  /* Weissblitz fuer genau einen Frame. */
  PFX.flash = function (tl, host, at) {
    const f = el('div', 'pfx-flash', $(host));
    tl.set(f, {opacity: 1}, at);
    tl.set(f, {opacity: 0}, at + 0.034);
    return f;
  };

  /* Glassprung + fallende Splitter. host: Container ueber allem (z. B. Buehne).
     opts: {w, h, cx, cy, at, out, seed, rays, fallTo} */
  PFX.crack = function (tl, host, o) {
    const rnd = PFX.rng(o.seed || 444);
    const svg = document.createElementNS(SVGNS, 'svg');
    svg.setAttribute('class', 'pfx-crack');
    svg.setAttribute('viewBox', '0 0 ' + o.w + ' ' + o.h);
    svg.style.width = o.w + 'px'; svg.style.height = o.h + 'px';
    $(host).appendChild(svg);
    const N = o.rays || 17, rays = [], paths = [];
    for (let i = 0; i < N; i++) {
      let a = (i / N) * Math.PI * 2 + (rnd() - 0.5) * 0.25, x = o.cx, y = o.cy, d = 'M' + x + ' ' + y;
      const pts = [[x, y]];
      while (x > -40 && x < o.w + 40 && y > -40 && y < o.h + 40) {
        const step = 55 + rnd() * 110;
        a += (rnd() - 0.5) * 0.28;
        x += Math.cos(a) * step; y += Math.sin(a) * step;
        d += ' L' + x.toFixed(1) + ' ' + y.toFixed(1);
        pts.push([x, y]);
      }
      rays.push({d, pts});
    }
    const add = (d, w) => {
      [['rgba(0,0,0,0.35)', w + 2.5], ['rgba(255,255,255,0.92)', w]].forEach(([c, sw]) => {
        const p = document.createElementNS(SVGNS, 'path');
        p.setAttribute('d', d); p.setAttribute('stroke', c); p.setAttribute('stroke-width', sw);
        svg.appendChild(p); paths.push(p);
      });
    };
    rays.forEach((r) => add(r.d, 2.2));
    [1, 2, 4].forEach((k) => {
      for (let i = 0; i < N; i++) {
        const A = rays[i].pts, B = rays[(i + 1) % N].pts;
        if (A[k] && B[k] && rnd() > 0.2) {
          const mx = (A[k][0] + B[k][0]) / 2 + (rnd() - 0.5) * 30, my = (A[k][1] + B[k][1]) / 2 + (rnd() - 0.5) * 30;
          add('M' + A[k][0].toFixed(1) + ' ' + A[k][1].toFixed(1) + ' L' + mx.toFixed(1) + ' ' + my.toFixed(1) + ' L' + B[k][0].toFixed(1) + ' ' + B[k][1].toFixed(1), 1.5);
        }
      }
    });
    const ci = document.createElementNS(SVGNS, 'circle');
    ci.setAttribute('cx', o.cx); ci.setAttribute('cy', o.cy); ci.setAttribute('r', 22); ci.setAttribute('fill', 'rgba(255,255,255,0.55)');
    svg.appendChild(ci);
    paths.forEach((p) => { const L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
    tl.set(svg, {opacity: 1}, o.at);
    tl.to(paths, {strokeDashoffset: 0, duration: 0.16, ease: 'power2.out'}, o.at);
    const shards = el('div', 'pfx-shards', $(host));
    for (let i = 0; i < 12; i++) {
      const s = el('div', 'pfx-shard', shards, {left: (o.cx - 120 + rnd() * 240) + 'px', top: (o.cy - 90 + rnd() * 180) + 'px'});
      const w = 26 + rnd() * 50, h = 26 + rnd() * 60;
      s.innerHTML = '<svg width="' + w + '" height="' + h + '" viewBox="0 0 10 10"><polygon points="0,' + (rnd() * 4).toFixed(1) + ' 10,' + (rnd() * 3).toFixed(1) + ' ' + (3 + rnd() * 5).toFixed(1) + ',10" fill="rgba(255,255,255,0.22)" stroke="rgba(255,255,255,0.9)" stroke-width="0.35"/></svg>';
      tl.set(s, {opacity: 1}, o.at + 0.04);
      tl.to(s, {y: (o.fallTo || 900) + rnd() * 500, x: (rnd() - 0.5) * 300, rotation: (rnd() - 0.5) * 540, duration: 1.1 + rnd() * 0.4, ease: 'power2.in'}, o.at + 0.06 + rnd() * 0.1);
      tl.to(s, {opacity: 0, duration: 0.25, ease: 'power1.in'}, o.at + 1.25);
    }
    tl.to(svg, {opacity: 0, duration: 0.3, ease: 'power2.in'}, o.out != null ? o.out : o.at + 0.7);
    return svg;
  };

  /* Label-Chip "01 EBENE Name". opts: {num, kicker, name, x, y, at} */
  PFX.chip = function (tl, host, o) {
    const c = el('div', 'pfx-chip', $(host), {left: o.x + 'px', top: o.y + 'px'});
    c.innerHTML = (o.num ? '<b>' + o.num + '</b>' : '') + (o.kicker ? '<i>' + o.kicker + '</i>' : '') + '<span>' + o.name + '</span>';
    if (o.at != null) tl.fromTo(c, {opacity: 0, scale: 0.85}, {opacity: 1, scale: 1, duration: 0.3, ease: 'power3.out', immediateRender: true}, o.at);
    if (o.out != null) tl.to(c, {opacity: 0, duration: 0.2}, o.out);
    return c;
  };

  /* Bild in 3D in Ebenen auffaechern und wieder zusammenfahren.
     planes: [{el, z, x}] im Stack; opts: {stack, at, back, view:{rotationY,rotationX,scale,x,y}, dur} */
  PFX.explode = function (tl, o) {
    const v = Object.assign({rotationY: -40, rotationX: 12, scale: 0.54, x: -95, y: 14}, o.view || {});
    const d = o.dur || 0.9;
    tl.to($(o.stack), Object.assign({duration: d, ease: 'power3.inOut'}, v), o.at);
    o.planes.forEach((p) => tl.to($(p.el), {z: p.z || 0, x: p.x || 0, duration: d, ease: 'power3.inOut'}, o.at));
    if (o.back != null) {
      tl.to($(o.stack), {rotationY: 0, rotationX: 0, scale: 1, x: 0, y: 0, duration: 0.5, ease: 'power3.inOut'}, o.back);
      o.planes.forEach((p) => tl.to($(p.el), {z: 0, x: 0, duration: 0.5, ease: 'power3.inOut'}, o.back));
    }
  };

  /* Bild zur Karte schrumpfen (clip-path im lokalen Raum + scale/translate) und zurueck.
     opts: {cam, W, H, card:{x,y,w,h}, S, TX, TY, at, back, radius} */
  PFX.frameCard = function (tl, o) {
    const cl = {l: (o.card.x - o.TX) / o.S, r: o.W - (o.card.x + o.card.w - o.TX) / o.S,
      t: Math.max(0, (o.card.y - o.TY) / o.S), b: o.H - (o.card.y + o.card.h - o.TY) / o.S};
    const r = o.radius || 21;
    const ins = (a) => 'inset(' + (cl.t * a).toFixed(1) + 'px ' + (cl.r * a).toFixed(1) + 'px ' + (cl.b * a).toFixed(1) + 'px ' + (cl.l * a).toFixed(1) + 'px round ' + (r * a).toFixed(1) + 'px)';
    tl.set($(o.cam), {transformOrigin: '0% 0%'}, o.at - 0.05);
    tl.fromTo($(o.cam), {clipPath: ins(0), x: 0, y: 0, scale: 1}, {clipPath: ins(1), x: o.TX, y: o.TY, scale: o.S, duration: 0.7, ease: 'power3.inOut', immediateRender: false}, o.at);
    if (o.back != null) {
      tl.to($(o.cam), {clipPath: ins(0), x: 0, y: 0, scale: 1, duration: 0.6, ease: 'power3.inOut'}, o.back);
      tl.set($(o.cam), {clipPath: 'none'}, o.back + 0.61);
    }
  };

  /* Push-in auf einen Punkt. opts: {origin:'56% 72%', scale, at, dur, back, backDur} */
  PFX.pushIn = function (tl, cam, o) {
    tl.set($(cam), {transformOrigin: o.origin || '50% 40%'}, o.at - 0.01);
    tl.fromTo($(cam), {scale: 1}, {scale: o.scale || 1.35, duration: o.dur || 1.0, ease: 'power2.inOut', immediateRender: false}, o.at);
    if (o.back != null) tl.to($(cam), {scale: 1, duration: o.backDur || 0.55, ease: 'power2.inOut'}, o.back);
  };

  /* Untertitel: groups [{start,end,words:[{t,s,k}]}] aus fx/pfx.py caption_groups(). */
  PFX.captions = function (tl, host, groups) {
    groups.forEach((g) => {
      const e = el('div', 'pfx-cg', $(host));
      g.words.forEach((w) => {
        const s = el('span', w.k ? 'k' : '', e);
        s.textContent = w.t;
        tl.fromTo(s, {opacity: 0, y: 6}, {opacity: 1, y: 0, duration: 0.07, ease: 'power1.out', immediateRender: false}, Math.max(0, w.s - 0.03));
      });
      e.querySelectorAll('span').forEach((s) => { s.style.opacity = 0; });
      tl.set(e, {opacity: 1}, g.start);
      tl.set(e, {opacity: 0}, g.end);
    });
  };

  window.PFX = PFX;
})();
