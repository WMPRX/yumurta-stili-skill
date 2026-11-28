// main.js — loads a story, exposes window.render(t) for frame-exact capture (no realtime clock).
// URL: /engine/index.html?story=<name>[&scale=0.5][&nocap=1]
//
// A story (stories/<name>/story.js) exports:
//   NAME, FPS (30), BRAND { ad: 'KANAL ADI' }, CAST { <SPEAKER TAG>: { tur: 'baykus' | 'kirpi', renk: {...} } }
//   build({ W, L, words, lines }) -> { shots: [...], expr: [...], poz: [...], end: { at }, look: {...} }
//     W('kelime', n)  start time of the n-th occurrence of a word (Turkish-aware, punctuation ignored)
//     L(i)            { start, end, spk, text } of script line i (0-based)
//   A shot: { at, set: 'kafe'|'sokak'|'oda', kind: 'ikili'|'tek'|'yakin'|'genis'|'nesne', who, ots, prop, opts, push, focus, flash: [t] }
//   An expression event: { at, who, expr }   A pose event: { at, who, pose }
import { Character } from './chars.js';
import { SETS, PAD, SPAN, backdrop } from './sets.js';
import { PROPS } from './props.js';
import { snow, rain, dust, glow, beam, flash } from './fx.js';
import { Post, LOOK } from './post.js';
import { captionTimeline, drawCaption, drawWatermark, drawTitle } from './overlay.js';
import { easeShot, smooth, clamp, blinkAt, canvas, hash } from './util.js';

const q = new URLSearchParams(location.search);
const STORY = q.get('story') || 'ornek';
const SCALE = parseFloat(q.get('scale') || '1');
const W = Math.round(1080 * SCALE / 2) * 2, H = Math.round(1920 * SCALE / 2) * 2, K = W / 1080;

try {
  await document.fonts.load(`40px Bangers`); await document.fonts.load(`600 40px Cinzel`);
  const base = `/stories/${STORY}/`;
  const story = await import(base + 'story.js');
  const FPS = story.FPS || 30;
  const voice = await (await fetch(base + 'voice/words.json')).json();
  const env = await fetch(base + 'voice/env.json').then(r => r.ok ? r.json() : []).catch(() => []);
  const words = voice.words, lines = voice.lines || [];
  const norm = s => s.toLocaleLowerCase('tr-TR').replace(/[^\p{L}\p{N}']/gu, '');
  const Wf = (w, n = 1) => { const hits = words.filter(x => norm(x.word) === norm(w)); if (!hits[n - 1]) throw new Error(`W('${w}', ${n}): kelime yok / word not found`); return hits[n - 1].start; };
  const Lf = i => { if (!lines[i]) throw new Error(`L(${i}): satır yok / no such line`); return lines[i]; };
  const plan = story.build({ W: Wf, L: Lf, words, lines });

  const cast = {}; for (const [tag, look] of Object.entries(story.CAST)) cast[tag] = new Character(look);
  const tags = Object.keys(cast);
  const mentor = story.MENTOR || tags[0], student = tags.find(t => t !== mentor) || tags[0];
  const lastWord = words[words.length - 1];
  const tE = plan.end?.at ?? Math.max(0, lastWord.end - 3);
  const DUR = plan.dur || Math.max(lastWord.end + 2.8, tE + 9.2);
  const shots = plan.shots.slice().sort((a, b) => a.at - b.at).map((s, i, A) => ({ ...s, a: i ? s.at : 0, b: A[i + 1] ? A[i + 1].at : DUR }));
  const exprEv = (plan.expr || []).slice().sort((a, b) => a.at - b.at);
  const poseEv = (plan.poz || []).slice().sort((a, b) => a.at - b.at);
  const swaps = Object.fromEntries(tags.map(t => [t, exprEv.filter(e => e.who === t).map(e => e.at)]));
  const caps = captionTimeline(words);

  const out = document.getElementById('out'), glc = document.getElementById('gl');
  out.width = W; out.height = H;
  const o = out.getContext('2d');
  const sc = canvas(W, H), g = sc.getContext('2d');
  const tmp = canvas(W, H), tg = tmp.getContext('2d');
  const post = new Post(glc, W, H);

  const exprOf = (who, t) => { let e = null; for (const x of exprEv) { if (x.who === who && x.at - 2 / FPS <= t) e = x.expr; } return e; };
  const poseOf = (who, t, s) => { let p = s.pose?.[who] ?? ((s.kind === 'ikili' || s.kind === 'genis') && s.set !== 'sokak' ? 'masa' : 'yan'); for (const x of poseEv) if (x.who === who && x.at - 2 / FPS <= t && x.at >= s.a - .01) p = x.pose; return p; };
  const speakerAt = t => { const w = words.find(w => t >= w.start - .04 && t < w.end + .04); return w ? w.spk : null; };
  const talkAt = (who, t) => {
    if (speakerAt(t) !== who) return 0;
    const f = Math.floor(t * FPS / 2) * 2;                                   // mouth shapes held two frames
    const e = env.length ? (env[Math.min(env.length - 1, f)] || 0) : (.5 + .5 * Math.sin(t * 22));
    return e < .12 ? 0 : e < .45 ? .5 : 1;
  };

  // composition per shot kind: where the characters stand and how the backdrop is viewed
  const SIDE = { [mentor]: .30, [student]: .70 };
  function layout(s) {
    if (s.kind === 'ikili' || s.kind === 'genis') {
      const cs = s.kind === 'genis' ? .66 : 1;
      return { cs, bg: { zoom: 1, cu: .5, cv: .5, blur: 3 }, chars: tags.map(t => ({ who: t, u: SIDE[t] ?? .5, v: .565, head: .27 })) };
    }
    const close = s.kind === 'yakin';
    const head = close ? .88 : .58, eyeV = close ? .40 : .42;
    return { cs: 1, bg: { zoom: close ? 2.2 : 1.7, cu: SIDE[s.who] ?? .5, cv: .33, blur: close ? 20 : 14 }, chars: [{ who: s.who, u: .5, eyeV, head }] };
  }

  function drawShot(s, t) {
    const u = (t - s.a) / Math.max(.001, s.b - s.a);
    let z = 1 + (s.push ?? .036) * easeShot(u);
    if (t > tE && s === shots[shots.length - 1]) z *= 1 - .07 * smooth((t - tE) / 5);
    const [fu, fv] = s.focus || (s.kind === 'tek' || s.kind === 'yakin' ? [.5, .42] : [.5, .5]);
    const cam = (p = 1) => { const zz = Math.pow(z, p); g.translate(fu * W, fv * H); g.scale(zz, zz); g.translate(-fu * W, -fv * H); };
    g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#120c09'; g.fillRect(0, 0, W, H);

    if (s.kind === 'nesne') {
      g.save(); cam(1);
      const fn = typeof s.prop === 'function' ? s.prop : PROPS[s.prop];
      if (!fn) throw new Error(`prop "${s.prop}" yok`);
      fn(g, t - s.a, W, H, s.opts || {}, { cast, t });
      g.restore();
      if (s.fx === 'yagmur') rain(g, t, W, H);
      return;
    }
    const set = SETS[s.set]; if (!set) throw new Error(`set "${s.set}" yok`);
    const L = layout(s);
    const comp = () => { g.translate(W * .5, H * .5); g.scale(L.cs, L.cs); g.translate(-W * .5, -H * .5); };
    // backdrop (cached + blurred), parallax 0.6
    const bd = backdrop(s.set, W, H, Math.round(L.bg.blur * K));
    g.save(); cam(.6); comp();
    const bz = L.bg.zoom, bw = W * SPAN * bz, bh = H * SPAN * bz;
    const ox = W * .5 - (L.bg.cu + PAD) / SPAN * bw, oy = H * .4 - (L.bg.cv + PAD) / SPAN * bh;
    const fx = L.bg.zoom === 1 ? -PAD * W : ox, fy = L.bg.zoom === 1 ? -PAD * H : oy;
    g.drawImage(bd, fx, fy, bw, bh);
    const toS = (lu, lv) => [fx + (lu + PAD) / SPAN * bw, fy + (lv + PAD) / SPAN * bh];
    for (const li of set.lights || []) {
      const [x, y] = toS(li.u, li.v);
      if (li.beam) { const [x1, y1] = toS(li.beam.to[0], li.beam.to[1]); beam(g, x, y, x1, y1, li.beam.w * W * bz, li.col, .13); }
      glow(g, x, y, li.r * W * bz, li.col, li.a * (1 + .03 * Math.sin(t * 9 + hash(li.u) * 6)));
    }
    g.restore();
    // characters: body, foreground, arms
    const lightU = (set.lights?.[0]?.u ?? .5);
    const states = L.chars.map(c => {
      const ch = cast[c.who], sPx = c.head * W / 660;
      const y = c.eyeV !== undefined ? c.eyeV * H + (ch.tur === 'baykus' ? 372 : 360) * sPx : c.v * H;
      const other = c.who === mentor ? 1 : -1;
      const ex = exprOf(c.who, t);
      return { ch, who: c.who, st: { x: c.u * W, y, s: sPx, k: K, expr: ex || undefined, talk: talkAt(c.who, t), blink: blinkAt(t, 1 + tags.indexOf(c.who) * 7, swaps[c.who], FPS),
        gazeX: ex === 'dusunceli' ? undefined : (L.chars.length > 1 ? .38 * other : .14 * other), pose: poseOf(c.who, t, s), light: lightU > c.u ? 1 : -1 } };
    });
    g.save(); cam(1); comp();
    for (const c of states) c.ch.body(g, c.st);
    set.fore(g, W, H, K, s.kind);
    for (const c of states) c.ch.arms(g, c.st);
    g.restore();
    // over-the-shoulder foreground: the other character, large and out of focus, in a lower corner (parallax 1.15)
    if (s.ots && (s.kind === 'tek' || s.kind === 'yakin')) {
      const ch = cast[s.ots], side = (SIDE[s.ots] ?? .3) < .5 ? -1 : 1;
      tg.setTransform(1, 0, 0, 1, 0, 0); tg.clearRect(0, 0, W, H);
      const sPx = .95 * W / 660;                                              // only a shoulder and the edge of the head show
      ch.body(tg, { x: W * (.5 + side * .8), y: H * 1.02, s: sPx, k: K, expr: exprOf(s.ots, t) || undefined, light: -side, pose: 'yan' });
      g.save(); cam(1.15); g.filter = `blur(${Math.round(16 * K)}px)`; g.globalAlpha = .96; g.drawImage(tmp, 0, 0); g.restore();
    }
    // particles
    const fxk = s.fx ?? set.fx;
    if (fxk === 'kar') snow(g, t, W, H, { seed: 3 + shots.indexOf(s) });
    if (fxk === 'yagmur') rain(g, t, W, H);
    if (fxk === 'toz') dust(g, t, W, H, { cx: .5, cy: .25 });
    return states;
  }

  function endEyes(states, t) {             // the mentor's eyes glow in the dark
    const m = states?.find(c => c.who === mentor); if (!m) return;
    const a = smooth((t - tE - 1.2) / 2.4); if (a <= 0) return;
    const [[x1, y1], [x2, y2], r] = m.ch.eyes(m.st);
    g.save();
    for (const [x, y] of [[x1, y1], [x2, y2]]) {
      glow(g, x, y, r * 2.6, '#ffb45a', .5 * a);
      g.save(); g.beginPath(); g.ellipse(x, y + r * .25, r * .95, r * .5, 0, 0, Math.PI * 2); g.clip();
      const gr = g.createRadialGradient(x, y + r * .1, 0, x, y + r * .1, r); gr.addColorStop(0, `rgba(255,236,190,${a})`); gr.addColorStop(1, `rgba(236,170,80,${a})`);
      g.fillStyle = gr; g.fillRect(x - r, y - r, 2 * r, 2 * r);
      g.beginPath(); g.ellipse(x, y + r * .3, r * .2, r * .32, 0, 0, 7); g.fillStyle = `rgba(40,20,8,${a})`; g.fill();
      g.restore();
    }
    g.restore();
  }

  window.render = t => {
    const s = shots.find(s => t >= s.a && t < s.b) || shots[shots.length - 1];
    const states = drawShot(s, t);
    const look = { ...LOOK, ...(plan.look || {}), ...(s.look || {}) };
    const fl = flash(t, s.flash || []); if (fl) look.exposure = (look.exposure || 1) * (1 + fl * .9);
    if (t > tE) {                                                            // end card: lights go down, eyes stay
      const d = smooth((t - tE) / 4) * .9;
      g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = `rgba(8,5,3,${d})`; g.fillRect(0, 0, W, H);
      endEyes(states, t);
    }
    look.dim = clamp((t - (DUR - 1.3)) / .8);
    post.render(sc, Math.round(t * FPS), look);
    o.setTransform(1, 0, 0, 1, 0, 0); o.drawImage(glc, 0, 0);
    const titleA = smooth((t - tE - 4.2) / .6) * (1 - look.dim);
    if (!q.has('nocap')) {
      drawWatermark(o, story.BRAND?.ad, W, H, 1 - smooth((t - tE - 3.6) / .6));
      drawCaption(o, caps, t, W, H);
    }
    drawTitle(o, story.BRAND?.ad, W, H, titleA);
    if (story.overlay) story.overlay(o, t, { W, H });
  };
  window.__meta = { DUR, FPS, NAME: story.NAME || STORY, W, H, SHOTS: shots.map(({ a, b, kind, set, who }) => ({ a, b, kind, set: set || null, who: who || null })),
    CUES: { DUR, FPS, end: tE, shots: shots.map(({ a, b, kind, set, flash }) => ({ a, b, kind, set: set || null, flash: flash || [] })),
            lines: lines.map(l => ({ start: l.start, end: l.end, spk: l.spk })), music: story.MUSIC || {} } };
  window.__ready = true;
  if (!q.has('capture')) { const t0 = performance.now(); const loop = () => { window.render(((performance.now() - t0) / 1000) % DUR); requestAnimationFrame(loop); }; loop(); }
} catch (e) { console.error(e); window.__error = String(e && e.stack || e); }
