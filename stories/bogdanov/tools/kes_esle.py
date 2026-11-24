# kes_esle.py — tools/bosluk_kes.py (same pause targets) + remaps the word times through the cuts and the tempo,
# so words.json stays exact (the API's alignment) instead of being heard again by Whisper.
#   python kes_esle.py <in.wav> <raw_words.json> <out.wav> <out_words.json> [tempo]
import sys, json, subprocess
import numpy as np
src, wj, dst, wout = sys.argv[1:5]; tempo = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
SR = 24000
y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).copy()
words = json.load(open(wj, encoding='utf-8'))['words']
hop = SR // 100
fr = np.sqrt(np.mean(y[:len(y) // hop * hop].reshape(-1, hop) ** 2, 1) + 1e-12); db = 20 * np.log10(fr)
quiet = db < np.percentile(db, 95) - 40
runs, i = [], 0
while i < len(quiet):
    if quiet[i]:
        j = i
        while j < len(quiet) and quiet[j]: j += 1
        runs.append((i * hop, j * hop)); i = j
    else: i += 1
def kind(t):
    w = [x for x in words if x['start'] < t]
    if not w: return 'lead'
    p = w[-1]['word'].rstrip('"\'')
    return 'end' if p[-1:] in '.:?!' else 'comma' if p[-1:] in ',;' else 'mid'
TARGET = {'lead': .03, 'end': .22, 'comma': .14, 'mid': .09}
keep, cur = [], 0
for a, b in runs:
    dur = (b - a) / SR
    k = 'lead' if a == 0 else 'tail' if b >= len(y) - hop else kind((a + b) / 2 / SR)
    tgt = .30 if k == 'tail' else TARGET[k]
    if dur <= tgt + .02: continue
    h = int(tgt * SR / 2)
    cut_a, cut_b = (a, b - int(tgt * SR)) if k == 'lead' else (a + h, b - h) if k != 'tail' else (a + int(tgt * SR), b)
    keep.append((cur, cut_a)); cur = cut_b
keep.append((cur, len(y)))
xf = int(.008 * SR); out = y[keep[0][0]:keep[0][1]].copy(); starts = [0]
for a, b in keep[1:]:
    seg = y[a:b].copy()
    if len(out) > xf and len(seg) > xf:
        r = np.linspace(0, 1, xf, dtype=np.float32); out[-xf:] = out[-xf:] * (1 - r) + seg[:xf] * r; seg = seg[xf:]; starts.append(len(out) - xf)
    else: starts.append(len(out))
    out = np.concatenate([out, seg])
def remap(t):
    s = t * SR
    for (a, b), o in zip(keep, starts):
        if s < a: return o / SR / tempo                      # inside a removed pause: snap to the join
        if s <= b: return (o + s - a) / SR / tempo
    return len(out) / SR / tempo
nw = [{'word': w['word'], 'start': round(remap(w['start']), 3), 'end': round(remap(w['end']), 3)} for w in words]
af = ['-af', f'atempo={tempo}'] if tempo != 1.0 else []
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', *af, '-ar', '48000', '-c:a', 'pcm_s16le', dst], input=out.astype(np.float32).tobytes(), check=True)
json.dump({'words': nw, 'duration': round(len(out) / SR / tempo, 3)}, open(wout, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('length %.2fs -> %.2fs -> x%.2f = %.2fs | %.2f w/s' % (len(y) / SR, len(out) / SR, tempo, len(out) / SR / tempo, len(nw) / nw[-1]['end']))
