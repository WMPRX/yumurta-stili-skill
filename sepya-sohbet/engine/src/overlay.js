// overlay.js — drawn AFTER the grade, so they stay clean: one-word captions, the channel watermark, the end-card title.
// Measurements (analiz/altyazi.md): caption centre at 76.4 % of the height, cap height 54 px at 1920, one word at a time;
// watermark centre at 5.3 %, cap height 18 px, width ≈ 17.5 % of the frame; end-card title centre at 27.9 %, width ≈ 57 %.

const PUNCT = /[.,!?;:"“”«»…()\[\]—–-]+/g;
export function captionText(w) { return w.replace(PUNCT, '').toLocaleUpperCase('tr-TR'); }

// words: [{ word, start, end }] -> [{ text, start, until }]; a word stays until the next one starts, or 0.35 s after it ends
export function captionTimeline(words) {
  const out = [];
  for (let i = 0; i < words.length; i++) {
    const w = words[i], n = words[i + 1], text = captionText(w.word);
    if (!text) continue;
    const until = n ? Math.min(n.start, w.end + .35) : w.end + .35;
    out.push({ text, start: w.start - .03, until: Math.max(until, w.start + .12) });
  }
  return out;
}

export function drawCaption(g, caps, t, W, H, o = {}) {
  const c = caps.find(c => t >= c.start && t < c.until);
  if (!c) return null;
  const size = (o.size || 75) * H / 1920, y = (o.y || .764) * H;
  g.save();
  g.font = `${size}px Bangers`; g.textAlign = 'center'; g.textBaseline = 'alphabetic';
  const base = y + size * .721 / 2;                                   // centre the CAP height on y
  g.lineJoin = 'round'; g.miterLimit = 2;
  g.shadowColor = 'rgba(8,4,2,.75)'; g.shadowBlur = size * .12; g.shadowOffsetX = size * .03; g.shadowOffsetY = size * .07;
  g.strokeStyle = '#120a06'; g.lineWidth = size * .17; g.strokeText(c.text, W / 2, base);
  g.shadowColor = 'transparent';
  g.fillStyle = '#ffffff'; g.fillText(c.text, W / 2, base);
  g.restore();
  return c.text;
}

export function drawWatermark(g, text, W, H, a = 1) {
  if (!text || a <= 0) return;
  const size = 26 * H / 1920;
  g.save(); g.globalAlpha = a * .88;
  g.font = `600 ${size}px Cinzel`; g.letterSpacing = `${size * .55}px`; g.textAlign = 'center';
  g.fillStyle = '#b8a080'; g.fillText(text.toLocaleUpperCase('tr-TR'), W / 2 + size * .27, .053 * H + size * .35);
  g.restore();
}

// end-card title: gold serif, letter-spaced, glowing; fitted to 57 % of the width
export function drawTitle(g, text, W, H, a = 1) {
  if (!text || a <= 0) return;
  text = text.toLocaleUpperCase('tr-TR');
  g.save(); g.globalAlpha = a;
  let size = 100 * H / 1920;
  g.font = `600 ${size}px Cinzel`; g.letterSpacing = `${size * .18}px`;
  const w = g.measureText(text).width; size *= (.57 * W) / w;
  g.font = `600 ${size}px Cinzel`; g.letterSpacing = `${size * .18}px`; g.textAlign = 'center';
  const y = .2785 * H + size * .35;
  const gr = g.createLinearGradient(0, y - size * .7, 0, y); gr.addColorStop(0, '#f3dcae'); gr.addColorStop(1, '#c39a62');
  g.shadowColor = 'rgba(255,190,110,.55)'; g.shadowBlur = size * .35;
  g.fillStyle = gr; g.fillText(text, W / 2 + size * .09, y);
  g.shadowBlur = 0; g.fillText(text, W / 2 + size * .09, y);
  g.restore();
}
