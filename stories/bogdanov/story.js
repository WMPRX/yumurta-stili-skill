// Bogdanov — Gençlik Kanıyla Ölümsüzlüğü Arayan Doktor.
// Story: in 1920s Moscow Alexander Bogdanov swaps blood with young volunteers to stop ageing; the 12th exchange, with a
// student who had malaria and tuberculosis, kills him (1928, aged 54). He notes his own symptoms until the end.
// Sets: LAB (x≈0: the transfusion room, two beds, the hanging lamp, the clock, the calendar, the chalkboard),
//       STREET (x≈200: the institute's façade in the Moscow snow), TUBE (x≈300: inside the glass tube, the blood cells).
// Every cue is pinned to a word of voice/words.json (W('word', n) = start of the n-th match).
// Light, per set (the style: the source is IN the picture, warm against cool, real cast shadows):
//   lab     the enamel lamp over the beds (warm key, shadows) against the blue snow-light from the window; the
//           bedside lamp is the second warm pool and the key of the last shot, then it goes out: only the moon is left
//   street  the street lamp (warm key, shadows on the snow) against the blue night; the sign's bulbs, warm windows
//   tube    the lamp seen through the glass at the end of the tube (warm) against the cool glass walls
import * as THREE from 'three';
import { stoneTex, woodTex, painted, flat, rng, D, shade } from '/engine/src/paint.js';
import { Toon, Arm3D, PLUM, flap, blinkAt } from '/engine/src/toon.js';
import { CamPath, smoother } from '/engine/src/camera.js';
import { Smoke, beam, glow, addBlend } from '/engine/src/fx.js';
import { holedWall, vistaMat } from '/engine/src/vista.js';

export const NAME = 'bogdanov';
export const FPS = 30;
export let DUR = 50;      // recomputed in setup() from the last word
export const CUES = [];

const S = smoother;
const ramp = (t, a, b) => S((t - a) / (b - a));
const lin = (t, a, b) => Math.max(0, Math.min(1, (t - a) / (b - a)));
const lerpN = (a, b, k) => a + (b - a) * k;
const V = (...a) => new THREE.Vector3(...a);
const HDR = (r, g, b) => new THREE.Color().setRGB(r, g, b);
const DEG = Math.PI / 180;
const FONT = '"Inter", "DejaVu Sans", sans-serif';
const HAND = '"DejaVu Serif", serif';
const WIN_CAM = [0.4, 1.7, 3.4];          // the wide of the lab: the window's night view is aimed from here
const BED_A = -0.74, BED_B = 0.74, BED_Z = -2.36;   // the two beds (x), where the patients sit (z)
const backOut = x => x <= 0 ? 0 : x >= 1 ? 1 : 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2;
let W;
let cast = {}, sets = {}, smokes = {}, dyn = {};

function wordTimes(words) {
  const norm = s => s.toLocaleLowerCase('tr-TR').replace(/[^\p{L}\p{N}]/gu, '');
  return (w, n = 1) => { let k = 0; for (const x of words) if (norm(x.word) === norm(w) && ++k === n) return x.start; throw new Error('word not found: ' + w); };
}
function shadows(g) {
  g.traverse(o => {
    if (!o.isMesh || o.isInstancedMesh) return;
    if (o.material.isMeshLambertMaterial) o.receiveShadow = true;
    if (/Box|Cylinder|Extrude|Lathe|Torus|Sphere/.test(o.geometry.type) && !o.userData.noShadow) o.castShadow = true;
  });
}
function canvasTex(w, h, draw, { srgb = true } = {}) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g, w, h);
  const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.c = c; t.g = g; return t;
}
function dabs(g, w, h, base, n, r, amt, seed) {
  const R = rng(seed);
  for (let i = 0; i < n; i++) { g.fillStyle = shade(base, 1 + (R() - .5) * amt); g.globalAlpha = .25 + R() * .35; g.beginPath(); g.ellipse(R() * w, R() * h, r * (.4 + R()), r * (.2 + R() * .5), R() * 3.14, 0, 6.29); g.fill(); }
  g.globalAlpha = 1;
}
const box = (g, sx, sy, sz, x, y, z, m) => { const b = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), m); b.position.set(x, y, z); g.add(b); return b; };
const cyl = (g, r0, r1, h, x, y, z, m, seg = 16) => { const b = new THREE.Mesh(new THREE.CylinderGeometry(r0, r1, h, seg), m); b.position.set(x, y, z); g.add(b); return b; };

// ---------------------------------------------------------------- PAINTINGS
// Night over Moscow in the snow: violet sky, stars, a big moon, snowy roofs with lit windows, onion domes and a tent spire.
// Drawn flat with thin dark outlines. Used twice: as a panorama behind the lab window and as the street's backdrop.
function paintMoscow(g, w, h, { horizon = .66, moonX = .7 } = {}) {
  const R = rng(41), HY = h * horizon, INK = D('#1a1a44');
  let gr = g.createLinearGradient(0, 0, 0, HY); gr.addColorStop(0, D('#101650')); gr.addColorStop(.55, D('#2a3592')); gr.addColorStop(1, D('#7c6cc8'));
  g.fillStyle = gr; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 700; i++) { g.globalAlpha = .4 + R() * .6; g.fillStyle = R() < .2 ? D('#ffe6b8') : D('#eef2ff'); g.beginPath(); g.arc(R() * w, R() * HY * .8, .8 + R() * 1.8 * w / 2048, 0, 6.29); g.fill(); }
  g.globalAlpha = 1;
  const mx = w * moonX, my = h * .17, mr = w * .035;
  const halo = g.createRadialGradient(mx, my, mr * .8, mx, my, mr * 6); halo.addColorStop(0, 'rgba(220,230,255,.5)'); halo.addColorStop(.4, 'rgba(170,190,255,.15)'); halo.addColorStop(1, 'rgba(150,170,255,0)');
  g.fillStyle = halo; g.fillRect(0, 0, w, h);
  g.fillStyle = D('#fbf4dc'); g.beginPath(); g.arc(mx, my, mr, 0, 6.29); g.fill();
  g.fillStyle = D('#e6dcc0'); for (const [dx, dy, r] of [[-.3, -.2, .22], [.25, .3, .16], [.1, -.4, .1]]) { g.beginPath(); g.arc(mx + dx * mr, my + dy * mr, r * mr, 0, 6.29); g.fill(); }
  const U = w / 2048;
  // far row: domes and a tent spire
  const dome = (x, base, r, col, stripe) => {
    g.lineWidth = 2.2 * U; g.strokeStyle = INK;
    g.fillStyle = D('#d9d2e8'); g.fillRect(x - r * .7, base - r * 1.2, r * 1.4, r * 1.2); g.strokeRect(x - r * .7, base - r * 1.2, r * 1.4, r * 1.2);    // drum
    for (let k = -1; k <= 1; k++) { g.fillStyle = D('#f2c25a'); g.fillRect(x + k * r * .4 - r * .08, base - r * .95, r * .16, r * .5); }
    const top = base - r * 1.2;
    g.beginPath(); g.moveTo(x - r * .75, top); g.bezierCurveTo(x - r * 1.25, top - r * .9, x - r * .2, top - r * 1.4, x, top - r * 2.25);
    g.bezierCurveTo(x + r * .2, top - r * 1.4, x + r * 1.25, top - r * .9, x + r * .75, top); g.closePath();
    g.fillStyle = D(col); g.fill(); g.stroke();
    if (stripe) { g.save(); g.clip(); g.strokeStyle = D(stripe); g.lineWidth = r * .22; for (let k = -3; k <= 3; k++) { g.beginPath(); g.moveTo(x + k * r * .4 - r, top + r * .2); g.quadraticCurveTo(x + k * r * .2, top - r, x + k * r * .05, top - r * 2.3); g.stroke(); } g.restore(); g.strokeStyle = INK; g.lineWidth = 2.2 * U; g.beginPath(); g.moveTo(x - r * .75, top); g.bezierCurveTo(x - r * 1.25, top - r * .9, x - r * .2, top - r * 1.4, x, top - r * 2.25); g.bezierCurveTo(x + r * .2, top - r * 1.4, x + r * 1.25, top - r * .9, x + r * .75, top); g.stroke(); }
    g.fillStyle = D('#ffffff'); g.globalAlpha = .9; g.beginPath(); g.ellipse(x - r * .25, top - r * .7, r * .5, r * .18, -.3, 0, 6.29); g.fill(); g.globalAlpha = 1;   // snow on the dome
    g.strokeStyle = D('#f2c25a'); g.lineWidth = 3 * U; g.beginPath(); g.moveTo(x, top - r * 2.25); g.lineTo(x, top - r * 2.9); g.moveTo(x - r * .22, top - r * 2.6); g.lineTo(x + r * .22, top - r * 2.6); g.stroke();
  };
  const tent = (x, base, r) => {
    g.lineWidth = 2.2 * U; g.strokeStyle = INK; g.fillStyle = D('#c84a4a'); g.fillRect(x - r, base - r * 2.6, r * 2, r * 2.6); g.strokeRect(x - r, base - r * 2.6, r * 2, r * 2.6);
    g.fillStyle = D('#f3e9d6'); for (let k = 0; k < 3; k++) g.fillRect(x - r * .75 + k * r * .6, base - r * 2.2, r * .3, r * .55);
    g.beginPath(); g.moveTo(x - r * 1.1, base - r * 2.6); g.lineTo(x, base - r * 6.4); g.lineTo(x + r * 1.1, base - r * 2.6); g.closePath(); g.fillStyle = D('#2f8f7a'); g.fill(); g.stroke();
    g.fillStyle = D('#ffffff'); g.globalAlpha = .85; g.beginPath(); g.moveTo(x - r * .9, base - r * 3); g.lineTo(x - r * .1, base - r * 6); g.lineTo(x - r * .2, base - r * 3); g.closePath(); g.fill(); g.globalAlpha = 1;
    g.fillStyle = D('#ffcf5a'); g.beginPath(); g.arc(x, base - r * 6.6, r * .25, 0, 6.29); g.fill(); g.stroke();
  };
  const fb = HY + h * .02;
  tent(w * .2, fb, 26 * U);
  dome(w * .36, fb, 34 * U, '#3fae9e', '#f2ead0'); dome(w * .43, fb + 6 * U, 22 * U, '#e8b84a'); dome(w * .3, fb + 8 * U, 18 * U, '#3b62c4');
  dome(w * .56, fb, 40 * U, '#d8443e', '#f4e6c8'); dome(w * .63, fb + 6 * U, 24 * U, '#e8b84a'); tent(w * .85, fb, 22 * U); dome(w * .92, fb + 6 * U, 26 * U, '#3fae9e');
  dome(w * .08, fb + 4 * U, 28 * U, '#e8b84a'); dome(w * .75, fb + 10 * U, 16 * U, '#3b62c4');
  // near row: snowy roofs and walls with lit windows
  let x = -20 * U;
  while (x < w) {
    const bw = (80 + R() * 120) * U, bh = (60 + R() * 70) * U, top = h * .78 - bh * .3 - R() * 30 * U;
    const wall = ['#8a7fb8', '#7a8ac8', '#9a86b0', '#6e7cb8'][Math.floor(R() * 4)];
    g.fillStyle = D(wall); g.fillRect(x, top, bw, h - top); g.strokeStyle = INK; g.lineWidth = 2 * U; g.strokeRect(x, top, bw, h - top);
    g.beginPath(); g.moveTo(x - 8 * U, top); g.lineTo(x + bw / 2, top - bw * .28); g.lineTo(x + bw + 8 * U, top); g.closePath(); g.fillStyle = D('#f4f6ff'); g.fill(); g.stroke();
    for (let wy = top + 16 * U; wy < h - 20 * U; wy += 34 * U) for (let wx = x + 14 * U; wx < x + bw - 22 * U; wx += 30 * U) {
      const lit = R() < .45; g.fillStyle = lit ? D('#ffcf7a') : D('#3a3f7a'); g.fillRect(wx, wy, 13 * U, 18 * U); g.lineWidth = 1.4 * U; g.strokeRect(wx, wy, 13 * U, 18 * U);
    }
    x += bw + 6 * U;
  }
  g.fillStyle = D('#eef1ff'); g.fillRect(0, h * .93, w, h * .07);
}
function moscowTex() { return canvasTex(2048, 1024, (g, w, h) => paintMoscow(g, w, h, { horizon: .62, moonX: .38 })); }

// pale blue-grey plaster with a stencil-roller pattern (the walls of 1920s Moscow rooms): flat light motifs, thin outlines
function stencilTex({ base = '#9fb3cc', a = '#c3d2e6', b = '#e7b86a', rep = [1, 1] } = {}) {
  const t = canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = base; g.fillRect(0, 0, w, h); dabs(g, w, h, base, 260, 30, .1, 7);
    const ink = shade(base, .55);
    for (let y = 0; y < h; y += 128) for (let x = (y / 128 % 2) * 64; x < w + 64; x += 128) {
      g.fillStyle = a; g.strokeStyle = ink; g.lineWidth = 2;
      for (let k = 0; k < 4; k++) { const an = k * Math.PI / 2; g.beginPath(); g.ellipse(x + Math.cos(an) * 16, y + 64 + Math.sin(an) * 16, 14, 7, an, 0, 6.29); g.fill(); g.stroke(); }
      g.fillStyle = b; g.beginPath(); g.arc(x, y + 64, 6, 0, 6.29); g.fill(); g.stroke();
      g.fillStyle = a; g.beginPath(); g.moveTo(x + 64, y); g.lineTo(x + 70, y + 8); g.lineTo(x + 64, y + 16); g.lineTo(x + 58, y + 8); g.closePath(); g.fill(); g.stroke();
    }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); return t;
}
// glazed white wall tiles with a teal border row on top (a hospital dado)
function tilesTex({ rep = [1, 1] } = {}) {
  const t = canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#e8eef0'; g.fillRect(0, 0, w, h);
    const R = rng(3); for (let y = 0; y < h; y += 64) for (let x = 0; x < w; x += 64) { g.fillStyle = shade('#e8eef0', .93 + R() * .1); g.fillRect(x + 2, y + 2, 60, 60); g.fillStyle = 'rgba(255,255,255,.45)'; g.fillRect(x + 6, y + 6, 22, 5); }
    g.fillStyle = '#3f9a9a'; g.fillRect(0, 0, w, 64); g.fillStyle = '#2f7a86'; for (let x = 0; x < w; x += 64) { g.beginPath(); g.moveTo(x + 32, 10); g.lineTo(x + 54, 32); g.lineTo(x + 32, 54); g.lineTo(x + 10, 32); g.closePath(); g.fill(); }
    g.strokeStyle = '#8a9aa4'; g.lineWidth = 3; for (let k = 0; k <= w; k += 64) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k, h); g.moveTo(0, k); g.lineTo(w, k); g.stroke(); }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); return t;
}
function checkerTex({ a = '#c9553e', b = '#efe2c6', rep = [1, 1] } = {}) {
  const t = canvasTex(512, 512, (g, w, h) => {
    for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { g.fillStyle = (x + y) % 2 ? a : b; g.fillRect(x * 64, y * 64, 64, 64); }
    dabs(g, w, h, b, 200, 20, .12, 5);
    for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) if ((x + y) % 2) { g.fillStyle = a; g.globalAlpha = .55; g.fillRect(x * 64 + 3, y * 64 + 3, 58, 58); }
    g.globalAlpha = 1; g.strokeStyle = shade(b, .55); g.lineWidth = 2.5; for (let k = 0; k <= 512; k += 64) { g.beginPath(); g.moveTo(k, 0); g.lineTo(k, h); g.moveTo(0, k); g.lineTo(w, k); g.stroke(); }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(...rep); return t;
}
function blanketTex() {
  const t = canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#5f78b0'; g.fillRect(0, 0, w, h); dabs(g, w, h, '#5f78b0', 120, 14, .12, 9);
    for (const y of [40, 56, 190, 206]) { g.fillStyle = '#e9dfc4'; g.fillRect(0, y, w, 8); }
    g.strokeStyle = '#46598a'; g.lineWidth = 1.5; for (let x = 0; x < w; x += 10) { g.globalAlpha = .35; g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }
    g.globalAlpha = 1;
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
}

// ---------------------------------------------------------------- PROPS
// a glass vessel: a lathe of glass (pale, see-through) with a lathe of blood inside
function vessel(profile, fill, { glassCol = '#cfe6ff', blood = '#a3172a' } = {}) {
  const g = new THREE.Group();
  const P = profile.map(([r, y]) => new THREE.Vector2(r, y));
  const glass = new THREE.Mesh(new THREE.LatheGeometry(P, 32), new THREE.MeshLambertMaterial({ color: glassCol, transparent: true, opacity: .38, depthWrite: false, side: THREE.DoubleSide, emissive: '#4a5a7a' }));
  glass.renderOrder = 3; glass.userData.noShadow = true; g.add(glass);
  const top = profile[profile.length - 1][1] * fill + profile[0][1] * (1 - fill);
  const inner = profile.filter(([r, y]) => y <= top).map(([r, y]) => new THREE.Vector2(r * .9, y)); inner.push(new THREE.Vector2(inner[inner.length - 1].x, top)); inner.push(new THREE.Vector2(0, top));
  const liq = new THREE.Mesh(new THREE.LatheGeometry(inner, 32), new THREE.MeshLambertMaterial({ color: blood, emissive: '#6a0c1c' })); g.add(liq);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(profile[profile.length - 1][0], .004, 6, 32), new THREE.MeshBasicMaterial({ color: HDR(1.05, 1.1, 1.2) })); rim.rotation.x = Math.PI / 2; rim.position.y = profile[profile.length - 1][1]; g.add(rim);
  const hl = new THREE.Mesh(new THREE.PlaneGeometry(.008, (profile[profile.length - 1][1] - profile[0][1]) * .5), new THREE.MeshBasicMaterial({ color: HDR(1.15, 1.2, 1.3), transparent: true, opacity: .8 }));
  hl.position.set(-profile[2][0] * .55, (top + profile[0][1]) / 2, profile[2][0] * .8); hl.layers.set(1); g.add(hl);      // a glint on the glass
  g.liquid = liq; return g;
}
const FLASK = [[0, 0], [.07, 0], [.075, .01], [.072, .03], [.03, .14], [.022, .17], [.022, .21], [.026, .215]];
const JAR = [[0, 0], [.09, 0], [.095, .02], [.095, .22], [.06, .26], [.04, .28], [.045, .29]];

// the blood line: a glass tube, the blood inside it flows in pulses (dir 1 = from the start of the curve, -1 = back)
const BLOOD_V = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`;
const BLOOD_F = `
uniform float uT; uniform float uFill; uniform float uDir; uniform float uFrom; uniform vec3 uA; uniform vec3 uB; varying vec2 vUv;
void main(){
  float x = uFrom > 0.5 ? 1.0 - vUv.x : vUv.x;
  if (x > uFill) discard;
  float p = 0.5 + 0.5 * sin(vUv.x * 46.0 - uT * 9.0 * uDir);
  float rim = 0.75 + 0.25 * sin(vUv.y * 6.2832);
  gl_FragColor = vec4(mix(uA, uB, p) * rim, 1.0);
}`;
function bloodLine(scene, points, { r = .011 } = {}) {
  const curve = new THREE.CatmullRomCurve3(points);
  const g = new THREE.Group(); scene.add(g);
  const mat = new THREE.ShaderMaterial({ vertexShader: BLOOD_V, fragmentShader: BLOOD_F,
    uniforms: { uT: { value: 0 }, uFill: { value: 0 }, uDir: { value: 1 }, uFrom: { value: 0 }, uA: { value: new THREE.Color('#5e0a18') }, uB: { value: new THREE.Color('#d8263a') } } });
  const blood = new THREE.Mesh(new THREE.TubeGeometry(curve, 96, r * .75, 8, false), mat); blood.layers.set(1); g.add(blood);
  const glass = new THREE.Mesh(new THREE.TubeGeometry(curve, 96, r, 8, false), addBlend(new THREE.MeshBasicMaterial({ color: '#9fb8d8', opacity: .35 })));
  glass.layers.set(1); glass.renderOrder = 5; g.add(glass);
  g.mat = mat; g.curve = curve; return g;
}

// ---------------------------------------------------------------- LAB (x = 0)
function buildLab(scene) {
  const g = new THREE.Group(); scene.add(g);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(8, 7.5), painted(checkerTex({ rep: [8 / 2.4, 7.5 / 2.4] }))); floor.rotation.x = -Math.PI / 2; floor.position.z = .75; g.add(floor);
  const ceil = new THREE.Mesh(new THREE.PlaneGeometry(8, 7.5), flat('#c9c3d6')); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, 3.4, .75); g.add(ceil);
  // walls: stencilled plaster above, a tiled dado below (it stands proud of the wall, with a moulding on top)
  const plasterB = painted(stencilTex({ rep: [1 / 1.6, 1 / 1.6] }));
  const back = holedWall(8, 3.4, [1.95, 1.15, 3.15, 2.55], plasterB); back.position.set(0, 0, -3); back.castShadow = true; g.add(back);
  const side = (x, ry) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(7.5, 3.4), painted(stencilTex({ rep: [7.5 / 1.6, 3.4 / 1.6] }))); m.position.set(x, 1.7, .75); m.rotation.y = ry; g.add(m); return m; };
  side(-4, Math.PI / 2); side(4, -Math.PI / 2);
  const front = new THREE.Mesh(new THREE.PlaneGeometry(8, 3.4), painted(stencilTex({ rep: [5, 2.1] }))); front.position.set(0, 1.7, 4.5); front.rotation.y = Math.PI; g.add(front);
  const tileM = (w) => painted(tilesTex({ rep: [w / 1.0, 1] }));
  const mould = flat('#4e8f94');
  for (const [w, x, z, ry] of [[8, 0, -2.97, 0], [7.5, -3.97, .75, Math.PI / 2], [7.5, 3.97, .75, -Math.PI / 2]]) {
    const d = new THREE.Mesh(new THREE.PlaneGeometry(w, 1.12), tileM(w)); d.position.set(x, .56, z); d.rotation.y = ry; g.add(d);
    const m = box(g, w, .06, .07, x, 1.14, z, mould); m.rotation.y = ry;
    const sk = box(g, w, .1, .05, x, .05, z, flat('#5a4a62')); sk.rotation.y = ry;
  }
  // a painted band under the ceiling
  const band = canvasTex(1024, 64, (c, w, h) => { c.fillStyle = '#e7d8b8'; c.fillRect(0, 0, w, h); c.strokeStyle = '#6a5a78'; c.lineWidth = 2;
    for (let x = 0; x < w; x += 64) { c.fillStyle = '#c75a4a'; c.beginPath(); c.moveTo(x + 32, 12); c.lineTo(x + 48, 32); c.lineTo(x + 32, 52); c.lineTo(x + 16, 32); c.closePath(); c.fill(); c.stroke(); c.fillStyle = '#4a9a9a'; c.beginPath(); c.arc(x, 32, 7, 0, 6.29); c.fill(); c.stroke(); }
    c.fillStyle = '#6a5a78'; c.fillRect(0, 0, w, 4); c.fillRect(0, h - 4, w, 4); });
  band.wrapS = THREE.RepeatWrapping; band.repeat.set(5, 1);
  for (const [w, x, z, ry] of [[8, 0, -2.96, 0], [7.5, -3.96, .75, Math.PI / 2], [7.5, 3.96, .75, -Math.PI / 2]]) { const b = new THREE.Mesh(new THREE.PlaneGeometry(w, .32), painted(band)); b.position.set(x, 3.12, z); b.rotation.y = ry; g.add(b); }
  // the window in the back wall: a deep wooden casing proud of the wall, cross bars, the snowy Moscow night behind
  const WX = [1.95, 3.15], WY = [1.15, 2.55], wc = (WX[0] + WX[1]) / 2, wy = (WY[0] + WY[1]) / 2;
  const jamb = painted(woodTex({ base: '#e8e2d4', plank: 128 }));
  box(g, WX[1] - WX[0] + .16, .1, .3, wc, WY[1] + .05, -2.98, jamb); box(g, WX[1] - WX[0] + .3, .08, .36, wc, WY[0] - .02, -2.9, jamb);
  for (const x of WX) box(g, .1, WY[1] - WY[0], .3, x + Math.sign(x - wc) * .05, wy, -2.98, jamb);
  box(g, .05, WY[1] - WY[0], .05, wc, wy, -3.06, jamb); box(g, WX[1] - WX[0], .05, .05, wc, wy + .25, -3.06, jamb);
  const out = new THREE.Mesh(new THREE.PlaneGeometry(WX[1] - WX[0] + .3, WY[1] - WY[0] + .3),
    vistaMat(moscowTex(), { yaw: Math.atan2(wc - WIN_CAM[0], -3.2 - WIN_CAM[2]), az: 60 * DEG, el: [-6 * DEG, 24 * DEG], gain: 1.25 }));
  out.position.set(wc, wy, -3.2); g.add(out);
  // frost in the window's corners
  const frost = canvasTex(256, 256, (c, w, h) => { const R = rng(4); for (let i = 0; i < 180; i++) { const x = R() < .5 ? R() * 60 : w - R() * 60, y = h - R() * 70; c.fillStyle = 'rgba(235,242,255,.5)'; c.beginPath(); c.arc(x, y, 2 + R() * 7, 0, 6.29); c.fill(); } });
  const fr = new THREE.Mesh(new THREE.PlaneGeometry(WX[1] - WX[0], WY[1] - WY[0]), new THREE.MeshBasicMaterial({ map: frost, transparent: true, depthWrite: false })); fr.position.set(wc, wy, -3.08); fr.layers.set(1); g.add(fr);
  // two iron beds, heads to the back wall; a blanket box hides the sitting figures' legs
  const iron = flat('#e2e0e8'), ironDk = flat('#9a98a8');
  const blanketT = blanketTex();
  for (const bx of [BED_A, BED_B]) {
    box(g, .92, .3, 1.95, bx, .33, -1.98, flat('#d8d4e2'));                                      // base / mattress
    const bl = blanketT.clone(); bl.needsUpdate = true; bl.repeat.set(1, 1);
    const blanket = box(g, .96, .14, 1.42, bx, .55, -1.72, painted(bl));
    box(g, .7, .13, .36, bx, .55, -2.72, flat('#f1eef6'));                                         // pillow
    for (const s of [-1, 1]) {                                                                     // head and foot posts
      cyl(g, .022, .022, 1.2, bx + s * .44, .6, -2.93, iron, 10); cyl(g, .022, .022, .78, bx + s * .44, .39, -1.0, iron, 10);
      const k = new THREE.Mesh(new THREE.SphereGeometry(.035, 12, 8), ironDk); k.position.set(bx + s * .44, 1.21, -2.93); g.add(k);
    }
    for (const y of [.85, 1.12]) { const r = cyl(g, .016, .016, .88, bx, y, -2.93, iron, 8); r.rotation.z = Math.PI / 2; }
    for (let k = -3; k <= 3; k++) cyl(g, .01, .01, .3, bx + k * .11, .98, -2.93, iron, 6);
    const r2 = cyl(g, .016, .016, .88, bx, .74, -1.0, iron, 8); r2.rotation.z = Math.PI / 2;
    for (const s of [-1, 1]) cyl(g, .025, .025, .2, bx + s * .42, .08, -1.02, ironDk, 8);
    void blanket;
  }
  // the transfusion table between the beds with the blood jar
  box(g, .3, .04, .4, 0, .76, -2.3, painted(woodTex({ base: '#8a5a3a' })));
  for (const [x, z] of [[-.13, -2.48], [.13, -2.48], [-.13, -2.12], [.13, -2.12]]) cyl(g, .015, .015, .74, x, .37, z, flat('#5a3a2a'), 6);
  dyn.jar = vessel(JAR, .75); dyn.jar.position.set(0, .78, -2.32); g.add(dyn.jar);
  const tray = box(g, .2, .015, .12, .0, .785, -2.14, flat('#c8ccd6')); tray.userData.noShadow = true;
  // the hanging enamel lamp (the key light): a green shade, white inside, a bare bulb brighter than white
  const LAMP = V(0, 2.32, -1.15);
  const shadeM = new THREE.MeshBasicMaterial({ color: '#1f4a40' });
  const sh = new THREE.Mesh(new THREE.LatheGeometry([[.03, .16], [.06, .14], [.16, .06], [.25, 0], [.26, -.01]].map(([r, y]) => new THREE.Vector2(r, y)), 32), shadeM); sh.position.copy(LAMP); g.add(sh);
  const shIn = new THREE.Mesh(new THREE.LatheGeometry([[.025, .155], [.055, .135], [.155, .055], [.245, -.005]].map(([r, y]) => new THREE.Vector2(r, y)), 32), new THREE.MeshBasicMaterial({ color: HDR(1.15, 1.05, .88), side: THREE.BackSide })); shIn.position.copy(LAMP); shIn.userData.noShadow = true; g.add(shIn);
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(.05, 16, 12), new THREE.MeshBasicMaterial({ color: HDR(3.2, 2.5, 1.4) })); bulb.position.copy(LAMP).add(V(0, .03, 0)); bulb.userData.noShadow = true; g.add(bulb);
  cyl(g, .006, .006, 3.4 - LAMP.y - .16, 0, (3.4 + LAMP.y + .16) / 2, LAMP.z, flat('#2a2630'), 5).userData.noShadow = true;
  dyn.bulb = bulb; dyn.shIn = shIn;
  // the wall clock above the beds
  const CLK = V(-0.86, 2.55, -2.93);
  const caseM = painted(woodTex({ base: '#7a4a2e' }));
  const cc = new THREE.Mesh(new THREE.CylinderGeometry(.27, .27, .07, 48), caseM); cc.rotation.x = Math.PI / 2; cc.position.copy(CLK); g.add(cc);
  const faceT = canvasTex(512, 512, (c, w) => {
    c.fillStyle = '#f4ecd8'; c.beginPath(); c.arc(256, 256, 250, 0, 6.29); c.fill();
    c.strokeStyle = '#3a2a3a'; c.lineWidth = 10; c.beginPath(); c.arc(256, 256, 236, 0, 6.29); c.stroke();
    c.fillStyle = '#2a1a2c'; c.font = `800 62px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle';
    for (let k = 1; k <= 12; k++) { const a = k / 12 * 6.283 - Math.PI / 2; c.fillText(String(k), 256 + Math.cos(a) * 180, 256 + Math.sin(a) * 180); }
    for (let k = 0; k < 60; k++) { const a = k / 60 * 6.283; c.lineWidth = k % 5 ? 3 : 7; c.beginPath(); c.moveTo(256 + Math.cos(a) * 226, 256 + Math.sin(a) * 226); c.lineTo(256 + Math.cos(a) * (k % 5 ? 214 : 204), 256 + Math.sin(a) * (k % 5 ? 214 : 204)); c.stroke(); }
    c.fillStyle = '#c8372f'; c.font = `700 26px ${FONT}`; c.fillText('МОСКВА', 256, 330);
  });
  const cf = new THREE.Mesh(new THREE.CircleGeometry(.235, 48), painted(faceT)); cf.position.copy(CLK).add(V(0, 0, .037)); g.add(cf);
  const handM = flat('#2a1a2c');
  const mkHand = (len, wdt) => { const p = new THREE.Group(); p.position.copy(CLK).add(V(0, 0, .05)); const b = new THREE.Mesh(new THREE.BoxGeometry(wdt, len, .008), handM); b.position.y = len / 2 - .02; b.userData.noShadow = true; p.add(b); g.add(p); return p; };
  dyn.hHour = mkHand(.13, .022); dyn.hMin = mkHand(.19, .014);
  const pin = new THREE.Mesh(new THREE.SphereGeometry(.016, 10, 8), flat('#c89a3a')); pin.position.copy(CLK).add(V(0, 0, .058)); g.add(pin);
  dyn.clock = CLK;
  // the tear-off calendar (its page is redrawn when the year changes)
  const CAL = V(-1.9, 2.2, -2.955);
  box(g, .5, .66, .025, CAL.x, CAL.y, CAL.z - .005, painted(woodTex({ base: '#8a5a3a' })));
  dyn.calT = canvasTex(400, 520, () => {});
  const calP = new THREE.Mesh(new THREE.PlaneGeometry(.44, .57), new THREE.MeshLambertMaterial({ map: dyn.calT })); calP.position.copy(CAL).add(V(0, -.02, .012)); g.add(calP);
  dyn.cal = CAL; dyn.calKey = '';
  // the chalkboard on the left wall: the transfusions are counted on it
  const BRD = V(-3.95, 1.62, -1.15);
  const bf = box(g, .05, 1.08, 1.62, BRD.x, BRD.y, BRD.z, painted(woodTex({ base: '#7a4a2e', vertical: true })));
  dyn.brdT = canvasTex(1200, 800, () => {});
  const bp = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1.0), new THREE.MeshLambertMaterial({ map: dyn.brdT })); bp.position.copy(BRD).add(V(.03, 0, 0)); bp.rotation.y = Math.PI / 2; g.add(bp);
  box(g, .1, .03, 1.5, BRD.x + .06, BRD.y - .53, BRD.z, flat('#6a4026'));
  dyn.brd = BRD; dyn.brdKey = ''; void bf;
  // a circulation chart on the back wall (cool and warm: red arteries, blue veins)
  const chart = canvasTex(600, 840, (c, w, h) => {
    c.fillStyle = '#f2e9d2'; c.fillRect(0, 0, w, h); c.strokeStyle = '#3a2a3a'; c.lineWidth = 8; c.strokeRect(14, 14, w - 28, h - 28);
    c.fillStyle = '#2a1a2c'; c.font = `900 70px ${FONT}`; c.textAlign = 'center'; c.fillText('КРОВЬ', w / 2, 100);
    c.fillStyle = '#e8dcc0'; c.strokeStyle = '#6a5a6a'; c.lineWidth = 5;
    c.beginPath(); c.ellipse(w / 2, 200, 55, 62, 0, 0, 6.29); c.fill(); c.stroke();
    c.beginPath(); c.moveTo(w / 2 - 90, 280); c.lineTo(w / 2 + 90, 280); c.lineTo(w / 2 + 110, 560); c.lineTo(w / 2 + 50, 770); c.lineTo(w / 2 - 50, 770); c.lineTo(w / 2 - 110, 560); c.closePath(); c.fill(); c.stroke();
    const vessel2 = (col, dx) => { c.strokeStyle = col; c.lineWidth = 9; c.lineCap = 'round'; c.beginPath(); c.moveTo(w / 2 + dx, 220); c.bezierCurveTo(w / 2 + dx * 3, 340, w / 2 - dx * 2, 420, w / 2 + dx * 2, 560); c.lineTo(w / 2 + dx * 3, 760); c.stroke();
      for (const y of [330, 450, 600]) { c.lineWidth = 5; c.beginPath(); c.moveTo(w / 2 + dx, y); c.lineTo(w / 2 + dx * 9, y + 50); c.stroke(); } };
    vessel2('#c8323a', 10); vessel2('#3a62c4', -10);
    c.fillStyle = '#c8323a'; c.beginPath(); c.moveTo(w / 2 - 6, 330); c.bezierCurveTo(w / 2 - 70, 290, w / 2 - 60, 380, w / 2 - 6, 410); c.bezierCurveTo(w / 2 + 50, 380, w / 2 + 60, 290, w / 2 - 6, 330); c.fill(); c.strokeStyle = '#5a1a2a'; c.lineWidth = 4; c.stroke();
  });
  const ch = new THREE.Mesh(new THREE.PlaneGeometry(.6, .84), painted(chart)); ch.position.set(-2.95, 1.75, -2.955); g.add(ch);
  box(g, .64, .88, .02, -2.95, 1.75, -2.97, flat('#5a3a2a'));
  // the bedside table with a small lamp (a second warm pool, the key of the last shot) and the notebook
  box(g, .5, .04, .42, 1.62, .7, -2.55, painted(woodTex({ base: '#8a5a3a' })));
  box(g, .46, .62, .38, 1.62, .37, -2.55, painted(woodTex({ base: '#7a4a2e', vertical: true })));
  const DL = V(1.72, .72, -2.64);
  cyl(g, .07, .09, .03, DL.x, DL.y + .015, DL.z, flat('#c89a3a')); cyl(g, .012, .012, .3, DL.x, DL.y + .17, DL.z, flat('#c89a3a'), 8);
  const dshade = new THREE.Mesh(new THREE.CylinderGeometry(.07, .15, .14, 24, 1, true), new THREE.MeshLambertMaterial({ color: '#e0a64a', side: THREE.DoubleSide, emissive: '#3a2008' })); dshade.position.set(DL.x, DL.y + .33, DL.z); g.add(dshade);
  const dbulb = new THREE.Mesh(new THREE.SphereGeometry(.035, 12, 10), new THREE.MeshBasicMaterial({ color: HDR(3, 2.2, 1.1) })); dbulb.position.set(DL.x, DL.y + .29, DL.z); dbulb.userData.noShadow = true; g.add(dbulb);
  dyn.dbulb = dbulb; dyn.dshade = dshade; dyn.deskLamp = V(DL.x, DL.y + .29, DL.z);
  // the flask of the hook (it waits on the bedside table at the end: the last shot shows it)
  dyn.flask = vessel(FLASK, .62); g.add(dyn.flask);
  // the glasses he drops: a little 3D pair that falls onto the floor in the mirror shot
  const gl = new THREE.Group(); const glM = new THREE.MeshBasicMaterial({ color: PLUM });
  for (const s of [-1, 1]) { const r = new THREE.Mesh(new THREE.TorusGeometry(.024, .0035, 6, 20), glM); r.position.x = s * .03; gl.add(r); }
  const br = new THREE.Mesh(new THREE.BoxGeometry(.016, .003, .003), glM); gl.add(br);
  gl.traverse(o => o.layers.set(1)); scene.add(gl); dyn.glasses = gl;
  // a mirror frame close to the lens in the mirror shot (blurred by the lens)
  const mf = box(g, .07, 1.2, .05, -1.585, 1.5, 2.06, painted(woodTex({ base: '#a0703a', vertical: true }))); mf.userData.noShadow = true; dyn.mirrorFrame = mf;
  // the notebook he writes his symptoms in (unlit: it stays cream), lying on the blanket in front of him
  dyn.nbT = canvasTex(1024, 720, () => {}); dyn.nbKey = -1;
  const nb = new THREE.Mesh(new THREE.PlaneGeometry(.34, .24), new THREE.MeshBasicMaterial({ map: dyn.nbT })); nb.rotation.x = -Math.PI / 2; nb.rotation.z = .08; nb.position.set(BED_B - .02, .625, -1.86); g.add(nb);
  const nbC = box(g, .36, .012, .26, BED_B - .02, .617, -1.86, flat('#7a2a3a')); nbC.rotation.y = .08; nbC.userData.noShadow = true; dyn.nbC = nbC;
  dyn.nb = nb;
  // pen
  const pen = new THREE.Group();
  const shaftM = new THREE.Mesh(new THREE.CylinderGeometry(.006, .0045, .15, 10), flat('#2a2a3a')); shaftM.position.y = .09; pen.add(shaftM);
  const nibM = new THREE.Mesh(new THREE.CylinderGeometry(.0045, .001, .022, 10), flat('#d8b04a')); nibM.position.y = .011; pen.add(nibM);
  dyn.penAxis = V(.35, .82, .45).normalize(); pen.quaternion.setFromUnitVectors(V(0, 1, 0), dyn.penAxis); g.add(pen); dyn.pen = pen;

  // light
  const L = new THREE.Group();
  dyn.hemiLab = new THREE.HemisphereLight('#8f9ee6', '#5a4a7a', 1.5); L.add(dyn.hemiLab);
  const key = new THREE.PointLight('#ffc98a', 5.2, 0, 1.25); key.position.copy(LAMP).add(V(0, -.02, 0)); key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024); key.shadow.camera.near = .1; key.shadow.camera.far = 12; key.shadow.bias = -.002; key.shadow.normalBias = .03; key.shadow.radius = 4; L.add(key); dyn.key = key;
  const dl = new THREE.PointLight('#ffb466', 1.1, 3.2, 1.5); dl.position.copy(dyn.deskLamp); L.add(dl); dyn.dl = dl;
  dl.shadow.mapSize.set(1024, 1024); dl.shadow.camera.near = .05; dl.shadow.camera.far = 8; dl.shadow.bias = -.002; dl.shadow.normalBias = .03; dl.shadow.radius = 4;
  // the snow-light through the window: a cool spot from outside (the wall casts, so it only enters through the opening)
  const moon = new THREE.SpotLight('#9fb4ff', 2.6, 0, .32, .4, 0); moon.position.set(4.6, 5.6, -8.4); moon.target.position.set(1.2, 0, -.4); moon.castShadow = true;
  moon.shadow.mapSize.set(1024, 1024); moon.shadow.camera.near = 3; moon.shadow.camera.far = 20; moon.shadow.bias = -.0008; moon.shadow.normalBias = .03; moon.shadow.radius = 3;
  L.add(moon); L.add(moon.target); dyn.moon = moon;
  scene.add(L); sets.lab = { g, L };
  shadows(g);
  dyn.wBeam = beam(scene, [wc, wy, -3.0], [1.4, .05, -.6], { r0: .55, r1: .9, color: '#a9bcff', strength: .14 });
  dyn.lampGlow = glow(scene, LAMP.clone().add(V(0, -.04, 0)).toArray(), '#ffc070', .55, .16);
}

// ---------------------------------------------------------------- STREET (x = 200)
function buildStreet(scene) {
  const g = new THREE.Group(); g.position.x = 200; scene.add(g);
  const snowT = canvasTex(512, 512, (c, w, h) => { c.fillStyle = '#e6eaf6'; c.fillRect(0, 0, w, h); dabs(c, w, h, '#e6eaf6', 400, 30, .1, 12);
    c.strokeStyle = '#b8c0dc'; c.lineWidth = 3; const R = rng(8); for (let i = 0; i < 30; i++) { const x = R() * w, y = R() * h; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + 30, y + (R() - .5) * 20, x + 60 + R() * 60, y + (R() - .5) * 10); c.stroke(); } });
  snowT.wrapS = snowT.wrapT = THREE.RepeatWrapping; snowT.repeat.set(10, 10);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), painted(snowT)); ground.rotation.x = -Math.PI / 2; g.add(ground);
  // the façade: one stone block with a cornice, pilasters, steps, a door, lit windows
  const stone = painted(stoneTex({ base: '#d8b8a0', bw: 192, bh: 64, rep: [12 / 3, 10 / 2] }));
  box(g, 12, 10, 1, 0, 5, -6.5, stone);
  box(g, 12.4, .35, 1.3, 0, 6.6, -6.4, flat('#efe2cc')); box(g, 12.4, .3, 1.2, 0, 9.9, -6.4, flat('#efe2cc')); box(g, 12.2, .12, 1.12, 0, 6.6 + .22, -6.4, flat('#f8f6ff'));   // cornices (with snow)
  for (const x of [-1.5, 1.5]) { cyl(g, .22, .26, 4.4, x, 2.2, -5.75, flat('#efe2cc'), 20); box(g, .62, .2, .62, x, 4.5, -5.75, flat('#efe2cc')); box(g, .62, .2, .62, x, .1, -5.75, flat('#efe2cc')); }
  box(g, 3.8, .3, .6, 0, 4.75, -5.75, flat('#efe2cc'));
  for (let k = 0; k < 3; k++) box(g, 3.4 - k * .3, .14, .5, 0, .07 + k * .14, -5.3 - k * .2, flat('#cfd4e4'));
  const door = painted(woodTex({ base: '#6a3a2a', vertical: true, rep: [1, 2] }));
  box(g, 1.5, 2.6, .12, 0, 1.72, -5.98, door);
  for (const s of [-1, 1]) for (const y of [1.1, 2.3]) box(g, .5, .8, .05, s * .38, y, -5.9, door);
  const glowWin = new THREE.MeshBasicMaterial({ color: HDR(1.25, .92, .5) }), frameM = flat('#efe2cc');
  for (const x of [-4.6, -3.0, 3.0, 4.6]) for (const y of [2.0, 5.0, 8.1]) {
    if (y === 2.0 && Math.abs(x) < 3.5) continue;
    const lit = (x * 7 + y * 3) % 2 > .6;
    const wm = new THREE.Mesh(new THREE.PlaneGeometry(.9, 1.4), lit ? glowWin : flat('#4a5490')); wm.position.set(x, y, -5.99); g.add(wm);
    box(g, 1.08, .12, .2, x, y - .76, -5.92, frameM); box(g, 1.08, .1, .14, x, y + .76, -5.94, frameM); box(g, 1.0, .06, .22, x, y - .68, -5.9, flat('#f8f6ff'));
    box(g, .05, 1.4, .06, x, y, -5.96, flat('#3a3050')); box(g, .9, .05, .06, x, y + .25, -5.96, flat('#3a3050'));
  }
  // the sign: "Institute of Blood Transfusion", with bulbs that light up on "kurdu"
  const signT = canvasTex(1600, 320, (c, w, h) => {
    c.fillStyle = '#9a2a32'; c.fillRect(0, 0, w, h); c.strokeStyle = '#f2c25a'; c.lineWidth = 14; c.strokeRect(20, 20, w - 40, h - 40);
    c.fillStyle = '#fff3d8'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.font = `900 92px ${FONT}`; c.fillText('ИНСТИТУТ', w / 2, 110);
    c.font = `800 74px ${FONT}`; c.fillText('ПЕРЕЛИВАНИЯ КРОВИ', w / 2, 210); c.font = `700 34px ${FONT}`; c.fillStyle = '#f2c25a'; c.fillText('1926', w / 2, 278);
  });
  const sign = new THREE.Mesh(new THREE.BoxGeometry(5.0, 1.0, .08), [flat('#6a1a22'), flat('#6a1a22'), flat('#6a1a22'), flat('#6a1a22'), painted(signT), flat('#6a1a22')]); sign.position.set(0, 3.6, -5.48); g.add(sign);
  dyn.bulbs = []; const bulbOff = flat('#8a7a5a');
  const bulbG = new THREE.SphereGeometry(.045, 10, 8);
  for (let k = 0; k < 26; k++) { const u = k / 26; let x, y; if (u < .5) { x = -2.6 + u * 2 * 5.2; y = 4.18; } else { x = 2.6 - (u - .5) * 2 * 5.2; y = 3.02; }
    const b = new THREE.Mesh(bulbG, bulbOff); b.position.set(x, y, -5.44); b.userData.noShadow = true; g.add(b); dyn.bulbs.push(b); }
  dyn.bulbOff = bulbOff; dyn.bulbOn = new THREE.MeshBasicMaterial({ color: HDR(3.0, 2.2, 1.0) });
  // the street lamp: the key light (warm), it throws the figures' shadows on the snow
  const LP = V(2.15, 0, -3.6);
  const lampM = flat('#2e2a3e');
  cyl(g, .07, .1, 3.5, LP.x, 1.75, LP.z, lampM, 12); cyl(g, .16, .2, .3, LP.x, .15, LP.z, lampM, 12);
  const arm = cyl(g, .03, .03, .55, LP.x - .22, 3.45, LP.z, lampM, 8); arm.rotation.z = Math.PI / 2;
  const lantern = new THREE.Mesh(new THREE.CylinderGeometry(.12, .08, .3, 6), new THREE.MeshBasicMaterial({ color: HDR(2.8, 2.0, 1.0) })); lantern.position.set(LP.x - .45, 3.2, LP.z); lantern.userData.noShadow = true; g.add(lantern);
  const cap = new THREE.Mesh(new THREE.ConeGeometry(.2, .18, 6), lampM); cap.position.set(LP.x - .45, 3.44, LP.z); g.add(cap);
  const snowCap = new THREE.Mesh(new THREE.ConeGeometry(.17, .08, 6), flat('#f4f6ff')); snowCap.position.set(LP.x - .45, 3.55, LP.z); g.add(snowCap);
  dyn.streetLamp = V(200 + LP.x - .45, 3.2, LP.z);
  // a bench and two snow drifts in front of the façade, a fence post close to the lens on the left
  const benchM = painted(woodTex({ base: '#5a6a9a' }));
  box(g, 1.6, .06, .4, -3.2, .48, -4.6, benchM); box(g, 1.6, .3, .05, -3.2, .72, -4.8, benchM); for (const s of [-1, 1]) box(g, .06, .48, .36, -3.2 + s * .7, .24, -4.6, lampM);
  box(g, 1.62, .05, .42, -3.2, .53, -4.6, flat('#f4f6ff'));
  for (const [x, z, s] of [[-5, -5.2, 1.2], [4.6, -5.2, 1], [-2.2, -1.2, .6]]) { const d = new THREE.Mesh(new THREE.SphereGeometry(s, 24, 12, 0, 6.29, 0, 1.2), painted(snowT)); d.scale.y = .3; d.position.set(x, -.1, z); g.add(d); }
  // the skyline behind (painted, unlit)
  const sky = new THREE.Mesh(new THREE.PlaneGeometry(90, 45), new THREE.MeshBasicMaterial({ map: canvasTex(2048, 1024, (c, w, h) => paintMoscow(c, w, h, { horizon: .62, moonX: .62 })) }));
  sky.position.set(0, 13, -34); g.add(sky);
  // newspapers (they fly through the street on "yayıldı")
  const paperT = canvasTex(600, 800, (c, w, h) => {
    c.fillStyle = '#efe6cf'; c.fillRect(0, 0, w, h); c.fillStyle = '#2a1a2c'; c.textAlign = 'center';
    c.font = `900 96px ${FONT}`; c.fillText('ВЕСТИ', w / 2, 110); c.fillRect(30, 130, w - 60, 6); c.font = `600 26px ${FONT}`; c.fillText('МОСКВА · 1925', w / 2, 168); c.fillRect(30, 182, w - 60, 3);
    c.fillStyle = '#b8222e'; c.font = `900 78px ${FONT}`; c.fillText('GENÇLİK', w / 2, 270); c.fillText('KANDA!', w / 2, 352);
    c.fillStyle = '#d8ccb0'; c.fillRect(60, 390, 240, 250); c.strokeStyle = '#2a1a2c'; c.lineWidth = 5; c.strokeRect(60, 390, 240, 250);
    c.fillStyle = '#ffffff'; c.beginPath(); c.ellipse(180, 480, 70, 64, 0, 0, 6.29); c.fill(); c.stroke();      // a little egg-head portrait
    c.lineWidth = 6; for (const s of [-1, 1]) { c.beginPath(); c.arc(180 + s * 22, 474, 15, 0, 6.29); c.stroke(); } c.beginPath(); c.moveTo(160, 512); c.quadraticCurveTo(180, 522, 200, 512); c.stroke();
    c.fillStyle = '#2a1a2c'; c.fillRect(110, 560, 140, 80);
    c.fillStyle = '#6a5a6a'; for (let y = 400; y < 760; y += 22) { c.fillRect(330, y, 220, 8); } for (let y = 670; y < 770; y += 22) c.fillRect(60, y, 240, 8);
  });
  const paperM = new THREE.MeshBasicMaterial({ map: paperT, side: THREE.DoubleSide });
  dyn.papers = [];
  for (let k = 0; k < 7; k++) { const p = new THREE.Mesh(new THREE.PlaneGeometry(.45, .6), paperM); p.layers.set(1); p.visible = false; scene.add(p); dyn.papers.push(p); }
  dyn.paperM = paperM;
  // light
  const L = new THREE.Group();
  L.add(new THREE.HemisphereLight('#7f8ee0', '#5a5080', 1.55));
  const pl = new THREE.PointLight('#ffc070', 9, 0, 1.3); pl.position.copy(dyn.streetLamp).sub(V(200, 0, 0)).add(V(200, -.05, 0)); pl.castShadow = true;
  pl.shadow.mapSize.set(1024, 1024); pl.shadow.camera.near = .1; pl.shadow.camera.far = 20; pl.shadow.bias = -.002; pl.shadow.normalBias = .04; pl.shadow.radius = 4; L.add(pl);
  const door2 = new THREE.PointLight('#ffb060', 2.2, 5, 1.6); door2.position.set(200, 2.6, -4.6); L.add(door2); dyn.signLight = door2;
  scene.add(L); sets.street = { g, L };
  shadows(g);
  dyn.sBeam = beam(scene, dyn.streetLamp.toArray(), [dyn.streetLamp.x - .3, .05, dyn.streetLamp.z + .4], { r0: .15, r1: 1.3, color: '#ffd89a', strength: .12 });
  glow(scene, dyn.streetLamp.toArray(), '#ffc070', .9, .25);
}

// ---------------------------------------------------------------- TUBE (x = 300): inside the glass, the blood cells
function cellGeo() {      // a red blood cell: a disc with a dimple on both faces
  const P = []; for (let i = 0; i <= 16; i++) { const a = i / 16 * Math.PI; const r = .5 * Math.sin(a); const y = .5 * Math.cos(a) * (.42 - .26 * Math.exp(-(r * r) / .03) * (r < .2 ? 1 : 0)); P.push(new THREE.Vector2(Math.max(r, .001), y)); }
  const pts = []; for (let i = 0; i <= 24; i++) { const u = i / 24, r = .5 * Math.sin(u * Math.PI); const y = (.18 + .3 * (r / .5) ** 2 * (1 - (r / .5) ** 6)) * Math.cos(u * Math.PI) * .9; pts.push(new THREE.Vector2(Math.max(r, .0005), y)); }
  return new THREE.LatheGeometry(pts, 32);
}
function buildTube(scene) {
  const g = new THREE.Group(); g.position.x = 300; scene.add(g);
  const wallT = canvasTex(1024, 256, (c, w, h) => {
    const gr = c.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#4a1430'); gr.addColorStop(.5, '#7a1c34'); gr.addColorStop(1, '#4a1430'); c.fillStyle = gr; c.fillRect(0, 0, w, h);
    c.strokeStyle = 'rgba(150,190,255,.55)'; c.lineWidth = 6; for (let x = 0; x < w; x += 128) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x + 40, h); c.stroke(); }
    c.strokeStyle = 'rgba(200,220,255,.8)'; c.lineWidth = 3; c.beginPath(); c.moveTo(0, h * .2); c.lineTo(w, h * .2); c.stroke(); c.beginPath(); c.moveTo(0, h * .8); c.lineTo(w, h * .8); c.stroke();
  });
  wallT.wrapS = wallT.wrapT = THREE.RepeatWrapping; wallT.repeat.set(10, 3);
  const tube = new THREE.Mesh(new THREE.CylinderGeometry(1.7, 1.7, 60, 48, 1, true), new THREE.MeshBasicMaterial({ map: wallT, side: THREE.BackSide }));
  tube.rotation.x = Math.PI / 2; tube.position.z = -20; g.add(tube);
  const end = new THREE.Mesh(new THREE.CircleGeometry(1.7, 48), new THREE.MeshBasicMaterial({ color: HDR(2.4, 1.5, .9) })); end.position.z = -49; g.add(end);
  dyn.tubeEnd = end;
  const N = 150, geo = cellGeo();
  const mat = new THREE.MeshLambertMaterial({ color: '#e8384a', emissive: '#6a1020' });
  dyn.cells = new THREE.InstancedMesh(geo, mat, N); dyn.cells.frustumCulled = false; g.add(dyn.cells);
  const R = rng(31); dyn.cellData = [];
  for (let i = 0; i < N; i++) {
    const a = R() * 6.283, r = Math.sqrt(R()) * 1.35, cl = Math.floor(R() * 9);
    dyn.cellData.push({ x: Math.cos(a) * r, y: Math.sin(a) * r, z0: R() * 44, spin: R() * 6, tilt: R() * 3, s: .32 + R() * .1, cl, type: R() < .5 ? 0 : 1 });
    dyn.cells.setColorAt(i, new THREE.Color(dyn.cellData[i].type ? '#e83a4a' : '#9a1c34'));
  }
  dyn.cells.instanceColor.needsUpdate = true;
  // the clumps: where the cells gather when the blood does not match
  dyn.clumps = []; for (let k = 0; k < 9; k++) dyn.clumps.push(V((R() - .5) * 1.8, (R() - .5) * 1.6, -2 - R() * 9));
  // antibodies: little yellow Y's
  const yC = canvasTex(128, 128, (c) => { c.strokeStyle = '#ffd25a'; c.lineWidth = 14; c.lineCap = 'round'; c.beginPath(); c.moveTo(64, 112); c.lineTo(64, 64); c.lineTo(28, 22); c.moveTo(64, 64); c.lineTo(100, 22); c.stroke(); });
  dyn.ys = []; for (let k = 0; k < 40; k++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: yC, transparent: true, depthWrite: false })); s.scale.setScalar(.22); s.layers.set(1); scene.add(s); dyn.ys.push({ s, a: R() * 6.28, r: .4 + R() * 1.1, z: -1 - R() * 12, k: Math.floor(R() * 9) }); }
  const L = new THREE.Group();
  L.add(new THREE.HemisphereLight('#b0c4ff', '#6a2040', 2.4));
  const p = new THREE.PointLight('#ffb070', 30, 0, 1.0); p.position.set(300, 0, -30); L.add(p);
  const p2 = new THREE.DirectionalLight('#aac0ff', 1.0); p2.position.set(301, 3, 6); L.add(p2);
  scene.add(L); sets.tube = { g, L };
}

// ---------------------------------------------------------------- CAST
// heads: drawn hats and hair-dos (drawHat) and extras over the face (drawFace) for this story
const stroke = (g, w = 10) => { g.strokeStyle = PLUM; g.lineWidth = w; g.lineJoin = 'round'; g.lineCap = 'round'; g.stroke(); };
function glassesOn(g, w, h, p, F) {
  if (!(p.glasses ?? 1)) return;
  const r = w * .088;
  g.fillStyle = 'rgba(200,225,255,.22)';
  for (const [x, y] of [F.eyeL, F.eyeR]) { g.beginPath(); g.arc(x, y - w * .01, r, 0, 6.29); g.fill(); stroke(g, 6.5); }
  g.beginPath(); g.moveTo(F.eyeL[0] + r, F.eyeL[1] - w * .03); g.quadraticCurveTo((F.eyeL[0] + F.eyeR[0]) / 2, F.eyeL[1] - w * .06, F.eyeR[0] - r, F.eyeR[1] - w * .03); stroke(g, 6);
  const far = F.turn > 0 ? F.eyeL : F.eyeR, s = F.turn > 0 ? -1 : 1;           // the temple arm on the far side
  g.beginPath(); g.moveTo(far[0] + s * r, far[1] - w * .02); g.lineTo(far[0] + s * (r + w * .12), far[1] - w * .05); stroke(g, 6);
}
function goatee(g, w, h, F) {             // a small pointed beard under the mouth (his photos: moustache + goatee)
  const [mx, my] = F.mouth, col = '#5a4436';
  g.beginPath(); g.moveTo(mx - w * .1, my + h * .07); g.quadraticCurveTo(mx - w * .08, my + h * .26, mx + F.turn * w * .02, my + h * .34);
  g.quadraticCurveTo(mx + w * .08, my + h * .26, mx + w * .1, my + h * .07); g.quadraticCurveTo(mx, my + h * .12, mx - w * .1, my + h * .07); g.closePath();
  g.fillStyle = col; g.fill(); stroke(g, 6);
}
function bogHair(g, w, h, p) {          // receding: dark hair on the sides and the back, a thin top that fills in (p.hairK)
  const k = p.hairK || 0, col = '#5a4436';
  g.fillStyle = col;
  for (const s of [-1, 1]) { g.beginPath(); g.ellipse(s * w * .45, -h * .2, w * .055, h * .15, s * .3, 0, 6.29); g.fill(); stroke(g, 5); }
  // the top: three thin strands, or a full tuft when the hair "came back"
  if (k < .05) { g.strokeStyle = col; g.lineWidth = 5; for (const x of [-.06, 0, .06]) { g.beginPath(); g.moveTo(w * x, -h * .46); g.quadraticCurveTo(w * (x + .08), -h * .56, w * (x + .16), -h * .5); g.stroke(); } }
  else {
    g.save(); g.translate(0, -h * .43); g.scale(.3 + .4 * k, .3 + .4 * k);
    g.beginPath(); g.moveTo(-w * .34, h * .08); g.bezierCurveTo(-w * .4, -h * .2, -w * .1, -h * .28, w * .05, -h * .18); g.bezierCurveTo(w * .15, -h * .32, w * .42, -h * .2, w * .36, h * .08);
    g.quadraticCurveTo(0, -h * .02, -w * .34, h * .08); g.closePath(); g.fillStyle = col; g.fill(); stroke(g, 8);
    g.restore();
  }
  if (p.sparkle) {                                                    // little stars of "new youth"
    g.fillStyle = '#ffe27a'; g.globalAlpha = Math.min(1, p.sparkle);
    for (const [x, y, s] of [[-.62, -.55, 1], [.66, -.42, .8], [.5, -.78, .6], [-.42, -.86, .7]]) {
      const R = 26 * s; g.beginPath(); for (let q = 0; q < 8; q++) { const a = q * Math.PI / 4, r = q % 2 ? R * .35 : R; g.lineTo(w * x + Math.cos(a) * r, h * y + Math.sin(a) * r); } g.closePath(); g.fill(); stroke(g, 4);
    }
    g.globalAlpha = 1;
  }
}
const ushanka = (g, w, h) => {          // a fur hat with ear flaps
  const fur = '#6a4a3a', top = () => { g.beginPath(); g.moveTo(-w * .46, -h * .34); g.bezierCurveTo(-w * .5, -h * .9, w * .5, -h * .9, w * .46, -h * .34); g.closePath(); };
  top(); g.fillStyle = '#4a3a5a'; g.fill(); stroke(g, 11);
  for (const s of [-1, 1]) { g.beginPath(); g.ellipse(s * w * .48, -h * .1, w * .12, h * .26, s * .1, 0, 6.29); g.fillStyle = fur; g.fill(); stroke(g, 10); }
  g.beginPath(); g.roundRect(-w * .55, -h * .5, w * 1.1, h * .2, 30); g.fillStyle = fur; g.fill(); stroke(g, 11);
  g.strokeStyle = '#8a6a52'; g.lineWidth = 4; for (let x = -.45; x < .5; x += .09) { g.beginPath(); g.moveTo(w * x, -h * .47); g.lineTo(w * (x + .03), -h * .35); g.stroke(); }
};
const flatCap = (col) => (g, w, h) => {
  g.beginPath(); g.moveTo(-w * .5, -h * .3); g.bezierCurveTo(-w * .55, -h * .78, w * .4, -h * .86, w * .52, -h * .4); g.lineTo(w * .78, -h * .32); g.quadraticCurveTo(w * .6, -h * .22, w * .3, -h * .3); g.closePath();
  g.fillStyle = col; g.fill(); stroke(g, 11);
  g.strokeStyle = shade(col, .7); g.lineWidth = 4; g.beginPath(); g.moveTo(-w * .3, -h * .66); g.quadraticCurveTo(0, -h * .5, w * .4, -h * .42); g.stroke();
  g.fillStyle = shade(col, 1.2); g.beginPath(); g.arc(-w * .02, -h * .74, 10, 0, 6.29); g.fill(); stroke(g, 4);
};
const studentCap = (g, w, h) => {      // a student's peaked cap: dark crown, a band, a black visor, a badge
  g.beginPath(); g.moveTo(-w * .48, -h * .36); g.quadraticCurveTo(-w * .62, -h * .82, 0, -h * .84); g.quadraticCurveTo(w * .62, -h * .82, w * .48, -h * .36); g.closePath(); g.fillStyle = '#2f3a6a'; g.fill(); stroke(g, 11);
  g.beginPath(); g.roundRect(-w * .48, -h * .46, w * .96, h * .12, 8); g.fillStyle = '#5a8ac8'; g.fill(); stroke(g, 8);
  g.beginPath(); g.moveTo(-w * .4, -h * .34); g.quadraticCurveTo(0, -h * .18, w * .4, -h * .34); g.closePath(); g.fillStyle = '#2a2236'; g.fill(); stroke(g, 8);
  g.fillStyle = '#f2c25a'; g.beginPath(); g.arc(0, -h * .58, 16, 0, 6.29); g.fill(); stroke(g, 4);
};
const bun = (g, w, h) => {             // parted dark hair with a bun on top
  const col = '#4a3428';
  g.beginPath(); g.arc(0, -h * .62, w * .17, 0, 6.29); g.fillStyle = col; g.fill(); stroke(g, 10);
  g.beginPath(); g.moveTo(-w * .5, -h * .02); g.bezierCurveTo(-w * .56, -h * .62, w * .56, -h * .62, w * .5, -h * .02); g.quadraticCurveTo(w * .3, -h * .38, 0, -h * .36); g.quadraticCurveTo(-w * .3, -h * .38, -w * .5, -h * .02); g.closePath(); g.fillStyle = col; g.fill(); stroke(g, 10);
  g.strokeStyle = shade(col, 1.5); g.lineWidth = 4; g.beginPath(); g.moveTo(0, -h * .5); g.lineTo(0, -h * .38); g.stroke();
};
// props in a drawn hand
const PAPER = (g, x, y) => { g.save(); g.translate(x, y); g.rotate(-.12); g.fillStyle = '#efe6cf'; g.beginPath(); g.rect(-70, -150, 140, 170); g.fill(); g.strokeStyle = PLUM; g.lineWidth = 6; g.stroke();
  g.fillStyle = '#b8222e'; g.font = `900 30px ${FONT}`; g.textAlign = 'center'; g.fillText('GENÇLİK', 0, -100); g.fillText('KANDA!', 0, -68); g.fillStyle = '#6a5a6a'; for (let k = 0; k < 4; k++) g.fillRect(-55, -40 + k * 14, 110, 6); g.restore(); };
const BOOK = (g, x, y) => { g.save(); g.translate(x, y); g.rotate(.25); g.fillStyle = '#3a7a5a'; g.beginPath(); g.roundRect(-34, -48, 68, 90, 6); g.fill(); g.strokeStyle = PLUM; g.lineWidth = 6; g.stroke(); g.fillStyle = '#f2e9d2'; g.fillRect(-26, -38, 52, 10); g.restore(); };
const GLASSES_HAND = (g, x, y) => { g.save(); g.translate(x, y - 34); g.strokeStyle = PLUM; g.lineWidth = 6; for (const s of [-1, 1]) { g.beginPath(); g.arc(s * 22, 0, 18, 0, 6.29); g.stroke(); } g.beginPath(); g.moveTo(-4, -4); g.lineTo(4, -4); g.stroke(); g.restore(); };

export const LOOK = {
  bogdanov: { cloth: '#dfe5ee', clothDark: '#a9b1c8', buttons: '#8a93a8', pocket: true, mustache: '#5e4a3c', height: 1.74, drawFace: (g, w, h, p, lit, F) => { goatee(g, w, h, F); bogHair(g, w, h, p); glassesOn(g, w, h, p, F); } },
  bogPalto: { cloth: '#3b4466', buttons: '#c9a45a', mustache: '#5e4a3c', height: 1.74, hat: 'ushanka', drawHat: ushanka, drawFace: (g, w, h, p, lit, F) => { goatee(g, w, h, F); glassesOn(g, w, h, p, F); } },
  bogYatak: { cloth: '#e8ecf4', pattern: 'stripes', collar: true, mustache: '#5e4a3c', height: 1.74, drawFace: (g, w, h, p, lit, F) => { goatee(g, w, h, F); bogHair(g, w, h, { ...p, hairK: 1 }); } },
  gonullu: { cloth: '#d8963e', pattern: 'stripes', hat: 'kasket', drawHat: flatCap('#6a5a7a'), height: 1.66, bodyW: 176 },
  maria: { cloth: '#4a4370', buttons: '#e8dcc0', hat: 'topuz', drawHat: bun, height: 1.6, headW: 266, headH: 252, bodyW: 172 },
  ogrenci: { cloth: '#6a8ab0', hat: 'kep', drawHat: studentCap, height: 1.68, bodyW: 164, headW: 266 },
  gazeteci: { cloth: '#8a5a3a', pocket: true, hat: 'kasket', drawHat: flatCap('#4a5a7a'), height: 1.42, bodyW: 170, headW: 262, headH: 250 },
};

// ---------------------------------------------------------------- CAMERA (seconds come from words)
function cameraPath() {
  const t = W;
  const keys = [
    // hook: Bogdanov holds a flask of blood up to the lamp -> the room -> the clock stops -> the blood line between two beds
    { t: 0, pos: [0.62, 0.98, 0.85], look: [0.22, 1.74, -0.75], fov: 46, creep: .3, drift: .06 },
    { t: t('Alexander') + .15, dur: .75, pos: WIN_CAM, look: [0.1, 1.45, -2.4], fov: 60, creep: .25 },
    { t: t('yaşlanmayı') + .35, dur: .55, pos: [-0.62, 2.45, -1.85], look: [-0.86, 2.55, -2.96], fov: 40, creep: .3, drift: .03 },
    { t: t('inanıyordu:') + .35, dur: .75, pos: [0.0, 1.5, 1.25], look: [0, 1.12, -2.4], fov: 56, creep: .28, drift: .02 },
    // "Bogdanov sıradan bir hekim değildi." -> the institute in the snow
    { t: t('Bogdanov', 2) + .12, dur: .32, move: 'whip', pos: [199.55, 1.22, -0.95], look: [199.15, 1.45, -3.85], fov: 50, creep: .27 },
    { t: t("Moskova'da") + .55, dur: 1.0, pos: [200.05, 1.0, 1.9], look: [200.0, 4.4, -6], fov: 60, creep: .22 },
    { t: t('teorisini') + .5, dur: .9, pos: [199.62, 1.42, -1.7], look: [199.18, 1.52, -3.85], fov: 44, creep: .28 },
    // 1924: the calendar, then the two beds and the blood going both ways
    { t: t("1924'ten") + .05, dur: .32, move: 'whip', pos: [-1.74, 2.02, -1.95], look: [-1.9, 2.2, -2.96], fov: 40, creep: .3, drift: .03 },
    { t: t('genç', 1) + .35, dur: .9, pos: [0.0, 1.5, 1.25], look: [0, 1.12, -2.4], fov: 56, creep: .27, drift: .02 },
    { t: t('İlk', 2) + .35, dur: .6, pos: [-1.25, 1.6, -1.12], look: [-3.96, 1.55, -1.15], fov: 48, creep: .3, drift: .04 },
    { t: t('Gözlüğü') + .1, dur: .35, move: 'whip', pos: [-1.45, 1.52, 2.45], look: [-1.62, 1.44, 0.55], fov: 38, creep: .3, drift: .03 },
    // the newspapers in the street, Lenin's sister in the bed
    { t: t('İddiaları') + .1, dur: .32, move: 'whip', pos: [200.3, 1.18, -0.75], look: [200.75, 1.42, -3.4], fov: 50, creep: .3 },
    { t: t("Lenin'in") + .02, dur: .32, move: 'whip', pos: [-0.1, 1.45, 0.9], look: [-0.15, 1.1, -2.4], fov: 54, creep: .28, drift: .02 },
    // 1928: the one hard cut
    { t: t('1928'), move: 'cut', pos: [-1.74, 2.02, -1.95], look: [-1.9, 2.2, -2.96], fov: 40, creep: .3, drift: .03 },
    { t: t('12.') + .3, dur: .5, pos: [-1.25, 1.6, -1.12], look: [-3.96, 1.55, -1.15], fov: 46, creep: .3, drift: .04 },
    { t: t('masaya') + .25, dur: .6, pos: [0.6, 1.38, -0.2], look: [0.68, 1.05, -2.4], fov: 46, creep: .27, drift: .04 },
    { t: t('kez') + .35, dur: .8, pos: [-0.6, 1.32, -0.45], look: [-0.72, 1.12, -2.4], fov: 44, creep: .28, drift: .04 },
    { t: t('Nakilden', 2) + .4, dur: .55, pos: [-0.62, 2.45, -1.85], look: [-0.86, 2.55, -2.96], fov: 40, creep: .3, drift: .03 },
    { t: t('ikisi') + .3, dur: .7, pos: [0.0, 1.52, 1.25], look: [0, 1.1, -2.4], fov: 56, creep: .27, drift: .02 },
    // "kan uyuşmazlığı": into the tube
    { t: t('ama') + .1, dur: .32, move: 'whip', pos: [300.0, 0.15, 3.5], look: [300.1, 0.0, -8], fov: 58, creep: .3 },
    // the end: the notebook by the bedside lamp, the lamp goes out
    { t: t('Gençlik') + .05, dur: .32, move: 'whip', pos: [1.45, 1.22, -1.1], look: [0.82, 0.9, -2.45], fov: 50, creep: .25, drift: .04 },
    { t: t('son') + .45, dur: .8, pos: [0.95, 1.18, -1.42], look: [0.72, 0.62, -1.9], fov: 38, creep: .25, drift: .02 },
    { t: t('kaybetti.') + .9, dur: 1.6, pos: [0.35, 1.5, 0.9], look: [0.3, 1.2, -2.9], fov: 52, creep: .18 },
  ];
  const cp = new CamPath(keys, { fps: FPS });
  cp.kick(t('durdurmanın') + .25, .8); cp.kick(t('kurdu') + .02, .6); cp.kick(t("1924'ten") + .5, .5); cp.kick(t('düştü.') + .05, 1.0); cp.kick(t('kaldıramadı.') + .1, .9);
  return cp;
}

// ---------------------------------------------------------------- canvases redrawn on change
function drawCalendar(year, month) {
  const key = year + month; if (dyn.calKey === key) return; dyn.calKey = key;
  const g = dyn.calT.g, w = 400, h = 520;
  g.fillStyle = '#f4ecd8'; g.fillRect(0, 0, w, h); g.fillStyle = '#c8323a'; g.fillRect(0, 0, w, 120);
  g.fillStyle = '#fff3d8'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.font = `900 64px ${FONT}`; g.fillText(month || 'TAKVİM', w / 2, 62);
  g.fillStyle = '#2a1a2c'; g.font = `900 150px ${FONT}`; g.fillText(String(year), w / 2, 270);
  g.strokeStyle = '#8a7a8a'; g.lineWidth = 4; for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(60, 380 + k * 32); g.lineTo(340, 380 + k * 32); g.stroke(); }
  g.fillStyle = '#5a4a5a'; for (let k = 0; k < 6; k++) { g.beginPath(); g.arc(50 + k * 60, 14, 7, 0, 6.29); g.fill(); }
  dyn.calT.needsUpdate = true;
}
function drawBoard(n, circle) {
  const key = n + ':' + circle; if (dyn.brdKey === key) return; dyn.brdKey = key;
  const g = dyn.brdT.g, w = 1200, h = 800;
  g.fillStyle = '#3f7466'; g.fillRect(0, 0, w, h); dabs(g, w, h, '#3f7466', 160, 60, .2, 3);
  g.fillStyle = 'rgba(230,240,235,.18)'; for (let k = 0; k < 6; k++) { g.beginPath(); g.ellipse(200 + k * 170, 600 - k * 40, 150, 30, -.2, 0, 6.29); g.fill(); }   // old wiped chalk
  g.fillStyle = '#eef2ea'; g.textAlign = 'left'; g.font = `800 92px ${HAND}`; g.fillText('NAKİL', 70, 140);
  g.strokeStyle = '#eef2ea'; g.lineCap = 'round'; g.lineWidth = 16;
  for (let i = 0; i < Math.min(n, 12); i++) {
    const grp = Math.floor(i / 5), k = i % 5, x0 = 90 + grp * 330, red = i === 11;
    g.strokeStyle = red ? '#ff6a6a' : '#eef2ea';
    if (k < 4) { const x = x0 + k * 58; g.beginPath(); g.moveTo(x, 270 + (k % 2) * 6); g.lineTo(x + 6, 470); g.stroke(); }
    else { g.beginPath(); g.moveTo(x0 - 30, 430); g.lineTo(x0 + 220, 300); g.stroke(); }
  }
  if (circle) { g.strokeStyle = '#ffd25a'; g.lineWidth = 12; g.beginPath(); g.ellipse(w * .78, 640, 120, 90, -.1, 0, 6.29); g.stroke(); g.fillStyle = '#ffd25a'; g.font = `800 120px ${HAND}`; g.textAlign = 'center'; g.fillText(String(n), w * .78, 680); }
  dyn.brdT.needsUpdate = true;
}
const NOTES = ['24 Mart 1928', 'Titreme. Ateş 39,8', 'Nabız hızlı, zayıf', 'Bulantı, sırtta ağrı', 'İdrar koyu...', 'Kalp ses'];
function drawNotebook(p) {
  const key = Math.round(p * 300); if (dyn.nbKey === key) return; dyn.nbKey = key;
  const g = dyn.nbT.g, w = 1024, h = 720;
  g.fillStyle = '#f6efd9'; g.fillRect(0, 0, w, h);
  g.strokeStyle = '#9ab0d8'; g.lineWidth = 3; for (let y = 120; y < h; y += 92) { g.beginPath(); g.moveTo(40, y); g.lineTo(w - 40, y); g.stroke(); }
  g.strokeStyle = '#e08a8a'; g.beginPath(); g.moveTo(120, 0); g.lineTo(120, h); g.stroke();
  g.fillStyle = '#d8cdb0'; g.fillRect(w / 2 - 6, 0, 12, h);                                 // the spine
  g.fillStyle = '#20264a'; g.font = `italic 600 58px ${HAND}`; g.textBaseline = 'alphabetic';
  // the text appears letter by letter; it is written across the right-hand page and the next lines
  const all = NOTES.join('\n'), n = Math.floor(all.length * p); let shown = all.slice(0, n).split('\n');
  shown.forEach((line, i) => g.fillText(line, 150, 104 + i * 92));
  dyn.nbT.needsUpdate = true;
  // where the pen is: the end of the last line (paper coordinates 0..1)
  const li = shown.length - 1; const wd = g.measureText(shown[li] || '').width;
  dyn.nbTip = [(150 + wd) / w, (104 + li * 92 - 14) / h];
}

// ---------------------------------------------------------------- SETUP
export async function setup(ctx) {
  W = wordTimes(ctx.words);
  DUR = Math.ceil((ctx.words[ctx.words.length - 1].end + 1.0) * FPS) / FPS;
  const { scene } = ctx;
  scene.background = new THREE.Color('#1a1f3a');
  buildLab(scene); buildStreet(scene); buildTube(scene);
  cast.bog = new Toon(LOOK.bogdanov, scene); cast.palto = new Toon(LOOK.bogPalto, scene); cast.yatak = new Toon(LOOK.bogYatak, scene);
  cast.gonullu = new Toon(LOOK.gonullu, scene); cast.maria = new Toon(LOOK.maria, scene); cast.ogrenci = new Toon(LOOK.ogrenci, scene); cast.gazeteci = new Toon(LOOK.gazeteci, scene);
  dyn.armFlask = new Arm3D(scene, cast.bog); dyn.armJar = new Arm3D(scene, cast.bog);
  dyn.armA = new Arm3D(scene, cast.gonullu); dyn.armM = new Arm3D(scene, cast.maria); dyn.armO = new Arm3D(scene, cast.ogrenci);
  dyn.armB = new Arm3D(scene, cast.yatak); dyn.armPen = new Arm3D(scene, cast.yatak);
  // the blood line between the beds: patient A's hand -> over the jar -> Bogdanov's hand
  const hA = V(BED_A + .42, .66, -2.05), hB = V(BED_B - .42, .66, -2.05);
  dyn.hA = hA; dyn.hB = hB;
  dyn.line = bloodLine(scene, [hA, V(-.17, .95, -2.2), V(0, 1.12, -2.3), V(.17, .95, -2.2), hB]);
  // snow: slow white specks falling in the street and outside the window
  smokes.snow = new Smoke(scene, { color: '#f2f4ff', maxPoints: 1400, H: ctx.H, additive: true, near: 1.2 });
  const hash = (i, k) => { const x = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453; return x - Math.floor(x); };
  smokes.snow.wisps.push({ n: 900, size: .03, alpha: .8, speed: .07, on: () => dyn.where === 'street',
    path: (u, t, i) => [194 + hash(i, 1) * 12 + Math.sin(t * .8 + i) * .2, 7 - u * 7.4, -6 + hash(i, 2) * 7.5 + Math.cos(t * .6 + i) * .15] });
  // dust in the lamp light; the cough puffs; the mosquito
  smokes.motes = new Smoke(scene, { color: '#fff0d0', maxPoints: 300, H: ctx.H, additive: true, near: 1.8 });
  smokes.motes.wisps.push({ n: 160, size: .008, alpha: .45, speed: .04, on: () => dyn.where === 'lab' && dyn.keyOn > .5,
    path: (u, t, i) => [(hash(i, 1) - .5) * 2.4 + Math.sin(t * .5 + i) * .05, .9 + hash(i, 2) * 1.5 + (u - .5) * .3, -1.6 + (hash(i, 3) - .5) * 2.2 + Math.cos(t * .4 + i * 2) * .05] });
  smokes.cough = new Smoke(scene, { color: '#d8d2e4', maxPoints: 200, H: ctx.H });
  smokes.cough.wisps.push({ n: 60, size: .05, alpha: .5, speed: .9, on: t => dyn.coughOn && t > 0,
    path: (u, t, i) => { const m = dyn.mouthO || V(); return [m.x + u * .25 + Math.sin(i) * .03 * u, m.y + Math.sin(u * 4 + i) * .03 - u * .04, m.z + u * .25]; } });
  const mq = canvasTex(128, 128, (c) => { c.strokeStyle = PLUM; c.lineCap = 'round'; c.lineWidth = 7; c.beginPath(); c.moveTo(40, 70); c.lineTo(88, 62); c.stroke(); c.lineWidth = 3; c.beginPath(); c.moveTo(88, 62); c.lineTo(118, 58); c.stroke();
    for (const [x, y] of [[50, 74], [62, 72], [74, 70]]) { c.beginPath(); c.moveTo(x, y); c.lineTo(x - 8, y + 22); c.stroke(); }
    c.fillStyle = 'rgba(220,235,255,.85)'; c.lineWidth = 3; for (const s of [-1, 1]) { c.beginPath(); c.ellipse(62, 54 + s * 2, 26, 11, -.4 - s * .25, 0, 6.29); c.fill(); c.stroke(); } });
  dyn.mosq = new THREE.Sprite(new THREE.SpriteMaterial({ map: mq, transparent: true, depthWrite: false })); dyn.mosq.scale.setScalar(.13); dyn.mosq.layers.set(1); scene.add(dyn.mosq);
  dyn.cam = cameraPath();
  // sound cues for this story's mix (audio/mix.py of the story)
  const cue = (t, type, extra = {}) => CUES.push({ t: +t.toFixed(3), type, ...extra });
  cue(W('Bogdanov', 2) - .1, 'whoosh'); cue(W("1924'ten") - .15, 'whoosh'); cue(W('İddiaları') - .1, 'whoosh'); cue(W("Lenin'in") - .15, 'whoosh'); cue(W('ama') - .1, 'whoosh'); cue(W('Gençlik') - .15, 'whoosh'); cue(W('Gözlüğü') - .1, 'whoosh');
  cue(W('yaşlanmayı') + .2, 'tick', { dur: W('durdurmanın') + .25 - (W('yaşlanmayı') + .2), fast: 1 }); cue(W('durdurmanın') + .25, 'stop');
  cue(W('kanını', 1), 'pump', { dur: W('Bogdanov', 2) - W('kanını', 1) - .1 });
  cue(0, 'room', { dur: W('Bogdanov', 2) }); cue(W("1924'ten"), 'room', { dur: W('İddiaları') - W("1924'ten") }); cue(W("Lenin'in"), 'room', { dur: W('ama') - W("Lenin'in") });
  cue(W('Bogdanov', 2), 'wind', { dur: W("1924'ten") - W('Bogdanov', 2) }); cue(W('İddiaları'), 'wind', { dur: W("Lenin'in") - W('İddiaları') });
  cue(W('kurdu') + .02, 'bulbs'); cue(W("1924'ten") + .1, 'flip', { dur: .5 }); cue(W('1928') + .05, 'flip', { dur: .7 }); cue(W('1928'), 'thunder');
  cue(W('karşılıklı'), 'pump', { dur: W('İlk', 2) - W('karşılıklı') });
  cue(W('İlk', 2) + .2, 'chalk', { n: 11, dur: .85 }); cue(W('inanılmazdı.') + .05, 'boom');
  cue(W('bıraktı,') + .05, 'clink'); cue(W('durdu,') - .05, 'sparkle'); cue(W('gençleşmiş') - .05, 'sparkle');
  cue(W('yayıldı') - .2, 'papers', { dur: 1.3 }); cue(W('12.') + .45, 'chalk', { n: 1, dur: .3 });
  cue(W('sıtma') - .1, 'buzz', { dur: 1.1 }); cue(W('tüberküloz') + .1, 'cough');
  cue(W('Nakilden', 2) + .4, 'tick', { dur: W('ikisi') - W('Nakilden', 2) - .2, fast: 3 }); cue(W('düştü.') + .05, 'boom');
  cue(W('ama') + .1, 'blood', { dur: W('Gençlik') - W('ama') }); cue(W('kaldıramadı.') + .1, 'stop');
  cue(W('son') + .5, 'pen', { dur: W('54') - W('son') - .5 }); cue(W('kaybetti.') + .1, 'click'); cue(W('kaybetti.') + .5, 'heart_end');
}

// ---------------------------------------------------------------- PER FRAME
const vis = (set, on) => { sets[set].g.visible = on; sets[set].L.visible = on; };
const WARM = '#ffb45a', NIGHT = '#d6d1f2';
const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), E = new THREE.Euler();
export function frame(t, ctx) {
  const { cam, env } = ctx;
  const cp = dyn.cam.apply(cam, t);
  const x = cam.position.x;
  const where = dyn.where = x < 100 ? 'lab' : x < 250 ? 'street' : 'tube';
  for (const s of ['lab', 'street', 'tube']) vis(s, s === where);
  const T = W, A = (w, n) => W(w, n) - 2 / FPS;
  const bl = (seed, ...swaps) => blinkAt(t, seed, swaps, FPS);
  const tint = FACE[where].map((v, i) => v / GRADE[where][i]);
  for (const c of Object.values(cast)) c.hide();
  for (const a of [dyn.armFlask, dyn.armJar, dyn.armA, dyn.armM, dyn.armO, dyn.armB, dyn.armPen]) a.hide();
  dyn.flask.visible = false; dyn.glasses.visible = false; dyn.mosq.visible = false; dyn.pen.visible = false; dyn.coughOn = false;
  dyn.papers.forEach(p => { p.visible = false; });
  dyn.ys.forEach(y => { y.s.visible = false; });
  dyn.line.visible = false; dyn.mirrorFrame.visible = false; dyn.nb.visible = dyn.nbC.visible = t > W('Gençlik') - .1;
  dyn.wBeam.visible = where === 'lab'; dyn.sBeam.visible = where === 'street'; dyn.lampGlow.visible = where === 'lab';

  // ---- the lab's lights over the story: the key flickers in the reaction, and is off at the end; the bedside lamp goes out last
  const end = t > T('Gençlik') - .1;
  const flick = t > T('ikisi') && t < T('ama') ? .75 + .25 * Math.sin(t * 37) * Math.sin(t * 11) : 1;
  dyn.keyOn = end ? 0 : flick;
  const deskOn = end ? 1 - lin(t, T('kaybetti.') + .1, T('kaybetti.') + .2) : 1;
  dyn.key.intensity = 5.2 * dyn.keyOn; dyn.key.visible = dyn.keyOn > .01;
  dyn.bulb.material.color.copy(dyn.keyOn > .01 ? HDR(3.2 * dyn.keyOn, 2.5 * dyn.keyOn, 1.4 * dyn.keyOn) : HDR(.35, .3, .3));
  dyn.shIn.material.color.copy(dyn.keyOn > .01 ? HDR(1.15, 1.05, .88) : HDR(.38, .4, .5));
  dyn.lampGlow.visible = where === 'lab' && dyn.keyOn > .01; dyn.lampGlow.material.opacity = .16 * dyn.keyOn;
  dyn.dl.intensity = (end ? 2.6 : 1.1) * deskOn; dyn.dl.castShadow = end; dyn.dl.distance = end ? 0 : 3.2; dyn.dl.decay = end ? 1.4 : 1.5;
  dyn.dbulb.material.color.copy(deskOn > .01 ? HDR(3 * deskOn + .2, 2.2 * deskOn + .2, 1.1 * deskOn + .25) : HDR(.3, .28, .3));
  dyn.dshade.material.emissive.set(deskOn > .01 ? '#3a2008' : '#000000');
  dyn.hemiLab.intensity = end ? 1.15 : 1.5;
  dyn.moon.intensity = end ? 3.4 : 2.6;

  // ---- clock: spins back on "yaşlanmayı", STOPS on "durdurmanın"; races forward on "birkaç saat sonra"; stopped at the end
  {
    let m = 10.1 * 60;                                                       // minutes past midnight (the time it shows)
    const b0 = T('yaşlanmayı') + .2, b1 = T('durdurmanın') + .25;
    if (t < b0) m += t * 2; else if (t < b1) m += b0 * 2 - (t - b0) * 600; else m += b0 * 2 - (b1 - b0) * 600;
    const f0 = T('Nakilden', 2) + .4, f1 = T('ikisi') + .1;
    if (t > f0) m += Math.min(t, f1) * 0 + (Math.min(t, f1) - f0) * 260;
    if (t > f1) m += (t - f1) * 3;
    if (t > T('kaybetti.') + .1) m -= (t - (T('kaybetti.') + .1)) * 3;      // stopped
    dyn.hMin.rotation.z = -m / 60 * Math.PI * 2; dyn.hHour.rotation.z = -m / 720 * Math.PI * 2;
  }
  // ---- calendar: 1920 -> 1924 on "1924'ten", 1924 -> 1928 + MART on the cut
  {
    let year = 1920, month = 'EKİM';
    if (t > T("1924'ten") + .05) { year = 1920 + Math.min(4, Math.floor(lin(t, T("1924'ten") + .05, T("1924'ten") + .5) * 4.99)); month = year === 1924 ? 'OCAK' : '·'; }
    if (t > T('1928') - .05) { year = 1924 + Math.min(4, Math.floor(lin(t, T('1928'), T('1928') + .6) * 4.99)); month = year === 1928 ? 'MART' : '·'; }
    if (where === 'lab') drawCalendar(year, month);
  }
  // ---- chalkboard: 11 marks between "İlk" and "nakilden"; the 12th, in red, on "12."
  {
    const n = t < T('İlk', 2) + .2 ? 0 : t < T('12.') + .45 ? Math.min(11, Math.floor(lin(t, T('İlk', 2) + .2, T('sonra', 1) - .05) * 11.99)) : 12;
    if (where === 'lab') drawBoard(n, t > T('inanılmazdı.') && t < T('12.'));
  }
  // ---- the blood line: on in every bed shot; it fills from A to B, pulses both ways in 1924, clots in 1928
  const hookBeds = t > T('bulduğuna') && t < T('Bogdanov', 2);
  const beds1924 = t > T('genç', 1) && t < T('İlk', 2) + .6;
  const bedsMaria = t > T("Lenin'in") && t < T('1928');
  const beds1928 = t > T('masaya') && t < T('ama') + .1;
  const bedsEnd = end;
  if (where === 'lab' && (hookBeds || beds1924 || bedsMaria || beds1928)) {
    dyn.line.visible = true;
    const u = dyn.line.mat.uniforms; u.uT.value = t;
    if (hookBeds) { u.uFill.value = lin(t, T('kanını') - .05, T('nakletmek.') + .1); u.uDir.value = 1; u.uFrom.value = 0; }
    else if (beds1924) { u.uFill.value = 1; u.uDir.value = Math.sin((t - T('karşılıklı')) * 2.6) > 0 ? 1 : -1; u.uFrom.value = 0; }
    else if (bedsMaria) { u.uFill.value = 1; u.uDir.value = -1; u.uFrom.value = 0; }
    else { u.uFill.value = 1; u.uDir.value = t > T('ikisi') ? .15 : 1; u.uFrom.value = 0; }
  }
  // ---- street: the sign lights up on "kurdu"
  if (where === 'street') {
    const on = t > T('kurdu') + .02 && t < T('İddiaları') - .5 || t > T('İddiaları');
    dyn.bulbs.forEach((b, i) => { const lit = on && (t - (T('kurdu') + .02) > i * .012 || t > T('İddiaları')) && (Math.sin(t * 6 + i * .9) > -.6); b.material = lit ? dyn.bulbOn : dyn.bulbOff; });
    dyn.signLight.intensity = on ? 2.6 : .8;
  }

  // ================= CAST
  if (where === 'lab') {
    // standing Bogdanov (lab coat): the hook (flask held up to the lamp) and the mirror; on "Lenin'in" he holds the jar
    const hook = t < T('yaşlanmayı') + .9, mirror = t > T('Gözlüğü') && t < T('İddiaları'), maria = false;
    if (hook) {
      const b = cast.bog; b.show(); b.place(0.22, 0, -0.72, cam, tint);
      const up = ramp(t, -.1, .5), F = b.toWorld(140, lerpN(300, 225, up), .25);
      F.z += .08; const swirl = Math.sin(t * 2.2) * .015;
      b.draw({ expr: t < A('Alexander') ? 'focused' : 'smug', look: .55, lookY: -.75, gazeX: .5, gazeY: -1, brow: t > A('Alexander') ? .5 : 0, blink: bl(1, A('Alexander')), noArmR: true, armL: [18, 20], tilt: -5,
        lit: 1, shade: NIGHT, rim: { color: WARM, a: .42 }, glasses: 1, hairK: 0 });
      dyn.flask.visible = true; dyn.flask.position.copy(F).add(V(0, -.05, 0)); dyn.flask.rotation.set(0, t * .3, swirl);
      dyn.armFlask.set(1, F.clone().add(V(0, .02, 0)), { sag: .06, tint });
      b.castFrom(dyn.key.position);
    } else if (mirror) {
      const b = cast.bog; b.show(); b.place(-1.62, 0, 0.55, cam, tint);
      const off = t > A('bıraktı,'), hair = lin(t, T('dökülmesi') - .05, T('durdu,') + .2), flex = t > A('20') - .1;
      const sp = flex ? ramp(t, T('20') - .1, T('20') + .15) * (1 - ramp(t, T('hissediyordu.') + .4, T('İddiaları'))) : ramp(t, T('durdu,') - .1, T('durdu,') + .1) * (1 - ramp(t, T('durdu,') + .5, T('kendini') + .2));
      const hold = t > A('Gözlüğü') && t < A('bıraktı,') + .25;
      b.draw({ expr: flex ? 'grin' : hair > .5 ? 'surprised' : off ? 'smile' : 'focused', look: flex ? .25 : 0, lookY: hair > .1 && hair < .95 && !flex ? -.6 : 0, gazeY: hair > .1 && !flex ? -1 : 0,
        blink: bl(2, A('bıraktı,'), A('durdu,') - .1, A('20') - .1), glasses: off ? 0 : 1, hairK: hair, sparkle: sp,
        armR: hold ? [150, 30] : flex ? [90, 90] : [14, 10], propR: hold ? GLASSES_HAND : undefined, armL: flex ? [90, 90] : [14, 10], lean: flex ? -3 : 0,
        lit: 1, shade: NIGHT, rim: { color: WARM, a: .35 } });
      b.castFrom(dyn.key.position);
      // the glasses fall to the floor after "bıraktı"
      const ft = t - (T('bıraktı,') + .25);
      if (ft > 0) { const h0 = b.toWorld(126, 110, .12); dyn.glasses.visible = true; const k = Math.min(1, ft / .42); dyn.glasses.position.set(h0.x + .05 * k, Math.max(.02, h0.y - 4.9 * Math.min(ft, .55) ** 2), h0.z + .1 * k); dyn.glasses.rotation.set(-Math.PI / 2 * k, ft * 3 * (1 - k), 0); }
      dyn.mirrorFrame.visible = true;
    } else if (maria) {
      const b = cast.bog; b.show(); b.place(0.2, 0, -1.65, cam, tint);
      b.draw({ expr: 'proud', look: -.6, lookY: .3, blink: bl(3), noArmR: true, armL: [14, 10], lit: 1, shade: NIGHT, rim: { color: WARM, a: .4 }, glasses: 1, hairK: 1 });
      dyn.armJar.set(-1, V(.02, 1.0, -2.24), { sag: .05, tint });
      b.castFrom(dyn.key.position);
    }
    // the beds: patient A (volunteer / Maria / the student), patient B (Bogdanov in bed)
    const inBed = (toon, bx, { sink = 0, pitch = 0, scale = 1 } = {}) => { toon.show(); toon.place(bx, -.07 - sink, BED_Z, cam, tint, scale, pitch); toon.castFrom(dyn.key.visible ? dyn.key.position : dyn.deskLamp); };
    if (hookBeds || beds1924) {
      const g = cast.gonullu; inBed(g, BED_A);
      g.draw({ expr: t < A('nakletmek.') && hookBeds ? 'neutral' : 'smile', look: .45, lookY: .3, blink: bl(4, A('nakletmek.')), noArmR: true, armL: [12, 8], lit: 1, shade: NIGHT, rim: { color: WARM, a: .4 } });
      dyn.armA.set(1, dyn.hA, { sag: .06, tint });
      const y = cast.yatak; inBed(y, BED_B);
      const happy = hookBeds ? t > A('kanını') : t > A('karşılıklı');
      y.draw({ expr: happy ? (hookBeds ? 'grin' : 'proud') : 'neutral', look: -.45, lookY: .3, blink: bl(5, hookBeds ? A('kanını') : A('karşılıklı')), noArmL: true, armR: [12, 8], lit: -1, shade: NIGHT, rim: { color: WARM, a: .4 } });
      dyn.armB.set(-1, dyn.hB, { sag: .06, tint });
    } else if (bedsMaria) {
      const m = cast.maria; inBed(m, BED_A);
      m.draw({ expr: t > A('denedi.') ? 'smile' : 'focused', look: .5, lookY: .2, blink: bl(6, A('denedi.')), noArmR: true, armL: [12, 8], lit: 1, shade: NIGHT, rim: { color: WARM, a: .4 } });
      dyn.armM.set(1, dyn.hA, { sag: .06, tint });
      const y = cast.yatak; inBed(y, BED_B);
      y.draw({ expr: 'proud', look: -.5, lookY: .3, blink: bl(5), noArmL: true, armR: [12, 8], lit: -1, shade: NIGHT, rim: { color: WARM, a: .4 } });
      dyn.armB.set(-1, dyn.hB, { sag: .06, tint });
    } else if (beds1928 || bedsEnd) {
      const sick = ramp(t, T('ikisi') - .1, T('düştü.') + .1), recover = ramp(t, T('Öğrenci'), T('hayatta') + .2);
      if (!bedsEnd) {
        const o = cast.ogrenci; inBed(o, BED_A, { sink: .16 * sick * (1 - recover), pitch: -.1 * sick * (1 - recover) });
        const cough = t > T('tüberküloz') + .05 && t < T('geçirmiş') + .4, mosq = t > T('sıtma') - .15 && t < T('tüberküloz') + .2;
        const exprO = recover > .5 ? 'smile' : sick > .5 ? 'worried' : cough ? 'angry' : mosq ? 'surprised' : t > A('üniversite') ? 'smile' : 'neutral';
        o.draw({ expr: exprO, look: mosq ? -.6 : .4, lookY: mosq ? -.8 : .2, gazeY: mosq ? -1 : 0, blink: bl(7, A('sıtma') - .15, A('tüberküloz') + .05, A('üniversite'), A('ikisi'), A('Öğrenci')),
          mouth: cough ? .5 + .5 * Math.abs(Math.sin(t * 16)) : 0, sweat: sick * (1 - recover), noArmR: true, armL: t > A('üniversite') && t < A('Nakilden', 2) ? [150, 20] : [12, 8], propL: t > A('üniversite') && t < A('Nakilden', 2) ? BOOK : undefined,
          lit: 1, shade: '#c8cbe8', rim: { color: WARM, a: .35 } });
        dyn.armO.set(1, dyn.hA, { sag: .06, tint });
        if (cough) { dyn.coughOn = true; dyn.mouthO = o.toWorld(60, 260, .1); }
        if (mosq) { dyn.mosq.visible = true; const a = t * 7; dyn.mosq.position.set(BED_A + Math.cos(a) * .32, 1.55 + Math.sin(a * 1.7) * .12, BED_Z + .25 + Math.sin(a) * .12); }
      }
      // Bogdanov in bed: lies back on "masaya yattı", sick on "düştü", writes at the end, gone on "kaybetti"
      const y = cast.yatak;
      const lieB = ramp(t, T('masaya') - .1, T('yattı.') + .1), gone = bedsEnd ? ramp(t, T('54') + .2, T('kaybetti.') + .3) : 0;
      const sinkB = bedsEnd ? .14 + .1 * gone : .08 * lieB + .12 * sick;
      inBed(y, BED_B, { sink: sinkB, pitch: bedsEnd ? -.08 - .06 * gone : -.06 * lieB - .06 * sick });
      if (!bedsEnd) {
        y.draw({ expr: sick > .5 ? 'worried' : t > A('kez') && t < A('sıtma') ? 'focused' : 'proud', look: -.45, lookY: .2, blink: bl(8, A('kez'), A('ikisi')), sweat: sick, noArmL: true, armR: [12, 8],
          lit: -1, shade: NIGHT, rim: { color: WARM, a: .38 } });
        dyn.armB.set(-1, dyn.hB, { sag: .06, tint });
      } else {
        // writing: the pen follows the end of the handwriting every frame; on "54" it stops, then drops
        const u = lin(t, T('son') + .5, T('54') - .05); drawNotebook(u);
        const tip = dyn.nbTip || [.15, .14], nb = dyn.nb;
        const P = nb.localToWorld(V((tip[0] - .5) * .34, (.5 - tip[1]) * .24, .004));
        const drop = ramp(t, T('yaşında') - .1, T('hayatını') + .2);
        P.y += .004 + drop * -.002; P.x += drop * .06; P.z += drop * .05;
        dyn.pen.visible = true; dyn.pen.position.copy(P);
        if (drop > 0) dyn.pen.quaternion.setFromUnitVectors(V(0, 1, 0), dyn.penAxis.clone().lerp(V(1, .1, .2).normalize(), drop).normalize()); else dyn.pen.quaternion.setFromUnitVectors(V(0, 1, 0), dyn.penAxis);
        const hand = P.clone().addScaledVector(dyn.penAxis, .07); hand.y += drop * .03;
        y.draw({ expr: gone > .5 ? 'neutral' : 'focused', look: -.2, lookY: .85, gazeX: (tip[0] - .5) * 2, gazeY: 1, lid: gone * .7, blink: gone > .9 ? 1 : bl(9, A('son') + .5),
          sweat: .6 * (1 - gone), noArmR: true, armL: [12, 8], lit: 1, shade: '#c9c6ea', rim: { color: '#ffb466', a: .45 * deskOn } });
        dyn.armPen.set(1, hand, { sag: .05, tint });
      }
      if (bedsEnd) { dyn.flask.visible = true; dyn.flask.position.set(1.52, .72, -2.45); dyn.flask.rotation.set(0, 0, 0); }
    }
  } else if (where === 'street') {
    const news = t > T('İddiaları') - .3;
    if (!news) {
      const b = cast.palto; b.show(); b.place(199.2, 0, -3.85, cam, tint);
      const self = t > A('kendi') - .1, decide = t > A('karar');
      b.draw({ expr: decide ? 'smug' : self ? 'proud' : t > A("Moskova'da") ? 'smile' : 'neutral', look: t > A("Moskova'da") && t < A('teorisini') ? .6 : .25, lookY: t > A("Moskova'da") && t < A('teorisini') ? -.9 : 0, brow: decide ? .6 : 0,
        blink: bl(10, A("Moskova'da"), A('kendi') - .1, A('karar')), armR: self ? [30, 170] : [14, 10], armL: [14, 10], lean: self ? -2 : 0,
        lit: 1, shade: NIGHT, rim: { color: WARM, a: .45 } });
      b.castFrom(dyn.streetLamp);
    } else {
      const n = cast.gazeteci; n.show(); n.place(200.85, 0, -3.45, cam, tint);
      n.draw({ expr: 'surprised', mouth: .6 + .4 * Math.abs(Math.sin(t * 9)), look: -.3, lookY: -.2, blink: bl(11), armR: [160, 10], propR: PAPER, armL: [40, 60], lean: -3,
        lit: 1, shade: NIGHT, rim: { color: WARM, a: .45 } });
      n.castFrom(dyn.streetLamp);
      // newspapers whirl up the street; one flies at the lens on "yayıldı"
      const t0 = T('yayıldı') - .25;
      dyn.papers.forEach((p, i) => {
        const u = t - t0 - i * .07; if (u < 0) return; p.visible = true;
        const k = u * 1.2, a = i * 1.7;
        if (i === 0) { const z = Math.min(u * 1.6, 1); p.position.set(200.75 - .3 * (1 - z), 1.4 + .1 * Math.sin(u * 3), -3.2 + z * 2.2); p.rotation.set(-.1 + .2 * Math.sin(u * 5), .2 * (1 - z), .3 * (1 - z)); p.lookAt(cam.position); p.rotateZ(.12 * Math.sin(u * 4)); }
        else { p.position.set(200.6 + Math.cos(a) * (.6 + k), .5 + k * 1.6 + Math.sin(u * 4 + a) * .2, -3.3 + Math.sin(a) * .7); p.rotation.set(u * 3 + a, u * 2.2, u * 1.4 + a); }
      });
    }
  } else {
    // ---- tube: the cells flow toward the lens; on "uyuşmazlığını" they gather in clumps, on "kaldıramadı" the flow stops
    const clump = ramp(t, T('uyuşmazlığını') - .1, T('kaldıramadı.') - .05);
    const stopT = T('kaldıramadı.') + .1, ft = t < stopT ? t : stopT + (1 - Math.exp(-(t - stopT) * 3)) * .3;
    dyn.cellData.forEach((c, i) => {
      const z = 1.2 - ((c.z0 + ft * 3.2) % 44);
      const free = V(c.x, c.y, z), C = dyn.clumps[c.cl], cl = C.clone().add(V(Math.cos(i * 2.4) * .28, Math.sin(i * 1.7) * .28, Math.sin(i * 3.1) * .25));
      const k = clump * (z < 1 && z > -16 ? 1 : 0);
      const P = free.lerp(cl, k);
      E.set(c.tilt + ft * .7 * (1 - clump), c.spin + ft * .5, 0); Q.setFromEuler(E);
      M4.compose(P, Q, V(c.s, c.s, c.s)); dyn.cells.setMatrixAt(i, M4);
    });
    dyn.cells.instanceMatrix.needsUpdate = true;
    dyn.ys.forEach((y, i) => { if (clump <= 0) return; y.s.visible = true; const C = dyn.clumps[y.k]; const free = V(Math.cos(y.a + t) * y.r, Math.sin(y.a + t) * y.r, y.z); free.lerp(C.clone().add(V(Math.cos(i) * .18, Math.sin(i * 1.3) * .18, .1)), clump); y.s.position.copy(free).add(V(300, 0, 0)); y.s.material.rotation = y.a + t * (1 - clump); });
    dyn.tubeEnd.material.color.copy(HDR(2.4 - clump * .6, 1.5 - clump * .5, .9 - clump * .3));
  }
  for (const s of Object.values(smokes)) s.update(t);

  // ---- look per set / beat
  const focusOn = (p, coc, range) => ({ focus: cam.position.distanceTo(p), coc, range });
  let look;
  if (where === 'lab') {
    if (t < T('Alexander') + .1) look = focusOn(V(.3, 1.6, -.6), 7, 1.6);
    else if (t < T('yaşlanmayı') + .3) look = { focus: 5, coc: 2, range: 6 };
    else if (t < T('inanıyordu:')) look = focusOn(dyn.clock, 6, 1.2);
    else if (t < T('Bogdanov', 2)) look = focusOn(V(0, .9, -2.3), 5, 1.6);
    else if (t < T('genç', 1) + .2) look = focusOn(V(-1.9, 2.2, -2.95), 7, .9);
    else if (t < T('İlk', 2) + .3) look = focusOn(V(0, .9, -2.3), 5, 1.6);
    else if (t < T('Gözlüğü')) look = focusOn(dyn.brd, 5, 1.0);
    else if (t < T('İddiaları')) look = focusOn(V(-1.62, 1.45, .55), 7, 1.2);
    else if (t < T('1928')) look = focusOn(V(-.6, 1.0, -2.3), 5, 1.4);
    else if (t < T('12.') + .3) look = focusOn(V(-1.9, 2.2, -2.95), 7, .9);
    else if (t < T('masaya')) look = focusOn(dyn.brd, 5, 1.0);
    else if (t < T('Nakilden', 2) + .2) look = focusOn(V(t < T('kez') ? .9 : -.9, 1.1, -2.35), 5, 1.4);
    else if (t < T('ikisi')) look = focusOn(dyn.clock, 6, 1.2);
    else if (!end) look = focusOn(V(0, 1.0, -2.3), 4, 2);
    else if (t < T('son') + .5) look = focusOn(V(.95, 1.0, -2.3), 5, 1.4);
    else if (t < T('kaybetti.') + .5) look = focusOn(V(.93, .64, -1.88), 8, .45);
    else look = { focus: 4, coc: 1.5 * (1 - lin(t, T('kaybetti.') + .5, T('kaybetti.') + 1.5)), range: 4 };
    Object.assign(look, { sat: 1.18, lift: [.1, .09, .16], bloom: .85, vignette: end ? .32 : .2 });
    if (t > T('1928') && t < T('1928') + .12) look.flash = .45;                    // lightning on the cut to 1928
  } else if (where === 'street') {
    look = { ...focusOn(t > T('İddiaları') - .3 ? V(200.85, 1.3, -3.45) : t > T("Moskova'da") + .3 && t < T('teorisini') + .3 ? V(200, 3.6, -5.5) : V(199.2, 1.4, -3.85), 5, 3), sat: 1.2, lift: [.09, .09, .18], bloom: .9, vignette: .22 };
  } else look = { focus: 5, coc: 3, range: 4, sat: 1.25, lift: [.12, .05, .12], bloom: 1.0, vignette: .3 };
  look.tint = GRADE[where];
  look.blur = cp.moving > .15 ? 16 : 0;
  look.captions = false;                                 // no subtitles in this short
  return look;
}
const GRADE = { lab: [1.0, .98, 1.02], street: [.98, .98, 1.04], tube: [1.03, .97, 1.0] };
const FACE = { lab: [1, .985, .965], street: [.975, .98, 1], tube: [1, .96, .96] };
