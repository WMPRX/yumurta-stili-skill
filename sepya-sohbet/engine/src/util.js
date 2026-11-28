// util.js — small helpers shared by every module.
export const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a, b, u) => a + (b - a) * u;
export const smooth = u => { u = clamp(u); return u * u * (3 - 2 * u); };
// measured push-in profile: 12 % of the move done at a quarter, 54 % at half, 93 % at three quarters (analiz/kamera.md)
export const easeShot = u => { u = clamp(u); return u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; };
export function hash(n) { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }
export function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) % 100000) / 100000; }; }

// hex helpers
export function hex2rgb(h) { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); const n = parseInt(h, 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
export function rgb2hex([r, g, b]) { return '#' + [r, g, b].map(v => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0')).join(''); }
export function shade(h, k) { return rgb2hex(hex2rgb(h).map(v => v * k)); }                 // k < 1 darker, > 1 lighter
export function mix(a, b, u) { const A = hex2rgb(a), B = hex2rgb(b); return rgb2hex(A.map((v, i) => lerp(v, B[i], u))); }
export function rgba(h, a) { const [r, g, b] = hex2rgb(h); return `rgba(${r},${g},${b},${a})`; }

// rounded rectangle / blob path helpers
export function rrect(g, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2);
  g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
}
// closed smooth curve through points (Catmull-Rom -> Bezier)
export function blob(g, pts, close = true) {
  const n = pts.length; g.beginPath();
  const P = i => pts[(i + n) % n];
  g.moveTo(pts[0][0], pts[0][1]);
  const last = close ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = close ? P(i - 1) : pts[Math.max(0, i - 1)], p1 = P(i), p2 = close ? P(i + 1) : pts[Math.min(n - 1, i + 1)], p3 = close ? P(i + 2) : pts[Math.min(n - 1, i + 2)];
    g.bezierCurveTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1]);
  }
  if (close) g.closePath();
}
export function fillStroke(g, fill, line, lw) { if (fill) { g.fillStyle = fill; g.fill(); } if (line) { g.strokeStyle = line; g.lineWidth = lw; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(); } }

// offscreen canvas
export function canvas(w, h) { const c = document.createElement('canvas'); c.width = Math.max(1, Math.round(w)); c.height = Math.max(1, Math.round(h)); return c; }

// blink: every 0.9 - 2.4 s, four frames (half, shut, shut, half); also one blink across every expression change
export function blinkAt(t, seed = 1, swaps = [], fps = 30) {
  const f = Math.floor(t * fps);
  for (const s of swaps) { const d = f - Math.floor(s * fps) + 2; if (d >= 0 && d < 4) return [.5, 1, 1, .5][d]; }
  let at = hash(seed) * 1.2, k = 0;
  while (at < t + 1 && k < 4000) {
    const d = f - Math.floor(at * fps);
    if (d >= 0 && d < 4) return [.5, 1, 1, .5][d];
    at += .9 + hash(seed * 13 + k * 7.31) * 1.5; k++;
  }
  return 0;
}
