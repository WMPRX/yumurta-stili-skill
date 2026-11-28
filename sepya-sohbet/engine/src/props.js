// props.js — insert shots ('nesne'): the story's key object, framed alone and large (24 % of the shots in the references).
// Every insert is a function (g, t, W, H, opts, ctx). opts come from the shot: { prop: 'telefon', mesajlar: [...] }.
// A story can pass its own: { kind: 'nesne', prop: (g, t, W, H, opts, ctx) => { ... } }.
import { rrect, fillStroke, rgba, shade, canvas, hash } from './util.js';
import { LINE } from './chars.js';
import { teaGlass } from './sets.js';
import { steam, glow } from './fx.js';
import { board, pieces, piece, POZ } from './chess.js';
import { easeShot } from './util.js';

function bokeh(g, W, H, seed = 1, col = '#f2c47a', n = 14, top = .05, bottom = .5) {
  for (let i = 0; i < n; i++) {
    const x = hash(i * 3 + seed) * W, y = (top + hash(i * 7 + seed) * (bottom - top)) * H, r = (30 + hash(i) * 40) * W / 1080;
    glow(g, x, y, r, col, .22 + hash(i * 5) * .2);
  }
}
const blurCache = new Map();
function soft(key, W, H, blur, paint) {        // paint once, blur once, reuse
  const k = `${key}|${W}|${blur}`; if (blurCache.has(k)) return blurCache.get(k);
  const a = canvas(W, H); paint(a.getContext('2d'));
  const b = canvas(W, H); const g = b.getContext('2d'); g.filter = `blur(${blur}px)`; g.drawImage(a, 0, 0); blurCache.set(k, b); return b;
}

function silhouette(g, cx, cy, r, tur, lean, h) {
  g.save(); g.fillStyle = '#3a2418';
  g.beginPath(); g.ellipse(cx, cy + r * 1.6, r * 1.8, r * 1.4, 0, Math.PI, 0); g.fill(); g.fillRect(cx - r * 1.8, cy + r * 1.6, r * 3.6, h);
  g.translate(cx, cy); g.rotate(lean); g.translate(-cx, -cy);
  const hx = cx + lean * r * 1.2;
  g.beginPath(); g.arc(hx, cy - r, r, 0, 7); g.fill();
  if (tur === 'kirpi') for (let a = -2.8; a < -.3; a += .28) { g.beginPath(); g.moveTo(hx + Math.cos(a) * r, cy - r + Math.sin(a) * r); g.lineTo(hx + Math.cos(a + .14) * r * 1.5, cy - r + Math.sin(a + .14) * r * 1.5); g.lineTo(hx + Math.cos(a + .28) * r, cy - r + Math.sin(a + .28) * r); g.fill(); }
  else if (tur === 'baykus') for (const s of [-1, 1]) { g.beginPath(); g.moveTo(hx + s * r * .5, cy - r * 1.7); g.lineTo(hx + s * r * 1.1, cy - r * 2.5); g.lineTo(hx + s * r, cy - r * 1.3); g.fill(); }
  else if (tur === 'kedi') for (const s of [-1, 1]) { g.beginPath(); g.moveTo(hx + s * r * .25, cy - r * 1.85); g.lineTo(hx + s * r * .8, cy - r * 2.35); g.lineTo(hx + s * r * .95, cy - r * 1.4); g.fill(); }
  if (lean) { g.beginPath(); g.ellipse(hx + r * .95, cy - r * .7, r * .3, r * .22, 0, 0, 7); g.fill(); }   // a hand cupped at the mouth
  g.restore();
}

export const PROPS = {
  // a tea glass on a patterned tablecloth, steam rising, café bokeh behind; a hand may reach in (opts.el: species hand colour)
  cay(g, t, W, H, o = {}, ctx) {
    const k = W / 1080;
    g.drawImage(soft('cay-bg', W, H, 18 * k, b => {
      b.fillStyle = '#3a2418'; b.fillRect(0, 0, W, H);
      b.fillStyle = '#4b3022'; for (let x = 0; x < W; x += 90 * k) b.fillRect(x, 0, 40 * k, H * .55);
      bokeh(b, W, H, 3);
    }), 0, 0);
    // tablecloth with a dotted pattern
    g.fillStyle = '#b8a78c'; g.fillRect(0, H * .57, W, H);
    g.strokeStyle = 'rgba(70,45,30,.35)'; g.lineWidth = 2 * k;
    for (let r = 0; r < 14; r++) for (let x = (r % 2) * 50 * k; x < W; x += 100 * k) { const y = H * .6 + r * r * 4 * k + r * 26 * k; g.beginPath(); g.ellipse(x, y, (10 + r) * k, (4 + r * .4) * k, 0, 0, 7); g.stroke(); }
    g.beginPath(); g.moveTo(0, H * .57); g.lineTo(W, H * .57); g.strokeStyle = LINE; g.lineWidth = 3 * k; g.stroke();
    teaGlass(g, W * .5, H * .82, H * .36, k * 1.8, o.dolu ?? .75);
    if (o.buhar !== false) steam(g, t, W * .5, H * .44, H * .3, k * 1.2);
    if (o.el) {                                   // a hand at the saucer
      g.save(); g.translate(W * .86, H * .86); g.rotate(-.25);
      g.beginPath(); g.ellipse(0, 0, 150 * k, 95 * k, 0, 0, 7); fillStroke(g, o.el, LINE, 6 * k);
      g.strokeStyle = LINE; g.lineWidth = 4 * k; for (const d of [-40, 0, 40]) { g.beginPath(); g.arc(-120 * k, d * k, 34 * k, -1.2, 1.2); g.stroke(); }
      g.fillStyle = o.el; g.fillRect(40 * k, -90 * k, 300 * k, 180 * k); g.restore();
    }
  },

  // a phone held in two hands: a lock screen with one notification, or a chat (opts.mesajlar: [{ ben: true|false, metin }])
  telefon(g, t, W, H, o = {}, ctx) {
    const k = W / 1080;
    g.drawImage(soft('tel-bg', W, H, 22 * k, b => { b.fillStyle = '#2a2230'; b.fillRect(0, 0, W, H); bokeh(b, W, H, 9, '#f0bd70', 18, .02, .7); b.fillStyle = '#3c2a20'; b.fillRect(0, H * .72, W, H); }), 0, 0);
    const pw = W * .54, ph = pw * 1.95, px = (W - pw) / 2, py = H * .12;
    g.save(); g.translate(W / 2, py + ph / 2); g.rotate(-.03); g.translate(-W / 2, -(py + ph / 2));
    rrect(g, px - 14 * k, py - 14 * k, pw + 28 * k, ph + 28 * k, 70 * k); fillStroke(g, '#1d1a1a', LINE, 6 * k);
    rrect(g, px, py, pw, ph, 56 * k); g.save(); g.clip();
    const chat = Array.isArray(o.mesajlar);
    g.fillStyle = chat ? '#cfc6b8' : '#4a4652'; g.fillRect(px, py, pw, ph);
    g.font = `600 ${30 * k}px sans-serif`; g.textAlign = 'center';
    if (!chat) {
      g.fillStyle = '#efe9df'; g.font = `300 ${150 * k}px sans-serif`; g.fillText(o.saat || '23:12', W / 2, py + ph * .2);
      g.font = `400 ${28 * k}px sans-serif`; g.fillText(o.tarih || 'Perşembe', W / 2, py + ph * .09);
      rrect(g, px + 24 * k, py + ph * .27, pw - 48 * k, 120 * k, 26 * k); g.fillStyle = 'rgba(235,230,222,.85)'; g.fill();
      g.textAlign = 'left'; g.fillStyle = '#2a2420'; g.font = `700 ${28 * k}px sans-serif`; g.fillText(o.kimden || 'Mesaj', px + 50 * k, py + ph * .27 + 46 * k);
      g.font = `400 ${26 * k}px sans-serif`; g.fillText(o.metin || '…', px + 50 * k, py + ph * .27 + 88 * k);
    } else {
      g.fillStyle = '#d8cfc0'; g.fillRect(px, py, pw, 120 * k);
      g.textAlign = 'left'; g.fillStyle = '#2a2420'; g.font = `700 ${30 * k}px sans-serif`; g.fillText(o.kimden || 'Mesaj', px + 110 * k, py + 76 * k);
      g.beginPath(); g.arc(px + 64 * k, py + 66 * k, 28 * k, 0, 7); g.fillStyle = '#9a8a76'; g.fill();
      let y = py + 170 * k;
      const shown = o.mesajlar;
      for (const m of shown) {
        if (m.taslak) { const blink = (t * 2 % 1) < .5 ? '|' : ''; m._t = m.metin + blink; }
        g.font = `400 ${36 * k}px sans-serif`;
        const w = Math.min(pw * .7, g.measureText(m.metin).width + 50 * k), x = m.ben ? px + pw - w - 24 * k : px + 24 * k;
        if (m.taslak) {   // the unsent draft sits in the text field at the bottom
          const fy = py + ph - 120 * k; rrect(g, px + 20 * k, fy, pw - 40 * k, 76 * k, 38 * k); g.fillStyle = '#ffffff'; g.fill(); g.strokeStyle = 'rgba(40,30,20,.4)'; g.lineWidth = 2 * k; g.stroke();
          g.fillStyle = '#2a2420'; g.font = `400 ${36 * k}px sans-serif`; g.textAlign = 'center'; g.fillText(m._t, W / 2, fy + 50 * k); g.textAlign = 'left'; continue;
        }
        rrect(g, x, y, w, 78 * k, 26 * k); g.fillStyle = m.ben ? '#cfe0c0' : '#ffffff'; g.fill();
        g.fillStyle = '#2a2420'; g.fillText(m.metin, x + 25 * k, y + 52 * k); y += 104 * k;
      }
    }
    g.restore();
    const sc = g.createLinearGradient(px, py, px + pw, py + ph); sc.addColorStop(0, 'rgba(255,255,255,.08)'); sc.addColorStop(.5, 'rgba(255,255,255,0)');
    rrect(g, px, py, pw, ph, 56 * k); g.fillStyle = sc; g.fill();
    g.restore();
    glow(g, W / 2, py + ph * .45, W * .7, '#ffe6bf', .18);
    // hands (thumbs over the edges)
    const hc = o.el || '#ecdfc9';
    for (const sx of [-1, 1]) {
      g.save(); g.translate(W / 2 + sx * pw * .55, py + ph * .8); g.rotate(sx * .22);
      g.beginPath(); g.ellipse(0, 60 * k, 95 * k, 150 * k, 0, 0, 7); fillStroke(g, hc, LINE, 6 * k);
      g.beginPath(); g.ellipse(-sx * 70 * k, -30 * k, 30 * k, 60 * k, -sx * .5, 0, 7); fillStroke(g, hc, LINE, 5 * k);
      const sl = o.kol || '#bd8d3c';   // sleeve colour
      rrect(g, -80 * k, 150 * k, 160 * k, H, 30 * k); fillStroke(g, sl, LINE, 6 * k);
      g.restore();
    }
  },

  // an old photo on the table under a lamp: two silhouettes (opts.kafalar: ['baykus','kirpi'] picks ear tufts / spines)
  fotograf(g, t, W, H, o = {}, ctx) {
    const k = W / 1080;
    g.drawImage(soft('foto-bg', W, H, 20 * k, b => { b.fillStyle = '#2d1c14'; b.fillRect(0, 0, W, H); const gr = b.createRadialGradient(W * .5, 0, 0, W * .5, 0, H * .7); gr.addColorStop(0, 'rgba(255,214,150,.6)'); gr.addColorStop(1, 'rgba(255,214,150,0)'); b.fillStyle = gr; b.fillRect(0, 0, W, H); }), 0, 0);
    g.fillStyle = '#c5b393'; g.beginPath(); g.ellipse(W * .5, H * .78, W * .9, H * .2, 0, 0, 7); g.fill();
    g.save(); g.translate(W * .5, H * .7); g.rotate(-.05);
    const w = W * .72, h = w * .72;
    rrect(g, -w / 2, -h / 2, w, h, 8 * k); fillStroke(g, '#efe6d4', LINE, 5 * k);
    g.fillStyle = '#8f7c62'; g.fillRect(-w / 2 + 30 * k, -h / 2 + 30 * k, w - 60 * k, h - 100 * k);
    g.fillStyle = '#a8977b'; g.fillRect(-w / 2 + 30 * k, -h / 2 + 30 * k, w - 60 * k, (h - 100 * k) * .55);
    const kaf = o.kafalar || ['baykus', 'kirpi'];
    kaf.forEach((tur, i) => {
      const x = (i ? .17 : -.17) * w, y = .1 * h, r = .12 * w;
      g.fillStyle = '#2a1d16';
      g.beginPath(); g.arc(x, y - r * .9, r, 0, 7); g.fill();
      g.beginPath(); g.ellipse(x, y + r * 1.2, r * 1.5, r * 1.1, 0, Math.PI, 0); g.fill();
      if (tur === 'baykus') for (const s of [-1, 1]) { g.beginPath(); g.moveTo(x + s * r * .6, y - r * 1.6); g.lineTo(x + s * r * 1.05, y - r * 2.3); g.lineTo(x + s * r * .95, y - r * 1.2); g.fill(); }
      else for (let a = -2.6; a < -.5; a += .3) { g.beginPath(); g.moveTo(x + Math.cos(a) * r * .9, y - r * .9 + Math.sin(a) * r * .9); g.lineTo(x + Math.cos(a + .15) * r * 1.4, y - r * .9 + Math.sin(a + .15) * r * 1.4); g.lineTo(x + Math.cos(a + .3) * r * .9, y - r * .9 + Math.sin(a + .3) * r * .9); g.fill(); }
    });
    g.fillStyle = 'rgba(255,250,235,.12)'; g.fillRect(-w / 2, -h / 2, w, h);
    g.restore();
  },

  // a lit window in a dark facade, someone inside (opts.kim: 'baykus' | 'kirpi' silhouette)
  pencere(g, t, W, H, o = {}, ctx) {
    const k = W / 1080;
    g.fillStyle = '#3e271f'; g.fillRect(0, 0, W, H);
    for (let y = 0; y < H; y += 26 * k) { g.fillStyle = 'rgba(15,8,5,.18)'; g.fillRect(0, y, W, 3 * k); }
    for (const [x, y, on] of [[.08, .06, 0], [.62, .06, 1], [.08, .74, 1], [.62, .74, 0]]) {
      g.fillStyle = on ? '#d99d55' : '#1b1820'; g.fillRect(x * W, y * H, W * .3, H * .16);
      g.strokeStyle = '#24160f'; g.lineWidth = 8 * k; g.strokeRect(x * W, y * H, W * .3, H * .16);
    }
    const x = W * .22, y = H * .3, w = W * .56, h = H * .36;
    g.fillStyle = '#d8a663'; g.fillRect(x, y, w, h);
    glow(g, x + w / 2, y + h / 2, W * .6, '#ffcf86', .25);
    // one silhouette (opts.kim) or several (opts.kimler: ['kirpi', 'kedi', ...]); opts.fisilti leans the first toward the second's ear
    const who = o.kimler || [o.kim || 'kirpi'], n = who.length;
    who.forEach((tur, i) => {
      const r = w * (n > 1 ? .11 : .14);
      let cx = x + w * (n > 1 ? .27 + .46 * i / (n - 1) : .5), cy = y + h * .64;
      const lean = o.fisilti && i === 0 ? .32 : 0;
      if (lean) cx += r * .35;
      silhouette(g, cx, cy, r, tur, lean, h);
    });
    g.strokeStyle = '#2a1a12'; g.lineWidth = 14 * k; g.strokeRect(x, y, w, h);
    g.lineWidth = 9 * k; g.beginPath(); g.moveTo(x + w / 2, y); g.lineTo(x + w / 2, y + h); g.moveTo(x, y + h * .4); g.lineTo(x + w, y + h * .4); g.stroke();
    g.fillStyle = '#e9e4dc'; g.fillRect(x - 30 * k, y + h, w + 60 * k, 22 * k); g.strokeStyle = LINE; g.lineWidth = 4 * k; g.strokeRect(x - 30 * k, y + h, w + 60 * k, 22 * k);
  },

  // the chess board up close: opts.zipla = seconds into the shot when the white knight jumps (2,5) -> (3,3); opts.el = colour of the hand that moves it
  satranc(g, t, W, H, o = {}, ctx) {
    const k = W / 1080;
    g.drawImage(soft('satranc-bg', W, H, 22 * k, b => { b.fillStyle = '#2f1d14'; b.fillRect(0, 0, W, H); bokeh(b, W, H, 21, '#f2c47a', 16, .02, .45); }), 0, 0);
    g.fillStyle = '#3a2418'; g.fillRect(0, H * .36, W, H);
    const map = board(g, { cx: W * .62, nearY: H * 1.25, farY: H * .36, nearW: W * 2.6, farW: W * 1.05, k, lw: 5 });
    const KN = 6, from = [2, 5], to = [3, 3];
    const z = o.zipla ?? 1e9, u = Math.min(1, Math.max(0, (t - z) / .7));
    pieces(g, map, POZ, 1.25, k, 5, KN);
    const a = map(...from), b = map(...to), e = easeShot(u);
    const x = a[0] + (b[0] - a[0]) * e, base = a[1] + (b[1] - a[1]) * e, y = base - Math.sin(Math.PI * u) * H * .1, hh = (a[2] + (b[2] - a[2]) * e) * 1.45;
    if (u > 0 && u < 1) { g.beginPath(); g.ellipse(x, base, hh * .3, hh * .07, 0, 0, 7); g.fillStyle = 'rgba(20,10,5,.35)'; g.fill(); }
    piece(g, 'at', x, y, hh, true, k, 6);
    if (o.el && t > z - .6 && t < z + 1.1) {                // the hand that plays it: a sleeve from the top right, a mitten pinching the knight's head
      const hx = x + hh * .02, hy = y - hh * .92;
      g.save(); g.translate(hx, hy); g.rotate(-.62);
      rrect(g, 60 * k, -95 * k, 1200 * k, 190 * k, 80 * k); fillStroke(g, o.kol || '#4f5140', LINE, 7 * k);
      rrect(g, 40 * k, -105 * k, 70 * k, 210 * k, 26 * k); fillStroke(g, '#3a3b2f', LINE, 6 * k);           // cuff
      g.beginPath(); g.ellipse(-10 * k, 0, 105 * k, 85 * k, 0, 0, 7); fillStroke(g, o.el, LINE, 7 * k);
      g.beginPath(); g.ellipse(-80 * k, 60 * k, 40 * k, 26 * k, .6, 0, 7); fillStroke(g, o.el, LINE, 6 * k);    // thumb
      g.strokeStyle = LINE; g.lineWidth = 4 * k; for (const d of [-40, 0, 40]) { g.beginPath(); g.arc(-95 * k, d * k - 20 * k, 26 * k, -1.3, 1.3); g.stroke(); }
      g.restore();
    }
  },
};
