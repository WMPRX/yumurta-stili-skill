// Soğuk Çay — sample story for the sepya-sohbet style (79 s of voice + the end card).
// Every shot and expression is pinned to a script line L(i) or a word W('...'), never to typed seconds:
// re-record the voice, re-run kelime_saat.py, and everything moves with it.
export const NAME = 'soguk-cay';
export const FPS = 30;
export const BRAND = { ad: 'Akşam Çayı' };                         // your channel name: watermark + end card title
export const CAST = {
  HOCA: { tur: 'baykus' },                                          // the mentor (speaks the last line)
  CIRAK: { tur: 'kirpi' },                                          // the young one
};
export const MENTOR = 'HOCA';
export const MUSIC = { key: 'Am', bpm: 66 };                       // audio/mix.py: soft piano bed

export function build({ W, L }) {
  const K = { set: 'kafe' };
  const TEL = { kimden: 'Deniz', el: '#ecdfc9', mesajlar: [
    { ben: false, metin: 'Tamam, görüşürüz.' }, { ben: true, metin: 'Görüşürüz.' }, { taslak: true, metin: 'Seni özledim' }] };
  // 21 shots over ~79 s of voice: median ≈ 3.6 s (references 3.4-5.2). Types: 7 mentor, 6 young one, 2 two-shots, 5 inserts, 1 wide.
  const shots = [
    { at: 0,                      kind: 'nesne', prop: 'telefon', opts: TEL },                        // hook: the key object in frame 0
    { at: L(1).start - .3,        kind: 'ikili', ...K },
    { at: W('Küstük,') - .1,      kind: 'nesne', prop: 'pencere', opts: { kim: 'kirpi' }, push: 0 },    // a held insert (8 % of shots hold still)
    { at: L(4).start - .2,        kind: 'yakin', who: 'CIRAK', ...K },
    { at: L(5).start - .25,       kind: 'ikili', ...K },
    { at: L(6).start - .2,        kind: 'tek', who: 'CIRAK', ots: 'HOCA', ...K },
    { at: L(7).start - .25,       kind: 'tek', who: 'HOCA', ...K },
    { at: L(8).start - .2,        kind: 'tek', who: 'CIRAK', ...K },
    { at: L(9).start - .25,       kind: 'nesne', prop: 'cay', opts: { buhar: false, dolu: .8 } },
    { at: L(11).start - .1,       kind: 'tek', who: 'HOCA', ots: 'CIRAK', ...K },
    { at: L(12).start - .2,       kind: 'yakin', who: 'CIRAK', ...K },
    { at: L(13).start - .25,      kind: 'tek', who: 'HOCA', ...K },
    { at: L(14).start - .2,       kind: 'genis', ...K, push: -.16 },                                     // a pull-out that opens the room
    { at: L(15).start - .2,       kind: 'nesne', prop: 'telefon', push: .08, opts: TEL },
    { at: L(16).start - .2,       kind: 'tek', who: 'HOCA', ots: 'CIRAK', ...K },
    { at: L(17).start - .2,       kind: 'yakin', who: 'CIRAK', ...K },
    { at: L(18).start - .25,      kind: 'tek', who: 'HOCA', ...K },
    { at: W('Göndermezsen,') - .2, kind: 'tek', who: 'CIRAK', ots: 'HOCA', ...K },                       // the listener
    { at: L(19).start - .25,      kind: 'yakin', who: 'HOCA', ...K },
    { at: W('sessizlikler') - .3, kind: 'nesne', prop: 'cay', opts: { buhar: false, dolu: .8 }, push: .22 },   // one big move per video
    { at: L(20).start - .25,      kind: 'tek', who: 'HOCA', ...K },                                       // the mentor carries the end card
  ];
  const expr = [
    { at: 0, who: 'CIRAK', expr: 'uzgun' }, { at: 0, who: 'HOCA', expr: 'bilge' },
    { at: L(2).start, who: 'CIRAK', expr: 'endiseli' },
    { at: W('özledim.'), who: 'CIRAK', expr: 'utangac' },
    { at: L(6).start, who: 'CIRAK', expr: 'dusunceli' }, { at: W('Belki'), who: 'CIRAK', expr: 'endiseli' },
    { at: L(7).start, who: 'HOCA', expr: 'notr' }, { at: L(8).start, who: 'CIRAK', expr: 'uzgun' },
    { at: L(9).start, who: 'HOCA', expr: 'bilge' }, { at: L(10).start, who: 'CIRAK', expr: 'notr' },
    { at: W('soğudu.'), who: 'HOCA', expr: 'gulumse' },
    { at: L(12).start, who: 'CIRAK', expr: 'saskin' },
    { at: L(13).start, who: 'HOCA', expr: 'bilge' },
    { at: L(17).start, who: 'CIRAK', expr: 'endiseli' },
    { at: L(18).start, who: 'HOCA', expr: 'notr' }, { at: W('Göndermezsen,'), who: 'HOCA', expr: 'bilge' },
  ];
  const poz = [ { at: W('soğudu.') - .1, who: 'HOCA', pose: 'el' } ];
  return { shots, expr, poz, end: { at: L(20).start } };
}
