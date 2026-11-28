// fx.js — particles and light, all deterministic in t (any frame can be rendered alone).
import { hash, rgba, clamp } from './util.js';

// snow: two depths; near flakes are bigger and soft (out of focus), as in the references
export function snow(g, t, W, H, { n = 90, seed = 1, wind = .015 } = {}) {
  g.save();
  for (let i = 0; i < n; i++) {
    const near = i % 7 === 0, z = near ? 1 : .35 + hash(i + seed) * .45;
    const sp = (.035 + hash(i * 3 + seed) * .04) * z;
    const x = ((hash(i * 7 + seed) + t * wind * z + Math.sin(t * .8 + i) * .01) % 1 + 1) % 1;
    const y = ((hash(i * 11 + seed) + t * sp) % 1.05);
    const r = (near ? 7 + hash(i) * 6 : 1.6 + z * 2.6) * W / 1080;
    if (near) { const gr = g.createRadialGradient(x * W, y * H, 0, x * W, y * H, r); gr.addColorStop(0, 'rgba(240,235,228,.55)'); gr.addColorStop(1, 'rgba(240,235,228,0)'); g.fillStyle = gr; }
    else g.fillStyle = `rgba(240,235,228,${.45 + z * .4})`;
    g.beginPath(); g.arc(x * W, y * H, r, 0, 7); g.fill();
  }
  g.restore();
}
export function rain(g, t, W, H, { n = 70, seed = 2, a = .22 } = {}) {
  g.save(); g.strokeStyle = `rgba(210,215,225,${a})`; g.lineWidth = 1.6 * W / 1080; g.lineCap = 'round';
  for (let i = 0; i < n; i++) {
    const x = hash(i * 5 + seed) * W, len = (40 + hash(i) * 50) * H / 1920;
    const y = ((hash(i * 9 + seed) + t * (1.6 + hash(i * 2) * .6)) % 1.1) * H - len;
    g.beginPath(); g.moveTo(x, y); g.lineTo(x - len * .08, y + len); g.stroke();
  }
  g.restore();
}
export function dust(g, t, W, H, { n = 40, seed = 4, cx = .5, cy = .3, spread = .5 } = {}) {
  g.save(); g.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const x = (cx + (hash(i * 13 + seed) - .5) * spread + Math.sin(t * .3 + i * 2.1) * .02) * W;
    const y = (cy + (hash(i * 17 + seed) - .5) * spread * 1.2 + ((t * .01 * (1 + hash(i))) % .1)) * H;
    const a = .18 * (.5 + .5 * Math.sin(t * 1.3 + i));
    g.fillStyle = `rgba(255,225,180,${a})`; g.beginPath(); g.arc(x, y, (1.5 + hash(i * 3) * 2) * W / 1080, 0, 7); g.fill();
  }
  g.restore();
}
// steam from a glass: three soft wavy ribbons rising from (x, y); s = height in px
export function steam(g, t, x, y, s, k = 1) {
  g.save(); g.lineCap = 'round';
  for (let j = 0; j < 3; j++) {
    const ph = t * 1.4 + j * 2.1, a = .32 - j * .06;
    g.beginPath();
    for (let i = 0; i <= 24; i++) {
      const u = i / 24, yy = y - u * s, xx = x + (j - 1) * s * .12 + Math.sin(u * 5 + ph) * s * .08 * u;
      i ? g.lineTo(xx, yy) : g.moveTo(xx, yy);
    }
    const gr = g.createLinearGradient(0, y, 0, y - s); gr.addColorStop(0, `rgba(235,225,210,0)`); gr.addColorStop(.25, `rgba(235,225,210,${a})`); gr.addColorStop(1, 'rgba(235,225,210,0)');
    g.strokeStyle = gr; g.lineWidth = s * .05 * k; g.stroke();
  }
  g.restore();
}
// soft additive glow (lamps, lit windows). Only light sources glow.
export function glow(g, x, y, r, col = '#ffcf86', a = .5) {
  g.save(); g.globalCompositeOperation = 'lighter';
  const gr = g.createRadialGradient(x, y, 0, x, y, r);
  gr.addColorStop(0, rgba(col, a)); gr.addColorStop(.25, rgba(col, a * .45)); gr.addColorStop(1, rgba(col, 0));
  g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r); g.restore();
}
// a cone of light from (x0,y0) to (x1,y1), w = half width at the far end
export function beam(g, x0, y0, x1, y1, w, col = '#ffd391', a = .12) {
  g.save(); g.globalCompositeOperation = 'lighter';
  const ang = Math.atan2(y1 - y0, x1 - x0), len = Math.hypot(x1 - x0, y1 - y0);
  g.translate(x0, y0); g.rotate(ang);
  const gr = g.createLinearGradient(0, 0, len, 0); gr.addColorStop(0, rgba(col, a)); gr.addColorStop(1, rgba(col, 0));
  g.fillStyle = gr; g.beginPath(); g.moveTo(0, -w * .08); g.lineTo(len, -w); g.lineTo(len, w); g.lineTo(0, w * .08); g.closePath(); g.fill();
  g.restore();
}
// lightning / lamp flicker: returns extra brightness 0..1 for flash times [t0, t1, ...] (two quick pulses each, like the references)
export function flash(t, times = []) {
  let v = 0;
  for (const t0 of times) { const d = t - t0; if (d >= 0 && d < .7) v = Math.max(v, d < .07 ? 1 : d < .2 ? .25 : d < .3 ? .85 : clamp(1 - (d - .3) / .4) * .4); }
  return v;
}
