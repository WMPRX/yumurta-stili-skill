// At Oynatmak — birbirinin arkasından iş çevirmek ("birinin arkasından at oynatmak").
// Kirpi wants to pay a colleague back the same way; Baykuş, playing chess at the café, shows him the knight and the hand that moves it.
// Every shot and expression is pinned to a script line L(i) or a word W('...').
export const NAME = 'at-oynatmak';
export const FPS = 30;
export const BRAND = { ad: 'Akşam Çayı' };                         // your channel name: watermark + end card title
export const CAST = { HOCA: { tur: 'baykus' }, CIRAK: { tur: 'kirpi' } };
export const MENTOR = 'HOCA';
export const MUSIC = { key: 'Dm', bpm: 64 };

export function build({ W, L }) {
  const K = { set: 'kafe', masa: 'satranc' };                       // the chess board sits on the table in every two-shot
  const FISILTI = { kimler: ['kedi', 'kirpi'], fisilti: true };     // someone whispering into someone's ear, in a lit window
  const EL = { el: '#8b7259', kol: '#4f5140' };                      // Baykuş's hand and sleeve
  const jumpAt = W('Ama') - .1, bigAt = L(13).start - .2;
  // 24 shots over ~88 s of voice: median ≈ 3.7 s. Types: 7 mentor, 7 young one, 3 two-shots, 1 wide, 6 inserts.
  const shots = [
    { at: 0,                        kind: 'nesne', prop: 'pencere', opts: FISILTI },                  // hook: the scheming itself, in frame 0
    { at: L(1).start - .3,          kind: 'ikili', ...K },
    { at: W('Toplantıda') - .1,     kind: 'tek', who: 'CIRAK', ots: 'HOCA', ...K },
    { at: L(3).start - .25,         kind: 'tek', who: 'HOCA', ...K },
    { at: L(4).start - .2,          kind: 'yakin', who: 'CIRAK', ...K },
    { at: W('Bakalım') - .1,        kind: 'ikili', ...K },
    { at: L(5).start - .25,         kind: 'tek', who: 'HOCA', ots: 'CIRAK', ...K },
    { at: W('ona') - .1,            kind: 'nesne', prop: 'pencere', opts: { kimler: ['kirpi', 'kedi'], fisilti: true }, push: 0 },
    { at: L(6).start - .2,          kind: 'yakin', who: 'CIRAK', ...K },
    { at: L(7).start - .25,         kind: 'nesne', prop: 'satranc', opts: {}, push: .06 },
    { at: L(8).start - .2,          kind: 'tek', who: 'CIRAK', ...K },
    { at: L(9).start - .25,         kind: 'tek', who: 'HOCA', ots: 'CIRAK', ...K },
    { at: jumpAt,                   kind: 'nesne', prop: 'satranc', opts: { ...EL, zipla: W('oynatan') - jumpAt }, push: .05 },
    { at: L(10).start - .2,         kind: 'yakin', who: 'CIRAK', ...K },
    { at: L(11).start - .25,        kind: 'tek', who: 'HOCA', ...K },
    { at: L(12).start - .2,         kind: 'genis', ...K, push: -.16 },                                 // a pull-out that opens the café
    { at: W('ikiniz') - .1,         kind: 'tek', who: 'CIRAK', ots: 'HOCA', ...K },                     // the listener
    { at: bigAt,                    kind: 'nesne', prop: 'satranc', opts: { ...EL, zipla: W('el') - bigAt - .3 }, push: .3 },   // one big move
    { at: L(14).start - .2,         kind: 'yakin', who: 'HOCA', ...K },
    { at: W('Yüze') - .1,           kind: 'ikili', ...K },
    { at: L(15).start - .2,         kind: 'tek', who: 'CIRAK', ...K },
    { at: W('Bitirmek') - .1,       kind: 'tek', who: 'HOCA', ...K },
    { at: L(16).start - .25,        kind: 'nesne', prop: 'pencere', opts: FISILTI, push: .15 },
    { at: L(17).start - .25,        kind: 'tek', who: 'HOCA', ...K },                                   // the mentor carries the end card
  ];
  const expr = [
    { at: 0, who: 'CIRAK', expr: 'kizgin' }, { at: 0, who: 'HOCA', expr: 'bilge' },
    { at: L(2).start, who: 'CIRAK', expr: 'endiseli' }, { at: W('suçlamış.'), who: 'CIRAK', expr: 'kizgin' },
    { at: L(3).start, who: 'HOCA', expr: 'notr' },
    { at: L(4).start, who: 'CIRAK', expr: 'kizgin' },
    { at: L(5).start, who: 'HOCA', expr: 'bilge' },
    { at: L(6).start, who: 'CIRAK', expr: 'saskin' },
    { at: L(8).start, who: 'CIRAK', expr: 'dusunceli' },
    { at: L(9).start, who: 'HOCA', expr: 'gulumse' }, { at: W('Ama'), who: 'HOCA', expr: 'bilge' },
    { at: L(10).start, who: 'CIRAK', expr: 'kizgin' }, { at: W('Yani'), who: 'CIRAK', expr: 'uzgun' },
    { at: L(11).start, who: 'HOCA', expr: 'notr' }, { at: W('yüzüne'), who: 'HOCA', expr: 'bilge' },
    { at: L(12).start, who: 'CIRAK', expr: 'uzgun' },
    { at: L(15).start, who: 'CIRAK', expr: 'dusunceli' },
    { at: L(16).start, who: 'HOCA', expr: 'notr' }, { at: W('kimse'), who: 'HOCA', expr: 'bilge' },
  ];
  const poz = [
    { at: W('Susma') - .1, who: 'HOCA', pose: 'el' },
    { at: L(8).start - .1, who: 'CIRAK', pose: 'cene' },
  ];
  return { shots, expr, poz, end: { at: L(17).start } };
}
