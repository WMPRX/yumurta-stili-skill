# olc.py — measure a video the way the six references were measured, and compare it with the target ranges.
#   python tools/olc.py video.mp4 [--json=out.json]
# Prints one table: measurement | reference range (median) | this video | OK / LOW / HIGH.
# Method (analiz/README.md): frames scaled to 180×320; the caption band (64-86 % of the height) and the end card are left out;
# cuts = local-median frame difference + histogram jump; push-in = ECC between the first and last frame of each shot (blurred,
# so the scanlines do not count); scanlines = FFT of the vertical high-pass profile; loudness = ffmpeg ebur128.
import sys, json, subprocess
import numpy as np, cv2

p = [a for a in sys.argv[1:] if not a.startswith('--')][0]
opt = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--'))

# reference ranges: [low, median, high] of THIS tool run on the six references (analiz/veri/olc_referans.json)
REF = {
    'sure_sn':            ([77.6, 87.0, 94.8],  'video length (s)'),
    'plan_sn_ortanca':    ([3.4, 3.85, 5.23],    'median shot length (s)'),
    'kesme_dakika':       ([12.9, 13.3, 15.9],  'cuts per minute'),
    'itme_plan_pct':      ([3.22, 3.81, 4.68],     'median push-in per shot, %'),
    'itme_olan_plan_pct': ([79.2, 87.8, 95.0],        'shots that push in > 1 %'),
    'y50':                ([0.118, 0.155, 0.192],  'median brightness'),
    'y5':                 ([0.0274, 0.049, 0.0588],  'dark end (p5)'),
    'kontrast':           ([0.443, 0.559, 0.624],    'contrast p95 - p5'),
    'a':                  ([5.88, 6.67, 7.51],     'Lab a* (red)'),
    'b':                  ([8.22, 9.81, 13.0],    'Lab b* (yellow)'),
    'c50':                ([10.0, 12.9, 16.1],  'chroma median (Lab C*)'),
    'c90':                ([15.7, 17.5, 19.3],  'chroma p90'),
    'kose':               ([0.168, 0.223, 0.315],     'corner / centre brightness'),
    'tarama_periyot':     ([0.01445, 0.01445, 0.01446], 'scanline period (fraction of height)'),
    'tarama_genlik':      ([0.0357, 0.0386, 0.044],  'scanline amplitude (relative)'),
    'tarama_kayma':       ([0.00033, 0.00037, 0.00044], 'scanline slide per frame (fraction of height, + = down)'),
    'altyazi_y':          ([0.72, 0.764, 0.764],  'caption centre (fraction of height)'),
    'altyazi_h':          ([0.0273, 0.0281, 0.0281], 'caption glyph height (fraction of height)'),
    'lufs':               ([-14.2, -14.1, -14.1], 'integrated loudness (LUFS)'),
    'kapanis_sn':         ([7.3, 7.85, 8.27],     'end: from the fade-out of the last shot to the end (s)'),
}

cap = cv2.VideoCapture(p); fps = cap.get(5); n = int(cap.get(7)); Wv, Hv = int(cap.get(3)), int(cap.get(4))
rows, prev, smalls = [], None, []
band = slice(int(.64 * 320), int(.86 * 320))
k = 0
while True:
    ok, f = cap.read()
    if not ok: break
    s = cv2.resize(f, (180, 320), interpolation=cv2.INTER_AREA)
    g = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY).astype(np.float32)
    m = np.ones((320, 180), bool); m[band] = False
    lab = cv2.cvtColor(s, cv2.COLOR_BGR2LAB).astype(np.float32)
    Y = g[m] / 255; A = lab[..., 1][m] - 128; B = lab[..., 2][m] - 128; C = np.hypot(A, B)
    r = dict(y50=np.median(Y), y5=np.percentile(Y, 5), y95=np.percentile(Y, 95), a=A.mean(), b=B.mean(), c50=np.median(C), c90=np.percentile(C, 90),
             kose=(g[:40, :25].mean() + g[:40, -25:].mean() + g[-40:, :25].mean() + g[-40:, -25:].mean()) / 4 / max(g[120:200, 60:120].mean(), 1), mean=g.mean() / 255)
    if prev is not None:
        r['diff'] = float(np.abs(s.astype(np.float32) - prev.astype(np.float32)).mean())
        h1 = cv2.calcHist([s], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3); h0 = cv2.calcHist([prev], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3)
        r['hist'] = float(cv2.compareHist(h0, h1, cv2.HISTCMP_BHATTACHARYYA))
    rows.append(r); prev = s; k += 1
N = len(rows)
mean = np.array([r['mean'] for r in rows])
k2 = N - 1
while k2 > 0 and mean[k2] < .12: k2 -= 1                                # the fade into the end card
diff = np.array([r.get('diff', 0) for r in rows]); hist = np.array([r.get('hist', 0) for r in rows])
med = np.array([np.median(diff[max(0, i - 8):i + 9]) for i in range(N)])
cand = [i for i in range(1, k2) if diff[i] > max(12, 4 * med[i]) and hist[i] > .12]
cuts = []
for c in cand:
    if not cuts or c - cuts[-1] > 3: cuts.append(c)
cuts = [c for j, c in enumerate(cuts) if not ((j + 1 < len(cuts) and cuts[j + 1] - c < 8) or (j > 0 and c - cuts[j - 1] < 8))]   # flashes are not cuts
bounds = [0] + cuts + [k2 + 1]
shots = [(a, b) for a, b in zip(bounds[:-1], bounds[1:]) if b - a > 10]

def grab(i):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = cap.read()
    g = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32), (0, 0), 4 * Hv / 1280)
    g[int(.64 * Hv):int(.86 * Hv)] = 0
    return cv2.resize(g, (360, 640))
zooms = []
for a, b in shots:
    M = np.eye(2, 3, dtype=np.float32)
    try:
        _, M = cv2.findTransformECC(grab(a + 4), grab(b - 4), M, cv2.MOTION_AFFINE, (3, 200, 1e-6), None, 5)
        zooms.append((np.sqrt(abs(np.linalg.det(M[:, :2]))) - 1) * 100)
    except cv2.error: pass
zooms = np.array(zooms)

# scanlines on 12 frames
per, amp, roll = [], [], []
for t in np.linspace(.1, .85, 12):
    i = int(t * k2); cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    prof = []
    for j in range(2):
        ok, f = cap.read(); g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
        reg = g[int(.08 * Hv):int(.6 * Hv), int(.1 * Wv):int(.9 * Wv)]
        hp = reg - cv2.GaussianBlur(reg, (0, 0), sigmaX=.1, sigmaY=6 * Hv / 1280)
        prof.append((hp / (cv2.GaussianBlur(reg, (0, 0), 6 * Hv / 1280) + 5)).mean(1))
    F = np.abs(np.fft.rfft(prof[0] - prof[0].mean())); fr = np.fft.rfftfreq(len(prof[0]))
    lo = int(len(prof[0]) * .008)
    k0 = np.argmax(F[lo:]) + lo; P = 1 / fr[k0]
    y = np.arange(len(prof[0])); sn, cs = np.sin(2 * np.pi * y / P), np.cos(2 * np.pi * y / P)
    per.append(P / Hv); amp.append(np.hypot((prof[0] * sn).mean() * 2, (prof[0] * cs).mean() * 2))
    ph0 = np.arctan2((prof[0] * cs).mean(), (prof[0] * sn).mean()); ph1 = np.arctan2((prof[1] * cs).mean(), (prof[1] * sn).mean())
    roll.append(-((ph1 - ph0 + np.pi) % (2 * np.pi) - np.pi) / (2 * np.pi) * P / Hv)

# captions: white glyphs in the band, every half second
cy, ch = [], []
for i in range(0, k2, int(fps / 2)):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, f = cap.read()
    b = f[int(.62 * Hv):int(.86 * Hv)]; hsv = cv2.cvtColor(b, cv2.COLOR_BGR2HSV)
    wm = ((hsv[..., 2] > 215) & (hsv[..., 1] < 45)).astype(np.uint8)
    cnt, lab_, st, _ = cv2.connectedComponentsWithStats(wm, 8)
    comps = [j for j in range(1, cnt) if st[j, 4] > 30 * (Hv / 1280) ** 2 and st[j, 3] > 12 * Hv / 1280]
    if comps:
        y0 = min(st[j, 1] for j in comps); y1 = max(st[j, 1] + st[j, 3] for j in comps)
        cy.append((int(.62 * Hv) + (y0 + y1) / 2) / Hv); ch.append(np.median([st[j, 3] for j in comps]) / Hv)

lufs = None
try:
    e = subprocess.run(['ffmpeg', '-nostats', '-i', p, '-vn', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    lufs = float(e[e.rindex('I:'):].split()[1])
except Exception: pass

R = [r for r in rows[:k2]]
res = {
    'sure_sn': N / fps, 'plan_sn_ortanca': float(np.median([(b - a) / fps for a, b in shots])), 'kesme_dakika': len(cuts) / (k2 / fps) * 60,
    'itme_plan_pct': float(np.median(zooms)) if len(zooms) else None, 'itme_olan_plan_pct': float((zooms > 1).mean() * 100) if len(zooms) else None,
    **{k: float(np.median([r[k] for r in R])) for k in ['y50', 'y5', 'a', 'b', 'c50', 'c90', 'kose']},
    'kontrast': float(np.median([r['y95'] - r['y5'] for r in R])),
    'tarama_periyot': float(np.median(per)), 'tarama_genlik': float(np.median(amp)), 'tarama_kayma': float(np.median(roll)),
    'altyazi_y': float(np.median(cy)) if cy else None, 'altyazi_h': float(np.median(ch)) if ch else None,
    'lufs': lufs, 'kapanis_sn': (N - k2) / fps,
}
print(f'{p}  {Wv}x{Hv}  {fps:.0f} fps  {N} frames  {len(shots)} shots')
print(f"{'olcu':22s} {'referans (ortanca)':>26s} {'bu video':>10s}")
for key, (rng_, label) in REF.items():
    v = res.get(key)
    if v is None: print(f'{key:22s} {"":>26s} {"-":>10s}  ({label})'); continue
    lo, md, hi = rng_; tag = 'OK' if lo <= v <= hi else ('DUSUK' if v < lo else 'YUKSEK')
    print(f'{key:22s} {f"{lo:g} - {hi:g} ({md:g})":>26s} {v:10.4g}  {tag:6s} {label}')
if 'json' in opt: json.dump(res, open(opt['json'], 'w'), indent=1)
