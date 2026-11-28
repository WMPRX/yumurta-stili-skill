// sets.js — painted night sets (analiz/mekan.md). Each set paints a BACKDROP once (cached, then blurred per shot kind)
// and a sharp FOREGROUND (table / ledge) that sits between a character's body and arms.
// Coordinates: frame fractions (u across, v down) of the two-shot framing; the backdrop covers u,v in [-0.3, 1.3].
// Paint in ordinary colours: the grade (post.js) turns everything sepia. Warm = lamps and lit windows, cool = night.
import { rrect, blob, fillStroke, shade, mix, rgba, rng, canvas } from './util.js';
import { LINE } from './chars.js';

export const PAD = .3, SPAN = 1 + 2 * PAD;          // backdrop covers [-PAD, 1+PAD] in u and v

function painter(c) {                                 // helpers in frame fractions for a backdrop canvas
  const g = c.getContext('2d'), X = u => (u + PAD) / SPAN * c.width, Y = v => (v + PAD) / SPAN * c.height, S = d => d / SPAN * c.width;
  return { g, X, Y, S, w: c.width, h: c.height };
}
function lw(P, px) { return px * P.w / SPAN / 1080; }  // a line width given in 1080-wide frame px

// ------------------------------------------------------------------------------------------------ shared pieces
function nightCity(P, u0, v0, u1, v1, seed = 3, opts = {}) {
  const { g, X, Y, S } = P, R = rng(seed);
  g.save(); g.beginPath(); g.rect(X(u0), Y(v0), X(u1) - X(u0), Y(v1) - Y(v0)); g.clip();
  const sky = g.createLinearGradient(0, Y(v0), 0, Y(v1)); sky.addColorStop(0, '#1b2236'); sky.addColorStop(1, '#2e3346');
  g.fillStyle = sky; g.fillRect(X(u0), Y(v0), X(u1) - X(u0), Y(v1) - Y(v0));
  if (opts.moon !== false) { g.beginPath(); g.arc(X(u0 + (u1 - u0) * .22), Y(v0 + (v1 - v0) * .16), S(.035), 0, 7); g.fillStyle = '#efe6cf'; g.fill(); }
  for (let layer = 0; layer < 2; layer++) {
    let u = u0 - .02;
    while (u < u1) {
      const bw = .1 + R() * .14, top = v0 + (v1 - v0) * (layer ? .28 + R() * .25 : .12 + R() * .2);
      g.fillStyle = layer ? '#3a3036' : '#2b2a36'; g.fillRect(X(u), Y(top), S(bw), Y(v1) - Y(top) + 2);
      for (let wy = top + .025; wy < v1 - .02; wy += .05) for (let wx = u + .015; wx < u + bw - .03; wx += .04) {
        const on = R() < (layer ? .42 : .25);
        g.fillStyle = on ? (R() < .5 ? '#f2c47a' : '#e9a95c') : '#1e1c26'; g.fillRect(X(wx), Y(wy), S(.022), S(.03));
        if (on && R() < .3) { g.fillStyle = '#3b2a22'; g.beginPath(); g.arc(X(wx + .011), Y(wy + .016), S(.006), 0, 7); g.fill(); g.fillRect(X(wx + .004), Y(wy + .021), S(.014), S(.012)); }
      }
      u += bw + .01;
    }
  }
  g.restore();
}
function silhouette(P, u, v, s, col = '#3b2a22') {      // a person in a lit window: head + shoulders
  const { g, X, Y, S } = P;
  g.fillStyle = col; g.beginPath(); g.arc(X(u), Y(v), S(.018 * s), 0, 7); g.fill();
  g.beginPath(); g.ellipse(X(u), Y(v + .05 * s), S(.032 * s), S(.032 * s), 0, Math.PI, 0); g.fill(); g.fillRect(X(u - .032 * s), Y(v + .05 * s), S(.064 * s), S(.04 * s));
}
function bentwoodChair(P, u, v, s) {
  const { g, X, Y, S } = P;
  g.strokeStyle = '#3a2217'; g.lineWidth = S(.012 * s); g.lineCap = 'round';
  g.beginPath(); g.ellipse(X(u), Y(v), S(.07 * s), S(.09 * s), 0, Math.PI, 0); g.stroke();
  g.beginPath(); g.ellipse(X(u), Y(v + .005), S(.045 * s), S(.06 * s), 0, Math.PI, 0); g.stroke();
  g.beginPath(); g.moveTo(X(u - .07 * s), Y(v)); g.lineTo(X(u - .07 * s), Y(v + .14 * s)); g.moveTo(X(u + .07 * s), Y(v)); g.lineTo(X(u + .07 * s), Y(v + .14 * s)); g.stroke();
}
function frame(P, u, v, w, h, inner) {
  const { g, X, Y, S } = P;
  rrect(g, X(u), Y(v), S(w), S(h), S(.004)); fillStroke(g, '#5a3b25', LINE, lw(P, 3));
  g.fillStyle = inner || '#a99476'; g.fillRect(X(u + .012), Y(v + .012), S(w - .024), S(h - .024) * (P.h / P.w) * (P.w / P.h));
}
export function teaGlass(g, x, y, s, k = 1, full = .8) {   // tulip tea glass on a saucer; (x,y) = saucer centre, s = px per glass height
  const L = LINE;
  g.save(); g.translate(x, y);
  g.beginPath(); g.ellipse(0, 0, s * .62, s * .16, 0, 0, 7); fillStroke(g, '#d9cdb8', L, 2.4 * k);
  g.beginPath(); g.ellipse(0, -s * .02, s * .38, s * .09, 0, 0, 7); g.strokeStyle = rgba(L, .35); g.lineWidth = 1.6 * k; g.stroke();
  const P2 = [[-.17, -.05], [-.22, -.3], [-.13, -.55], [-.21, -.95], [.21, -.95], [.13, -.55], [.22, -.3], [.17, -.05]].map(([a, b]) => [a * s, b * s]);
  g.beginPath(); g.moveTo(P2[0][0], P2[0][1]);
  g.bezierCurveTo(-.25 * s, -.2 * s, -.1 * s, -.5 * s, -.12 * s, -.58 * s); g.bezierCurveTo(-.14 * s, -.7 * s, -.24 * s, -.85 * s, -.22 * s, -.98 * s);
  g.lineTo(.22 * s, -.98 * s); g.bezierCurveTo(.24 * s, -.85 * s, .14 * s, -.7 * s, .12 * s, -.58 * s); g.bezierCurveTo(.1 * s, -.5 * s, .25 * s, -.2 * s, .17 * s, -.05 * s); g.closePath();
  g.save(); g.clip();
  g.fillStyle = 'rgba(230,220,205,.35)'; g.fillRect(-s, -s * 1.2, 2 * s, 1.3 * s);
  g.fillStyle = '#9c4a22'; g.fillRect(-s, -s * (.05 + .9 * full), 2 * s, s * .9 * full + s * .05);
  g.fillStyle = 'rgba(255,240,220,.35)'; g.fillRect(-s * .12, -s * .9, s * .05, s * .8);
  g.restore();
  g.strokeStyle = L; g.lineWidth = 2.6 * k; g.stroke();
  g.beginPath(); g.ellipse(0, -.98 * s, .22 * s, .045 * s, 0, 0, 7); g.strokeStyle = L; g.lineWidth = 2 * k; g.stroke();
  g.restore();
}
function tableTop(g, W, H, v, k, cloth = '#cdbfa6') {      // round table seen from the front, top edge at v
  const y = v * H, L = LINE;
  g.beginPath(); g.ellipse(W * .5, y + H * .06, W * .62, H * .07, 0, 0, 7); fillStroke(g, cloth, L, 4 * k);
  const X0 = -W * .3, XW = W * 1.6;                       // wide enough for the 'genis' framing (scaled to .66)
  g.fillStyle = shade(cloth, .78); g.fillRect(X0, y + H * .06, XW, H);
  g.beginPath(); g.moveTo(X0, y + H * .06); g.lineTo(X0 + XW, y + H * .06); g.strokeStyle = L; g.lineWidth = 4 * k; g.stroke();
  // scalloped cloth edge
  g.fillStyle = shade(cloth, .9);
  for (let x = X0; x < X0 + XW; x += 60 * k) { g.beginPath(); g.arc(x, y + H * .135, 30 * k, 0, Math.PI); g.fill(); g.strokeStyle = rgba(L, .5); g.lineWidth = 2 * k; g.stroke(); }
  g.fillStyle = '#2a1a12'; g.fillRect(X0, y + H * .135 + 30 * k, XW, H);
}

// ------------------------------------------------------------------------------------------------ sets
export const SETS = {
  kafe: {
    fx: 'toz',
    lights: [{ u: .5, v: .17, r: .2, col: '#ffcf86', a: .55 }],
    back(c) {
      const P = painter(c), { g, X, Y, S } = P;
      g.fillStyle = '#3d4a4a'; g.fillRect(0, 0, P.w, P.h);                                   // cool green wallpaper
      for (let u = -.3; u < 1.3; u += .05) { g.fillStyle = 'rgba(20,30,30,.18)'; g.fillRect(X(u), 0, S(.012), P.h); }
      nightCity(P, .08, -.08, .92, .56, 7);
      // window frame + mullions
      g.strokeStyle = '#4a2e1e'; g.lineWidth = S(.025);
      g.strokeRect(X(.08), Y(-.08), X(.92) - X(.08), Y(.56) - Y(-.08));
      g.lineWidth = S(.012); for (const u of [.36, .64]) { g.beginPath(); g.moveTo(X(u), Y(-.08)); g.lineTo(X(u), Y(.56)); g.stroke(); }
      g.beginPath(); g.moveTo(X(.08), Y(.2)); g.lineTo(X(.92), Y(.2)); g.stroke();
      g.strokeStyle = LINE; g.lineWidth = lw(P, 3); g.strokeRect(X(.065), Y(-.095), X(.935) - X(.065), Y(.575) - Y(-.095));
      // reflections on glass
      g.fillStyle = 'rgba(255,255,255,.05)'; g.beginPath(); g.moveTo(X(.12), Y(.5)); g.lineTo(X(.3), Y(-.05)); g.lineTo(X(.36), Y(-.05)); g.lineTo(X(.18), Y(.5)); g.fill();
      // wood panelling
      g.fillStyle = '#4a2c1c'; g.fillRect(0, Y(.6), P.w, P.h);
      g.fillStyle = '#5a3824'; g.fillRect(0, Y(.6), P.w, S(.02));
      for (let u = -.3; u < 1.3; u += .2) { rrect(g, X(u + .02), Y(.65), S(.16), S(.25), S(.01)); fillStroke(g, '#53321f', 'rgba(25,12,6,.6)', lw(P, 2)); }
      // pendant lamp
      g.strokeStyle = '#1f140e'; g.lineWidth = lw(P, 3); g.beginPath(); g.moveTo(X(.5), Y(-.3)); g.lineTo(X(.5), Y(.1)); g.stroke();
      g.beginPath(); g.moveTo(X(.42), Y(.16)); g.quadraticCurveTo(X(.5), Y(.05), X(.58), Y(.16)); g.closePath(); fillStroke(g, '#6b4a2a', LINE, lw(P, 3));
      g.beginPath(); g.ellipse(X(.5), Y(.16), S(.08), S(.012), 0, 0, 7); g.fillStyle = '#fff1c8'; g.fill();
      // picture frames
      frame(P, -.22, .08, .2, .26, '#7b6a55'); frame(P, 1.02, .1, .18, .22, '#8a7860');
      bentwoodChair(P, .3, .45, 1.2); bentwoodChair(P, .7, .45, 1.2);
    },
    fore(g, W, H, k, kind) {
      if (kind === 'tek' || kind === 'yakin') return;     // singles are framed above the table
      tableTop(g, W, H, .79, k);
      teaGlass(g, W * .3, H * .865, H * .085, k); teaGlass(g, W * .7, H * .865, H * .085, k, .55);
      // sugar bowl
      g.beginPath(); g.ellipse(W * .5, H * .87, W * .05, H * .012, 0, 0, 7); fillStroke(g, '#cfc3ad', LINE, 2.4 * k);
      g.beginPath(); g.moveTo(W * .455, H * .87); g.bezierCurveTo(W * .455, H * .83, W * .545, H * .83, W * .545, H * .87); fillStroke(g, 'rgba(230,222,208,.6)', LINE, 2.4 * k);
    },
  },

  sokak: {
    fx: 'kar',
    lights: [{ u: .9, v: .02, r: .18, col: '#ffd391', a: .6, beam: { to: [.62, .9], w: .45 } }],
    back(c) {
      const P = painter(c), { g, X, Y, S } = P, R = rng(11);
      g.fillStyle = '#1c2030'; g.fillRect(0, 0, P.w, P.h);
      // apartment facade
      g.fillStyle = '#4a2f26'; g.fillRect(X(-.25), Y(-.3), X(1.25) - X(-.25), Y(.9) - Y(-.3));
      for (let v = -.3; v < .9; v += .018) { g.fillStyle = 'rgba(20,10,6,.12)'; g.fillRect(X(-.25), Y(v), X(1.25) - X(-.25), S(.002)); }
      for (let row = 0; row < 5; row++) for (let col = 0; col < 6; col++) {
        const u = -.2 + col * .25, v = -.25 + row * .24, on = R() < .45;
        g.fillStyle = '#5c3b2d'; g.fillRect(X(u - .015), Y(v - .015), S(.15), S(.2));
        g.fillStyle = on ? (R() < .5 ? '#f0bd70' : '#e8a35a') : '#191822'; g.fillRect(X(u), Y(v), S(.12), S(.16));
        if (on) { const gl = g.createRadialGradient(X(u + .06), Y(v + .08), 0, X(u + .06), Y(v + .08), S(.12)); gl.addColorStop(0, 'rgba(255,200,120,.25)'); gl.addColorStop(1, 'rgba(255,200,120,0)'); g.fillStyle = gl; g.fillRect(X(u - .1), Y(v - .1), S(.32), S(.36)); }
        if (on && R() < .5) silhouette(P, u + .03 + R() * .06, v + .07, 1.3);
        g.strokeStyle = '#2b1a14'; g.lineWidth = S(.008); g.strokeRect(X(u), Y(v), S(.12), S(.16)); g.beginPath(); g.moveTo(X(u + .06), Y(v)); g.lineTo(X(u + .06), Y(v + .16)); g.moveTo(X(u), Y(v + .06)); g.lineTo(X(u + .12), Y(v + .06)); g.stroke();
        g.fillStyle = '#e9e4dc'; g.fillRect(X(u - .02), Y(v + .16), S(.16), S(.012));       // snow on the sill
        if (row === 2 && col % 2) { g.strokeStyle = '#1e1410'; g.lineWidth = S(.006); for (let i = 0; i < 9; i++) { g.beginPath(); g.moveTo(X(u - .02 + i * .02), Y(v + .17)); g.lineTo(X(u - .02 + i * .02), Y(v + .24)); g.stroke(); } g.fillRect(X(u - .03), Y(v + .17), S(.18), S(.008)); }
      }
      // street lamp post
      g.fillStyle = '#1b130f'; g.fillRect(X(.95), Y(-.05), S(.012), Y(1.2) - Y(-.05));
      g.beginPath(); g.moveTo(X(.86), Y(.02)); g.lineTo(X(.94), Y(.02)); g.lineTo(X(.92), Y(-.04)); g.lineTo(X(.88), Y(-.04)); g.closePath(); fillStroke(g, '#2a1d15');
      g.fillStyle = '#fff0c4'; g.fillRect(X(.875), Y(.02), S(.05), S(.008));
    },
    fore(g, W, H, k, kind) {
      if (kind === 'tek' || kind === 'yakin') return;
      const y = H * .79, X0 = -W * .3, XW = W * 1.6;
      g.fillStyle = '#5a3a2c'; g.fillRect(X0, y, XW, H);
      for (let r = 0; r < 6; r++) for (let x = X0 + (r % 2) * -40 * k; x < X0 + XW; x += 80 * k) { g.strokeStyle = 'rgba(30,15,8,.55)'; g.lineWidth = 2 * k; g.strokeRect(x, y + 30 * k + r * 36 * k, 80 * k, 36 * k); }
      g.beginPath(); g.moveTo(X0, y + 8 * k);
      for (let x = X0; x < X0 + XW; x += 34 * k) g.quadraticCurveTo(x + 17 * k, y - 14 * k - ((Math.abs(x) * 7) % 9) * k, x + 34 * k, y + 4 * k);
      g.lineTo(X0 + XW, y + 34 * k); g.lineTo(X0, y + 34 * k); g.closePath(); fillStroke(g, '#ece7df', LINE, 3 * k);
    },
  },

  oda: {
    fx: 'toz',
    lights: [{ u: .9, v: .3, r: .22, col: '#ffcf86', a: .6 }],
    back(c) {
      const P = painter(c), { g, X, Y, S } = P;
      g.fillStyle = '#5b4436'; g.fillRect(0, 0, P.w, P.h);
      // damask wallpaper: light motifs with thin dark outlines
      for (let v = -.3; v < .7; v += .12) for (let u = -.3; u < 1.3; u += .1) {
        const x = X(u + ((Math.round(v * 100) / 12) % 2) * .05), y = Y(v);
        g.beginPath(); g.ellipse(x, y, S(.018), S(.032), 0, 0, 7); fillStroke(g, '#6c5444', 'rgba(35,20,12,.35)', lw(P, 1.4));
      }
      // window with rain (right of centre)
      nightCity(P, .52, -.1, .82, .3, 5, { moon: false });
      g.strokeStyle = '#3e2618'; g.lineWidth = S(.02); g.strokeRect(X(.52), Y(-.1), S(.3), Y(.3) - Y(-.1));
      g.lineWidth = S(.008); g.beginPath(); g.moveTo(X(.67), Y(-.1)); g.lineTo(X(.67), Y(.3)); g.stroke();
      // curtains
      for (const [u, d] of [[.44, 1], [.84, -1]]) { g.fillStyle = '#6e2f28'; g.fillRect(X(u), Y(-.3), S(.1), Y(.6) - Y(-.3)); g.strokeStyle = 'rgba(30,8,6,.45)'; g.lineWidth = lw(P, 2); for (let i = 1; i < 4; i++) { g.beginPath(); g.moveTo(X(u + i * .025), Y(-.3)); g.lineTo(X(u + i * .025 + d * .005), Y(.6)); g.stroke(); } }
      // glass cabinet (büfe) with cups on the left
      rrect(g, X(-.05), Y(-.05), S(.4), Y(.7) - Y(-.05), S(.01)); fillStroke(g, '#4a2a1a', LINE, lw(P, 3));
      g.fillStyle = '#2c2220'; g.fillRect(X(-.02), Y(-.02), S(.34), Y(.4) - Y(-.02));
      for (const v of [.1, .25, .4]) { g.fillStyle = '#5a3a26'; g.fillRect(X(-.02), Y(v), S(.34), S(.01)); for (let i = 0; i < 4; i++) { const x = X(.01 + i * .08), y = Y(v); g.beginPath(); g.moveTo(x, y); g.lineTo(x + S(.05), y); g.lineTo(x + S(.045), y - S(.035)); g.lineTo(x + S(.005), y - S(.035)); g.closePath(); fillStroke(g, '#e4dccd', LINE, lw(P, 1.6)); } }
      g.fillStyle = 'rgba(255,255,255,.07)'; g.beginPath(); g.moveTo(X(0), Y(.35)); g.lineTo(X(.12), Y(-.02)); g.lineTo(X(.16), Y(-.02)); g.lineTo(X(.04), Y(.35)); g.fill();
      // floor lamp (the key light)
      g.fillStyle = '#1f140e'; g.fillRect(X(.9), Y(.3), S(.008), Y(1) - Y(.3));
      g.beginPath(); g.moveTo(X(.84), Y(.32)); g.lineTo(X(.97), Y(.32)); g.lineTo(X(.94), Y(.2)); g.lineTo(X(.87), Y(.2)); g.closePath(); fillStroke(g, '#f2dcae', LINE, lw(P, 3));
      // dado
      g.fillStyle = '#3e2618'; g.fillRect(0, Y(.62), P.w, P.h);
      g.fillStyle = '#56371f'; g.fillRect(0, Y(.62), P.w, S(.015));
      bentwoodChair(P, .3, .45, 1.2); bentwoodChair(P, .7, .45, 1.2);
    },
    fore(g, W, H, k, kind) { if (kind !== 'tek' && kind !== 'yakin') tableTop(g, W, H, .79, k, '#d4c6ae'); },
  },
};

// cached backdrops (sharp + blurred variants)
const cache = new Map();
export function backdrop(name, W, H, blurPx = 0) {
  const key = `${name}|${W}|${blurPx}`;
  if (cache.has(key)) return cache.get(key);
  let c;
  if (!blurPx) { c = canvas(W * SPAN, H * SPAN); SETS[name].back(c); }
  else {
    const src = backdrop(name, W, H, 0);
    c = canvas(src.width, src.height); const g = c.getContext('2d');
    g.filter = `blur(${blurPx}px)`; g.drawImage(src, 0, 0); g.filter = 'none';
  }
  cache.set(key, c); return c;
}
