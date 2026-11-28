// chars.js — flat 2D animal characters in clothes, drawn with Canvas 2D paths (analiz/karakter.md).
// Character space: origin at the neck base, y down. The head is ~660 units wide; shoulders ±400; the torso runs to y≈1000.
// A character is drawn in two passes so a table can sit between them:  body()  ->  set foreground  ->  arms().
//
//   const c = new Character({ tur: 'baykus' })            // or 'kirpi'; colours can be overridden: { tur, renk: { ceket: '#...' } }
//   c.body(g, st); c.arms(g, st)                          // st = { x, y, s, k, expr, talk, blink, gazeX, gazeY, pose, light }
//     x, y   screen position of the neck base (px)          s  px per unit (head width in px = 660 * s)
//     k      frame width / 1080 (line widths are set in 1080-wide px)
//     expr   'notr' | 'bilge' | 'gulumse' | 'uzgun' | 'endiseli' | 'saskin' | 'dusunceli' | 'kizgin' | 'utangac'
//     talk   0..1 mouth / beak opening (from the voice envelope, only while this character speaks)
//     blink  0..1 lid closure from blinkAt()
//     pose   'yan' (arms down) | 'masa' (forearms on the table) | 'el' (right hand raised) | 'cene' (hand on chin) | 'telefon' (phone in both hands)
//     light  -1 | 1 : side of the key light (the other side gets the cel shadow)
import { blob, fillStroke, rrect, shade, mix, rgba, clamp, lerp } from './util.js';

export const LINE = '#2a1a12';            // measured outline colour after the grade: dark umber, never black

// --- expressions --------------------------------------------------------------------------------
// lid: upper lid closure (0 open, 1 shut) · tilt: + inner corner down (angry), − inner corner up (sad)
// brow: vertical offset in units (− = raised) · btilt: like tilt for the brows · mouth: −1 frown … +1 smile · open: resting mouth opening
const EXPR = {
  notr:      { lid: .12, tilt: 0,   brow: 0,   btilt: 0,   mouth: .15, open: 0,   gx: 0,   gy: 0,   pupil: 1 },
  bilge:     { lid: .46, tilt: -.05, brow: 6,   btilt: .1,  mouth: .45, open: 0,   gx: 0,   gy: .05, pupil: .95 },
  gulumse:   { lid: .3,  tilt: 0,   brow: -8,  btilt: -.1, mouth: .9,  open: .15, gx: 0,   gy: 0,   pupil: 1 },
  uzgun:     { lid: .38, tilt: -.45, brow: -14, btilt: -.6, mouth: -.55, open: 0,  gx: 0,   gy: .35, pupil: 1.05 },
  endiseli:  { lid: .08, tilt: -.3, brow: -28, btilt: -.55, mouth: -.3, open: .05, gx: 0,   gy: 0,   pupil: .9 },
  saskin:    { lid: 0,   tilt: 0,   brow: -48, btilt: 0,   mouth: 0,   open: .45, gx: 0,   gy: 0,   pupil: .72 },
  dusunceli: { lid: .3,  tilt: .05, brow: -6,  btilt: .2,  mouth: -.05, open: 0,  gx: .45, gy: -.4, pupil: 1 },
  kizgin:    { lid: .32, tilt: .5,  brow: 14,  btilt: .7,  mouth: -.45, open: .05, gx: 0,  gy: 0,   pupil: .9 },
  utangac:   { lid: .3,  tilt: -.2, brow: -10, btilt: -.35, mouth: .3, open: 0,   gx: -.4, gy: .35, pupil: 1, blush: .5 },
};
export const EXPRESSIONS = Object.keys(EXPR);

// --- species ------------------------------------------------------------------------------------
const SPECIES = {
  baykus: {   // owl: the calm mentor. Tufted wide head, pale facial discs, amber half-lidded eyes, beak, tweed jacket + bow tie
    renk: { tuy: '#8b7259', tuyKoyu: '#5f4a38', disk: '#ddd0bb', diskKenar: '#a48b70', gaga: '#d2a764', iris: '#e3a23b', ceket: '#4f5140', ceketKoyu: '#3a3b2f',
            gomlek: '#e7dfcf', kravat: '#b98a2e', yelek: '#6d5a44', el: '#8b7259' },
    expr: 'bilge',
  },
  kirpi: {    // hedgehog: the young one. Crown of spines, round cream face, big shiny eyes, striped knit sweater
    // the face is mid-light: a cream face filling a close-up pushes the contrast over the references
    renk: { diken: '#6a4a33', dikenAcik: '#9a7557', yuz: '#d8c6aa', yuzKoyu: '#b8a080', kulak: '#d79a8a', burun: '#2b1b14', allik: '#e08a78',
            kazak: '#bd8d3c', kazakKoyu: '#94692a', serit: '#ead9b4', yaka: '#e7dfcf', el: '#d8c6aa' },
    expr: 'notr',
  },
};
export const SPECIES_NAMES = Object.keys(SPECIES);

export class Character {
  constructor(look = {}) {
    const sp = SPECIES[look.tur || 'baykus'];
    if (!sp) throw new Error(`unknown tur "${look.tur}" (${SPECIES_NAMES.join(', ')})`);
    this.tur = look.tur || 'baykus';
    this.r = { ...sp.renk, ...(look.renk || {}) };
    this.defaultExpr = look.expr || sp.expr;
    this.line = look.line || LINE;
  }
  // world position of the two eye centres and the eye radius (used by the end card's glowing eyes)
  eyes(st) {
    const e = this.tur === 'baykus' ? { dx: 122, y: -372, r: 86 } : { dx: 104, y: -360, r: 74 };
    return [[st.x - e.dx * st.s, st.y + e.y * st.s], [st.x + e.dx * st.s, st.y + e.y * st.s], e.r * st.s];
  }
  _setup(g, st) {
    const headPx = 660 * st.s / (st.k || 1);                        // head width in 1080-wide px
    this.lw = (3.1 + 0.0076 * headPx) * (st.k || 1) / st.s;         // measured: 4.6 px in a two-shot, ~10 px in a close-up (at 1080)
    g.save(); g.translate(st.x, st.y); g.scale(st.s, st.s);
  }
  // cel shadow on the side away from the light, clipped to the current path
  _cel(g, x0, x1, light = 1, a = .22) {
    g.save(); g.clip();
    const gr = g.createLinearGradient(light > 0 ? x0 : x1, 0, light > 0 ? x1 : x0, 0);
    gr.addColorStop(0, 'rgba(25,12,6,0)'); gr.addColorStop(.5, 'rgba(25,12,6,0)'); gr.addColorStop(.78, `rgba(25,12,6,${a * .8})`); gr.addColorStop(1, `rgba(25,12,6,${a * 1.15})`);
    g.fillStyle = gr; g.fillRect(x0 - 50, -2000, x1 - x0 + 100, 4000); g.restore();
  }

  body(g, st) {
    this._setup(g, st);
    const ex = { ...EXPR[st.expr || this.defaultExpr] || EXPR.notr };
    if (this.tur === 'baykus') { this._owlBody(g, st); this._owlHead(g, st, ex); }
    else { this._hogBody(g, st); this._hogHead(g, st, ex); }
    g.restore();
  }
  arms(g, st) {
    this._setup(g, st);
    this._arms(g, st);
    g.restore();
  }

  // ---------------------------------------------------------------- torso
  _torso(g, fill, dark, light) {
    const L = this.line, lw = this.lw;
    blob(g, [[-170, -10], [170, -10], [330, 40], [420, 150], [445, 420], [430, 1150], [-430, 1150], [-445, 420], [-420, 150], [-330, 40]]);
    fillStroke(g, fill); this._cel(g, -450, 450, light, .2); fillStroke(g, null, L, lw);
  }
  _owlBody(g, st) {
    const r = this.r, L = this.line, lw = this.lw, li = st.light ?? 1;
    this._torso(g, r.ceket, r.ceketKoyu, li);
    // shirt V + waistcoat
    g.beginPath(); g.moveTo(-175, -8); g.lineTo(175, -8); g.lineTo(60, 430); g.lineTo(-60, 430); g.closePath(); fillStroke(g, r.yelek, L, lw * .8);
    g.beginPath(); g.moveTo(-150, -8); g.lineTo(150, -8); g.lineTo(0, 300); g.closePath(); fillStroke(g, r.gomlek, L, lw * .8);
    // waistcoat buttons
    for (const y of [360, 470, 580]) { g.beginPath(); g.arc(0, y, 13, 0, 7); fillStroke(g, shade(r.yelek, .6)); }
    g.beginPath(); g.moveTo(0, 300); g.lineTo(0, 1150); g.strokeStyle = this.line; g.lineWidth = lw * .55; g.stroke();
    // lapels
    for (const sx of [-1, 1]) {
      g.beginPath(); g.moveTo(sx * 175, -10); g.lineTo(sx * 300, 40); g.lineTo(sx * 250, 160); g.lineTo(sx * 300, 210); g.lineTo(sx * 70, 640); g.lineTo(sx * 60, 430); g.closePath();
      fillStroke(g, shade(r.ceket, sx === -(li) ? .82 : 1.06), L, lw * .8);
    }
    // collar points
    for (const sx of [-1, 1]) { g.beginPath(); g.moveTo(sx * 18, 40); g.lineTo(sx * 150, -12); g.lineTo(sx * 118, 120); g.closePath(); fillStroke(g, r.gomlek, L, lw * .7); }
    // bow tie
    g.beginPath(); g.moveTo(0, 62); g.quadraticCurveTo(-60, 10, -112, 30); g.lineTo(-112, 112); g.quadraticCurveTo(-60, 130, 0, 70);
    g.quadraticCurveTo(60, 130, 112, 112); g.lineTo(112, 30); g.quadraticCurveTo(60, 10, 0, 62); fillStroke(g, r.kravat, L, lw * .8);
    rrect(g, -24, 44, 48, 44, 12); fillStroke(g, shade(r.kravat, .85), L, lw * .7);
    // breast pocket + square
    g.beginPath(); g.moveTo(-385, 300); g.lineTo(-245, 285); fillStroke(g, null, L, lw * .7);
    g.beginPath(); g.moveTo(-372, 298); g.lineTo(-352, 262); g.lineTo(-326, 290); g.lineTo(-300, 258); g.lineTo(-276, 288); fillStroke(g, r.gomlek, L, lw * .55);
    // tweed flecks
    g.fillStyle = rgba(shade(r.ceket, 1.35), .35);
    for (let i = 0; i < 140; i++) { const x = ((i * 97) % 840) - 420, y = 80 + ((i * 53) % 1000); if (Math.abs(x) > 80 + y * .1) g.fillRect(x, y, 10, 4); }
  }
  _hogBody(g, st) {
    const r = this.r, L = this.line, lw = this.lw, li = st.light ?? 1;
    this._torso(g, r.kazak, r.kazakKoyu, li);
    // knit stripes (clipped to the torso)
    g.save();
    blob(g, [[-170, -10], [170, -10], [330, 40], [420, 150], [445, 420], [430, 1150], [-430, 1150], [-445, 420], [-420, 150], [-330, 40]]); g.clip();
    for (const y of [330, 420, 700, 790]) { g.fillStyle = r.serit; g.fillRect(-460, y, 920, 46); g.strokeStyle = rgba(this.line, .5); g.lineWidth = lw * .45; g.strokeRect(-460, y, 920, 46); }
    g.strokeStyle = rgba(shade(r.kazak, .7), .55); g.lineWidth = lw * .35;
    for (let x = -420; x <= 420; x += 46) { g.beginPath(); g.moveTo(x, 900); g.lineTo(x, 1150); g.stroke(); }   // ribbed hem
    g.restore();
    // neck + crew collar
    blob(g, [[-110, -60], [110, -60], [120, 40], [-120, 40]]); fillStroke(g, r.yuzKoyu, L, lw * .8);
    g.beginPath(); g.ellipse(0, 28, 175, 62, 0, 0, Math.PI); g.lineTo(-175, 28); fillStroke(g, null, L, lw);
    g.beginPath(); g.ellipse(0, 22, 200, 80, 0, -.05, Math.PI + .05); g.ellipse(0, 22, 165, 50, 0, Math.PI, 0, true); g.closePath(); fillStroke(g, shade(r.kazak, .9), L, lw * .8);
    g.strokeStyle = rgba(this.line, .45); g.lineWidth = lw * .35;
    for (let a = .25; a < Math.PI - .2; a += .2) { g.beginPath(); g.moveTo(Math.cos(a) * 168, 22 + Math.sin(a) * 52); g.lineTo(Math.cos(a) * 198, 22 + Math.sin(a) * 78); g.stroke(); }
  }

  // ---------------------------------------------------------------- heads
  _owlHead(g, st, ex) {
    const r = this.r, L = this.line, lw = this.lw, li = st.light ?? 1;
    // ear tufts
    for (const sx of [-1, 1]) {
      blob(g, [[sx * 330, -500], [sx * 395, -720], [sx * 370, -770], [sx * 290, -690], [sx * 160, -585]]);
      fillStroke(g, r.tuy, L, lw);
      g.beginPath(); g.moveTo(sx * 300, -560); g.lineTo(sx * 360, -705); g.lineTo(sx * 250, -610); fillStroke(g, r.tuyKoyu);
    }
    // head
    const head = [[-300, -580], [-150, -628], [0, -636], [150, -628], [300, -580], [352, -440], [345, -255], [292, -118], [168, -38], [0, -12], [-168, -38], [-292, -118], [-345, -255], [-352, -440]];
    blob(g, head); fillStroke(g, r.tuy); this._cel(g, -360, 360, li, .24); fillStroke(g, null, L, lw * 1.15);
    // chest/neck feather scallops under the head
    g.strokeStyle = rgba(r.tuyKoyu, .9); g.lineWidth = lw * .55;
    for (let i = -2; i <= 2; i++) { g.beginPath(); g.arc(i * 70, -70, 34, .2, Math.PI - .2); g.stroke(); }
    // facial discs
    for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(sx * 122, -360, 172, 160, 0, 0, 7); fillStroke(g, r.disk); }
    g.save(); g.beginPath(); g.ellipse(-122, -360, 172, 160, 0, 0, 7); g.ellipse(122, -360, 172, 160, 0, 0, 7); g.clip();
    this._cel(g, -300, 300, li, .12); g.restore();
    for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(sx * 122, -360, 172, 160, 0, sx > 0 ? -2.2 : -4.08 + 3.1, sx > 0 ? 2.0 : 5.2 - 3.1); }
    g.strokeStyle = r.diskKenar; g.lineWidth = lw * .9;
    g.beginPath(); g.ellipse(-122, -360, 172, 160, 0, 1.75, 5.15); g.stroke();
    g.beginPath(); g.ellipse(122, -360, 172, 160, 0, -2.0, 1.4); g.stroke();
    // disc feather ticks
    g.lineWidth = lw * .4;
    for (const sx of [-1, 1]) for (let a = 0; a < 6.28; a += .32) {
      const c = Math.cos(a), s = Math.sin(a); if (sx * c < -.35) continue;
      g.beginPath(); g.moveTo(sx * 122 + c * 140, -360 + s * 130); g.lineTo(sx * 122 + c * 160, -360 + s * 150); g.stroke();
    }
    // forehead V ridge
    g.beginPath(); g.moveTo(-70, -520); g.quadraticCurveTo(0, -470, 70, -520); g.lineTo(18, -300); g.lineTo(-18, -300); g.closePath(); fillStroke(g, r.tuy);
    this._eyes(g, st, ex, 122, -372, 86, 86, r.iris, true);
    this._brows(g, ex, 122, -505, 150, r.tuyKoyu, true);
    // beak (talk opens the lower mandible)
    const o = clamp((st.talk || 0) * .9 + ex.open * .5);
    if (o > .02) { blob(g, [[-36, -262], [36, -262], [30, -205 + o * 70], [0, -190 + o * 80], [-30, -205 + o * 70]]); fillStroke(g, '#3a1d17', L, lw * .7); }
    blob(g, [[-30, -222 + o * 62], [30, -222 + o * 62], [0, -186 + o * 80]]); fillStroke(g, shade(r.gaga, .85), L, lw * .7);
    blob(g, [[-48, -300], [0, -322], [48, -300], [28, -236], [0, -198], [-28, -236]]); fillStroke(g, r.gaga, L, lw * .85);
    g.beginPath(); g.moveTo(-12, -296); g.quadraticCurveTo(0, -304, 12, -296); fillStroke(g, null, shade(r.gaga, .6), lw * .5);
    // mood in the beak corners: a tiny smile / frown line under the discs
    const m = ex.mouth;
    if (Math.abs(m) > .2) for (const sx of [-1, 1]) { g.beginPath(); g.moveTo(sx * 52, -250); g.quadraticCurveTo(sx * 70, -250 - m * 14, sx * 84, -258 - m * 22); fillStroke(g, null, L, lw * .55); }
  }
  _hogHead(g, st, ex) {
    const r = this.r, L = this.line, lw = this.lw, li = st.light ?? 1;
    // crown of spines behind the face
    const sp = [];
    const N = 15;
    for (let i = 0; i <= N; i++) {
      const a = Math.PI * (1.08 + i / N * .84);               // from left cheek over the top to the right cheek
      const R1 = 330, R2 = 470 + ((i % 3) - 1) * 26;
      const a2 = a + Math.PI / N / 2;
      sp.push([Math.cos(a) * R1, -360 + Math.sin(a) * R1 * .92]);
      if (i < N) sp.push([Math.cos(a2) * R2, -360 + Math.sin(a2) * R2 * .95]);
    }
    sp.push([300, -170], [0, -120], [-300, -170]);
    g.beginPath(); sp.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath();
    g.lineJoin = 'round'; fillStroke(g, r.diken); this._cel(g, -480, 480, li, .25); fillStroke(g, null, L, lw);
    g.strokeStyle = r.dikenAcik; g.lineWidth = lw * .55;
    for (let i = 0; i < N; i++) { const a = Math.PI * (1.08 + (i + .5) / N * .84); g.beginPath(); g.moveTo(Math.cos(a) * 340, -360 + Math.sin(a) * 315); g.lineTo(Math.cos(a) * 425, -360 + Math.sin(a) * 400); g.stroke(); }
    // ears
    for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(sx * 228, -560, 62, 58, sx * .3, 0, 7); fillStroke(g, r.yuz, L, lw); g.beginPath(); g.ellipse(sx * 228, -556, 32, 30, sx * .3, 0, 7); fillStroke(g, r.kulak); }
    // face
    const face = [[-250, -560], [-120, -625], [0, -635], [120, -625], [250, -560], [312, -420], [305, -270], [240, -150], [110, -72], [0, -60], [-110, -72], [-240, -150], [-305, -270], [-312, -420]];
    blob(g, face); fillStroke(g, r.yuz); this._cel(g, -320, 320, li, .18);
    // spine fringe on the forehead
    g.beginPath(); g.moveTo(-200, -585);
    for (let i = 0; i <= 8; i++) { const x = -200 + i * 50; g.lineTo(x + 25, -535 + (i % 2) * 12); g.lineTo(x + 50, -598 + Math.abs(i - 4) * 5); }
    g.lineTo(220, -640); g.lineTo(-220, -640); g.closePath(); fillStroke(g, r.diken);
    blob(g, face); fillStroke(g, null, L, lw * 1.15);
    // blush
    const bl = .45 + (ex.blush || 0);
    for (const sx of [-1, 1]) { g.beginPath(); g.ellipse(sx * 185, -255, 62, 30, 0, 0, 7); g.fillStyle = rgba(r.allik, bl * .7); g.fill(); }
    for (const sx of [-1, 1]) for (let k = 0; k < 3; k++) { g.beginPath(); g.moveTo(sx * (160 + k * 22), -262); g.lineTo(sx * (150 + k * 22), -240); fillStroke(g, null, rgba(shade(r.allik, .6), .7), lw * .4); }
    this._eyes(g, st, ex, 104, -360, 70, 82, '#3b2a20', false);
    this._brows(g, ex, 104, -470, 95, r.diken, false);
    // snout + nose
    g.beginPath(); g.ellipse(0, -225, 92, 62, 0, 0, 7); fillStroke(g, mix(r.yuz, '#ffffff', .25));
    g.beginPath(); g.ellipse(0, -258, 36, 26, 0, 0, 7); fillStroke(g, r.burun, L, lw * .6);
    g.beginPath(); g.ellipse(-10, -266, 11, 7, -.3, 0, 7); g.fillStyle = 'rgba(255,255,255,.75)'; g.fill();
    // mouth
    const o = clamp((st.talk || 0) + ex.open);
    const m = ex.mouth, w = 46;
    if (o > .06) {
      blob(g, [[-w, -205 - m * 8], [0, -200 + m * 10], [w, -205 - m * 8], [w * .7, -190 + o * 50], [0, -180 + o * 62], [-w * .7, -190 + o * 50]]);
      fillStroke(g, '#4a1f1d', L, lw * .75);
      g.save(); g.clip(); g.beginPath(); g.ellipse(0, -172 + o * 62, 34, 22, 0, 0, 7); g.fillStyle = '#c9706a'; g.fill(); g.restore();
    } else {
      g.beginPath(); g.moveTo(-w, -203 - m * 14); g.quadraticCurveTo(0, -203 + m * 26, w, -203 - m * 14); fillStroke(g, null, L, lw * .8);
    }
    g.beginPath(); g.moveTo(0, -232); g.lineTo(0, -210 + m * 4); fillStroke(g, null, L, lw * .55);
  }

  // eyes: sclera (kirpi) or full amber disc (baykuş), pupil + highlight, upper lid closing from the top
  _eyes(g, st, ex, dx, cy, rx, ry, iris, owl) {
    const L = this.line, lw = this.lw, r = this.r;
    const shut = clamp(Math.max(ex.lid, 0) + (st.blink || 0) * (1 - ex.lid));
    const gx = (st.gazeX ?? ex.gx) * rx * .32, gy = (st.gazeY ?? ex.gy) * ry * .3;
    for (const sx of [-1, 1]) {
      const x = sx * dx;
      g.save();
      g.beginPath(); g.ellipse(x, cy, rx, ry, 0, 0, 7);
      if (owl) { fillStroke(g, iris); }
      else fillStroke(g, '#fbf7ef');
      g.clip();
      if (owl) {
        g.beginPath(); g.arc(x + gx, cy + gy, rx * .42 * ex.pupil, 0, 7); g.fillStyle = '#1f120c'; g.fill();
        g.beginPath(); g.arc(x, cy, rx * .78, 0, 7); g.strokeStyle = rgba(shade(iris, .7), .6); g.lineWidth = lw * .5; g.stroke();
      } else {
        g.beginPath(); g.arc(x + gx, cy + gy + 6, rx * .7 * ex.pupil, 0, 7); g.fillStyle = iris; g.fill();
        g.beginPath(); g.arc(x + gx, cy + gy + 6, rx * .44 * ex.pupil, 0, 7); g.fillStyle = '#140b07'; g.fill();
      }
      g.beginPath(); g.arc(x + gx - rx * .22, cy + gy - ry * .22, rx * .16, 0, 7); g.fillStyle = 'rgba(255,255,255,.95)'; g.fill();
      g.beginPath(); g.arc(x + gx + rx * .18, cy + gy + ry * .12, rx * .07, 0, 7); g.fill();
      // upper lid: a flat-bottomed shape coming down, its edge tilted by the expression
      if (shut > .01) {
        const yEdge = cy - ry + shut * 2 * ry, tilt = ex.tilt * ry * .55;
        const yi = yEdge + tilt, yo = yEdge - tilt * .4;               // inner / outer corner
        const xi = x - sx * rx * 1.1, xo = x + sx * rx * 1.1;
        g.beginPath(); g.moveTo(xi, cy - ry * 1.3); g.lineTo(xo, cy - ry * 1.3); g.lineTo(xo, yo); g.quadraticCurveTo(x, (yi + yo) / 2 + ry * .1 * (1 - shut), xi, yi); g.closePath();
        g.fillStyle = owl ? r.tuy : r.yuzKoyu; g.fill();
        g.beginPath(); g.moveTo(xo, yo); g.quadraticCurveTo(x, (yi + yo) / 2 + ry * .1 * (1 - shut), xi, yi); g.strokeStyle = L; g.lineWidth = lw * 1.1; g.stroke();
      }
      g.restore();
      g.beginPath(); g.ellipse(x, cy, rx, ry, 0, 0, 7); g.strokeStyle = L; g.lineWidth = lw * (owl ? .9 : 1); g.stroke();
      if (!owl && shut < .9) {   // lashes
        g.beginPath(); g.moveTo(x + sx * rx * .9, cy - ry * .5); g.lineTo(x + sx * rx * 1.18, cy - ry * .72); g.stroke();
      }
    }
  }
  _brows(g, ex, dx, y, len, col, owl) {
    const L = this.line, lw = this.lw;
    for (const sx of [-1, 1]) {
      const xi = sx * (dx - len * .5), xo = sx * (dx + len * .5);
      const yi = y + ex.brow + ex.btilt * 40, yo = y + ex.brow - ex.btilt * 22;
      g.beginPath(); g.moveTo(xi, yi); g.quadraticCurveTo(sx * dx, Math.min(yi, yo) - 26, xo, yo);
      g.strokeStyle = L; g.lineWidth = lw * (owl ? 3.2 : 2.6); g.lineCap = 'round'; g.stroke();
      g.strokeStyle = col; g.lineWidth = lw * (owl ? 1.5 : 1.1); g.stroke();
    }
  }

  // ---------------------------------------------------------------- arms
  _arms(g, st) {
    const pose = st.pose || 'yan';
    const P = {
      yan:     { L: [[-395, 150], [-455, 520], [-420, 880]], R: [[395, 150], [455, 520], [420, 880]] },
      masa:    { L: [[-395, 150], [-430, 560], [-140, 640]], R: [[395, 150], [430, 560], [140, 655]] },
      el:      { L: [[-395, 150], [-430, 560], [-140, 640]], R: [[395, 150], [420, 560], [300, 210]] },
      cene:    { L: [[-395, 150], [-430, 560], [-140, 640]], R: [[395, 150], [330, 560], [110, -110]] },
      telefon: { L: [[-395, 150], [-420, 560], [-95, 560]], R: [[395, 150], [420, 560], [95, 575]] },
    }[pose] || null;
    if (!P) return;
    const sleeve = this.tur === 'baykus' ? this.r.ceket : this.r.kazak;
    if (pose === 'telefon') this._phone(g);
    for (const side of ['L', 'R']) {
      const [a, b, c] = P[side];
      g.beginPath(); g.moveTo(a[0], a[1]); g.quadraticCurveTo(b[0], b[1], c[0], c[1]);
      g.strokeStyle = this.line; g.lineWidth = 128 + this.lw * 2; g.lineCap = 'round'; g.stroke();
      g.strokeStyle = sleeve; g.lineWidth = 128; g.stroke();
      // fold lines at the elbow
      g.beginPath(); g.moveTo(b[0] * .96 - 30, b[1] - 20); g.quadraticCurveTo(b[0] * .96, b[1], b[0] * .96 + 30, b[1] - 10);
      g.strokeStyle = rgba(this.line, .5); g.lineWidth = this.lw * .6; g.stroke();
      // cuff + hand
      const ang = Math.atan2(c[1] - b[1], c[0] - b[0]);
      const hx = c[0] + Math.cos(ang) * 70, hy = c[1] + Math.sin(ang) * 70;
      g.save(); g.translate(c[0], c[1]); g.rotate(ang);
      rrect(g, -10, -70, 40, 140, 14); fillStroke(g, shade(sleeve, .85), this.line, this.lw * .8);
      g.restore();
      const open = (pose === 'el' && side === 'R');
      this._hand(g, hx, hy, ang, side === 'L' ? -1 : 1, open);
    }
  }
  _hand(g, x, y, ang, sx, open) {
    const col = this.r.el, L = this.line, lw = this.lw;
    g.save(); g.translate(x, y); g.rotate(open ? -Math.PI / 2 : ang);
    if (open) {
      rrect(g, -60, -40, 120, 110, 50); fillStroke(g, col, L, lw);
      for (let i = 0; i < 4; i++) { rrect(g, -58 + i * 30, -110, 28, 90, 14); fillStroke(g, col, L, lw * .8); }
      g.beginPath(); g.ellipse(sx * 70, 10, 26, 44, sx * .6, 0, 7); fillStroke(g, col, L, lw * .8);
    } else {
      g.beginPath(); g.ellipse(14, 0, 70, 58, 0, 0, 7); fillStroke(g, col, L, lw);
      g.beginPath(); g.ellipse(10, -sx * 46, 34, 22, -sx * .4, 0, 7); fillStroke(g, col, L, lw * .8);
      g.strokeStyle = rgba(L, .7); g.lineWidth = lw * .5;
      for (const k of [-18, 8, 34]) { g.beginPath(); g.moveTo(60, k - 6); g.lineTo(78, k); g.stroke(); }
      if (this.tur === 'baykus') { g.fillStyle = rgba(this.r.tuyKoyu, .6); for (const k of [-20, 0, 20]) { g.beginPath(); g.ellipse(-20, k, 18, 8, 0, 0, 7); g.fill(); } }
    }
    g.restore();
  }
  _phone(g) {
    g.save(); g.translate(0, 470); g.rotate(-.04);
    rrect(g, -100, -170, 200, 330, 28); fillStroke(g, '#2b2622', this.line, this.lw);
    rrect(g, -84, -152, 168, 290, 18); g.fillStyle = '#e6dccb'; g.fill();
    const gr = g.createRadialGradient(0, -20, 10, 0, -20, 260); gr.addColorStop(0, 'rgba(255,240,210,.55)'); gr.addColorStop(1, 'rgba(255,240,210,0)');
    g.globalCompositeOperation = 'lighter'; g.fillStyle = gr; g.fillRect(-300, -400, 600, 700); g.globalCompositeOperation = 'source-over';
    g.restore();
  }
}
