// chess.js — a chess board in perspective with flat outlined pieces, for inserts (props.satranc) and the café table (masa: 'satranc').
import { fillStroke } from './util.js';
import { LINE } from './chars.js';

// a piece standing at (x, y) (its base centre), h = height in px
export function piece(g, type, x, y, h, white = true, k = 1, lw = 3) {
  const fill = white ? '#ebe1cc' : '#3b2a20', L = LINE;
  g.save(); g.translate(x, y); g.scale(h, h); g.lineWidth = lw * k / h; g.lineJoin = 'round';
  g.beginPath(); g.ellipse(0, 0, .3, .07, 0, 0, 7); fillStroke(g, fill, L, lw * k / h);           // base
  if (type === 'piyon') {
    g.beginPath(); g.moveTo(-.2, -.02); g.quadraticCurveTo(-.08, -.25, -.1, -.45); g.lineTo(.1, -.45); g.quadraticCurveTo(.08, -.25, .2, -.02); g.closePath(); fillStroke(g, fill, L, lw * k / h);
    g.beginPath(); g.arc(0, -.58, .16, 0, 7); fillStroke(g, fill, L, lw * k / h);
  } else if (type === 'at') {
    g.beginPath(); g.moveTo(-.22, -.03); g.lineTo(-.18, -.35); g.quadraticCurveTo(-.26, -.6, -.08, -.85);   // neck back + mane
    g.lineTo(-.02, -1.0); g.lineTo(.05, -.88);                                                        // ear
    g.quadraticCurveTo(.2, -.8, .3, -.6); g.lineTo(.27, -.5); g.quadraticCurveTo(.12, -.52, .06, -.48); // muzzle
    g.quadraticCurveTo(.2, -.3, .22, -.03); g.closePath(); fillStroke(g, fill, L, lw * k / h);
    g.beginPath(); g.arc(.05, -.72, .025, 0, 7); g.fillStyle = white ? L : '#ebe1cc'; g.fill();         // eye
    g.beginPath(); g.moveTo(-.16, -.62); g.quadraticCurveTo(-.2, -.4, -.12, -.2); g.strokeStyle = white ? 'rgba(42,26,18,.5)' : 'rgba(235,225,204,.4)'; g.stroke();
  } else if (type === 'sah') {
    g.beginPath(); g.moveTo(-.22, -.02); g.quadraticCurveTo(-.1, -.4, -.16, -.75); g.lineTo(.16, -.75); g.quadraticCurveTo(.1, -.4, .22, -.02); g.closePath(); fillStroke(g, fill, L, lw * k / h);
    g.beginPath(); g.ellipse(0, -.78, .2, .06, 0, 0, 7); fillStroke(g, fill, L, lw * k / h);
    g.beginPath(); g.rect(-.035, -1.05, .07, .25); g.rect(-.11, -.98, .22, .07); fillStroke(g, fill, L, lw * k / h);
  }
  g.restore();
}

// board: corners given as near / far edge centre and width; returns a mapper from (file, rank) in 0..8 to screen
export function board(g, { cx, nearY, farY, nearW, farW, k = 1, lw = 3 }) {
  const P = (u, v) => {                     // u across 0..8, v from far (0) to near (8)
    const t = Math.pow(v / 8, 1.25), y = farY + (nearY - farY) * t, w = farW + (nearW - farW) * t;
    return [cx - w / 2 + w * u / 8, y, w / 8];
  };
  for (let j = 0; j < 8; j++) for (let i = 0; i < 8; i++) {
    const a = P(i, j), b = P(i + 1, j), c = P(i + 1, j + 1), d = P(i, j + 1);
    g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.lineTo(c[0], c[1]); g.lineTo(d[0], d[1]); g.closePath();
    g.fillStyle = (i + j) % 2 ? '#7a5638' : '#d9c7a4'; g.fill();
  }
  const A = P(0, 0), B = P(8, 0), C = P(8, 8), D = P(0, 8);
  g.beginPath(); g.moveTo(A[0], A[1]); g.lineTo(B[0], B[1]); g.lineTo(C[0], C[1]); g.lineTo(D[0], D[1]); g.closePath();
  g.strokeStyle = LINE; g.lineWidth = lw * k; g.stroke();
  // frame edge (thickness toward the viewer)
  g.beginPath(); g.moveTo(D[0], D[1]); g.lineTo(C[0], C[1]); g.lineTo(C[0], C[1] + 22 * k * (nearW / 1000)); g.lineTo(D[0], D[1] + 22 * k * (nearW / 1000)); g.closePath();
  fillStroke(g, '#4a2c1c', LINE, lw * k);
  return (u, v) => { const p = P(u + .5, v + .5); return [p[0], p[1] + p[2] * .18, p[2]]; };
}

// a standard little position: [type, file, rank (0 = far), white]
export const POZ = [
  ['sah', 4, 0, false], ['piyon', 2, 1, false], ['piyon', 5, 1, false], ['at', 6, 2, false], ['piyon', 3, 3, false],
  ['piyon', 4, 4, true], ['at', 2, 5, true], ['piyon', 5, 6, true], ['piyon', 1, 6, true], ['sah', 4, 7, true],
];
export function pieces(g, map, list, hk, k, lw, skip = -1) {
  const items = list.map((p, i) => ({ p, i, at: map(p[1], p[2]) })).sort((a, b) => a.at[1] - b.at[1]);
  for (const { p, i, at } of items) if (i !== skip) piece(g, p[0], at[0], at[1], at[2] * hk * (p[0] === 'sah' ? 1.35 : p[0] === 'at' ? 1.15 : .9), p[3], k, lw);
}
