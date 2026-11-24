# mix.py (Bogdanov) — this story's own score + effects, synthesized with numpy, mixed under the voice.
#   python stories/bogdanov/audio/mix.py stories/bogdanov
# Same levels as engine/audio/mix.py (music ~17 dB under the voice and ducked, effects ~11 dB under, -14 LUFS),
# but a 1920s-Moscow colour instead of the sample's makam: a music box in D minor over a low string drone and a
# heartbeat; after the cut to 1928 the box falls silent, the drone darkens, the heartbeat slows and stops at the end.
import sys, json, subprocess, pathlib
import numpy as np

SR = 48000
story = pathlib.Path(sys.argv[1])
cues = json.load(open(story / 'audio' / 'cues.json', encoding='utf-8'))
DUR = cues['DUR']; N = int(DUR * SR)
rng = np.random.default_rng(11)
C = cues['cues']
def first(ty, default):
    return next((c['t'] for c in C if c['type'] == ty), default)

def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def save(p, x):
    x = np.clip(x, -1, 1); st = np.stack([x, x], 1)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', str(p)], input=st.astype(np.float32).tobytes(), check=True)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4); return np.fft.irfft(X * m, len(x))
def env_ad(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))
def put(buf, t, x, g=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if 0 <= i < len(buf) and j > i: buf[i:j] += x[:j - i] * g
def noise(d): return rng.standard_normal(max(1, int(round(d * SR))))
def tone(f, d, dec, parts=((1, 1), (2.76, .35), (5.4, .12))):      # a struck metal comb tooth (music box)
    n = int(d * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * t) * a * np.exp(-t / (dec / (1 + k * .3))) for k, a in parts) * np.minimum(1, t / .002)
def pad(f, d, amp=.07, lo=40, hi=700):
    n = int(d * SR); t = np.arange(n) / SR
    x = sum(((t * f * dd) % 1 * 2 - 1) for dd in (1, 1.003, .996, 1.5))
    x = band(x, lo, hi) * amp; fade = np.minimum(1, np.minimum(t / 1.0, (d - t) / 1.0)); return x * fade
def beat():
    n = int(.35 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (55 + 40 * np.exp(-t * 25)) * t) * env_ad(n, .002, .09)

HZ = {'A3': 220.0, 'Bb3': 233.1, 'C4': 261.6, 'C#4': 277.2, 'D4': 293.7, 'E4': 329.6, 'F4': 349.2, 'G4': 392.0, 'A4': 440.0, 'Bb4': 466.2, 'C5': 523.3, 'D5': 587.3, 'E5': 659.3, 'F5': 698.5, 'A5': 880.0,
      'D2': 73.4, 'A1': 55.0, 'Bb1': 58.3, 'F2': 87.3, 'C#2': 69.3}
t_dark = first('thunder', DUR * .56)
t_end = next((c['t'] for c in C if c['type'] == 'click'), DUR - 1.2)
music = np.zeros(N)
# the music box: a slow waltz-like figure in D minor (3/4, 84 bpm)
bpm = 84; b = 60 / bpm
melody = ['D5', 'A4', 'F4', 'A4', 'E5', 'A4', 'C#4', 'A4', 'D5', 'A4', 'F4', 'A4', 'F5', 'E5', 'D5', 'C5', 'Bb4', 'F4', 'D4', 'F4', 'A4', 'E4', 'C#4', 'E4']
t = 0.0; k = 0
while t < t_dark - .2:
    put(music, t, tone(HZ[melody[k % len(melody)]], 1.6, .55), .22 if k % 3 == 0 else .14); k += 1
    t += b
# bass drone and the heartbeat
put(music, 0, pad(HZ['D2'], t_dark + .4, .06))
put(music, t_dark, pad(HZ['Bb1'], t_end - t_dark + .5, .085, 30, 500))
put(music, t_dark, pad(HZ['C#2'] * 2, t_end - t_dark + .5, .025, 60, 900))       # a sour second voice after 1928
t = .3; period = 60 / 66
while t < t_end:
    dark = t > t_dark
    g = .55 if not dark else .7
    put(music, t, beat(), g); put(music, t + .26, beat(), g * .6)                       # lub-dub
    if dark and t > first('boom', t_end) - 1e9: period = min(1.35, period * 1.012) if t > t_dark + 8 else period
    t += period
# the end: one low struck note under the last words
put(music, t_end + .1, tone(HZ['D4'] / 2, 3.0, 1.2), .3); put(music, t_end + .1, tone(HZ['A3'] / 2, 3.0, 1.2), .18)

# ------------------------------------------------------------------ effects
sfx = np.zeros(N)
for c in C:
    t0, ty, d = c['t'], c['type'], c.get('dur', 1.0)
    if ty == 'whoosh':
        x = noise(.45); tt = np.arange(len(x)) / SR; put(sfx, t0, band(x, 300, 3500) * np.sin(np.pi * tt / .45) ** 2, .35)
    elif ty == 'tick':
        rate = 2.0 * c.get('fast', 1) * 3
        for i in range(int(d * rate)):
            nb = int(.03 * SR); x = band(noise(.03), 2500, 7000) * env_ad(nb, .0003, .006) + np.sin(2 * np.pi * 1900 * np.arange(nb) / SR) * env_ad(nb, .0005, .01) * .3
            put(sfx, t0 + i / rate, x, .5 if i % 2 else .35)
    elif ty == 'stop':
        nb = int(.5 * SR); tt = np.arange(nb) / SR
        x = band(noise(.5), 1500, 7000) * env_ad(nb, .0004, .012) + np.sin(2 * np.pi * 140 * tt) * env_ad(nb, .001, .05) * .9 + np.sin(2 * np.pi * 1320 * tt) * env_ad(nb, .001, .12) * .4
        put(sfx, t0, x, .55)
    elif ty == 'pump':                     # blood in the glass line: a soft squelchy pulse
        for i in range(int(d * 1.6)):
            nb = int(.25 * SR); tt = np.arange(nb) / SR; x = band(noise(.25), 120, 700) * np.sin(np.pi * tt / .25) ** 2
            put(sfx, t0 + i / 1.6, x, .22)
    elif ty == 'room':                     # the room tone: a faint hum of the bulb
        n = int(d * SR); tt = np.arange(n) / SR
        x = (np.sin(2 * np.pi * 100 * tt) * .3 + band(noise(d), 60, 400)) * np.minimum(1, np.minimum(tt / .4, (d - tt) / .4)); put(sfx, t0, x, .035)
    elif ty == 'wind':
        x = band(noise(d), 200, 1400); tt = np.arange(len(x)) / SR
        x *= (.55 + .45 * np.sin(2 * np.pi * .5 * tt)) * np.minimum(1, np.minimum(tt / .5, (d - tt) / .5)); put(sfx, t0, x, .14)
    elif ty == 'bulbs':                    # the sign's bulbs switch on: a row of clicks and a warm hum
        for i in range(8): put(sfx, t0 + i * .035, band(noise(.02), 2000, 8000) * env_ad(int(.02 * SR), .0002, .004), .4)
        n = int(1.2 * SR); tt = np.arange(n) / SR; put(sfx, t0 + .1, np.sin(2 * np.pi * 120 * tt) * env_ad(n, .05, .5), .12)
    elif ty == 'flip':
        for i in range(5): put(sfx, t0 + i * d / 5, band(noise(.08), 800, 5000) * np.sin(np.pi * np.arange(int(.08 * SR)) / int(.08 * SR)), .35)
    elif ty == 'thunder':
        nb = int(2.5 * SR); tt = np.arange(nb) / SR
        x = band(noise(2.5), 30, 300) * env_ad(nb, .05, .7) + band(noise(2.5), 300, 2000) * env_ad(nb, .002, .08) * .5; put(sfx, t0, x, .7)
    elif ty == 'chalk':
        n = c.get('n', 1)
        for i in range(n):
            nb = int(.08 * SR); x = band(noise(.08), 2500, 9000) * np.sin(np.pi * np.arange(nb) / nb) ** .5; put(sfx, t0 + i * d / max(1, n), x, .25)
    elif ty == 'boom':
        nb = int(1.2 * SR); tt = np.arange(nb) / SR
        x = np.sin(2 * np.pi * (48 + 30 * np.exp(-tt * 8)) * tt) * env_ad(nb, .003, .35) + band(noise(1.2), 60, 400) * env_ad(nb, .002, .12) * .4; put(sfx, t0, x, .6)
    elif ty == 'clink':
        nb = int(.6 * SR); tt = np.arange(nb) / SR
        x = sum(np.sin(2 * np.pi * f * tt) * env_ad(nb, .0005, dc) * a for f, dc, a in [(2400, .08, .6), (3900, .06, .4), (5200, .04, .3)])
        put(sfx, t0 + .5, x, .35)        # the glasses land
    elif ty == 'sparkle':
        nb = int(1.2 * SR); tt = np.arange(nb) / SR
        x = sum(np.sin(2 * np.pi * f * tt) * env_ad(nb, .005 + i * .05, .4) for i, f in enumerate([1760, 2217, 2637, 3520])) / 4; put(sfx, t0, x, .25)
    elif ty == 'papers':
        for i in range(10):
            nb = int(.12 * SR); x = band(noise(.12), 900, 6000) * np.sin(np.pi * np.arange(nb) / nb); put(sfx, t0 + i * d / 10 + rng.uniform(0, .05), x, .3)
    elif ty == 'buzz':
        n = int(d * SR); tt = np.arange(n) / SR
        f = 560 + 60 * np.sin(2 * np.pi * 3 * tt); ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sign(np.sin(ph)) * .3 * np.minimum(1, np.minimum(tt / .1, (d - tt) / .1)) * (.6 + .4 * np.sin(2 * np.pi * 1.5 * tt)); put(sfx, t0, band(x, 300, 4000), .12)
    elif ty == 'cough':
        for i, g in enumerate([1, .8, .6]):
            nb = int(.18 * SR); x = band(noise(.18), 200, 2500) * env_ad(nb, .005, .06); put(sfx, t0 + i * .22, x, .45 * g)
    elif ty == 'blood':                    # inside the tube: a muffled rushing flow
        x = band(noise(d), 40, 500); tt = np.arange(len(x)) / SR
        x *= (.6 + .4 * np.sin(2 * np.pi * 1.1 * tt)) * np.minimum(1, np.minimum(tt / .3, (d - tt) / .3)); put(sfx, t0, x, .3)
    elif ty == 'pen':
        n = int(d * SR); x = np.zeros(n)
        for _ in range(int(d * 7)):
            ts = rng.uniform(0, max(.01, d - .2)); ns = int(rng.uniform(.08, .2) * SR)
            s = band(noise(ns / SR), 2500, 9000) * np.sin(np.pi * np.arange(ns) / ns) ** 2; j = int(ts * SR); x[j:j + ns] += s[:max(0, min(ns, n - j))]
        put(sfx, t0, x, .12)
    elif ty == 'click':
        put(sfx, t0, band(noise(.03), 1500, 7000) * env_ad(int(.03 * SR), .0003, .006), .6)

# ------------------------------------------------------------------ mix
voice = load(story / 'voice' / 'voice.wav'); voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
win = int(.05 * SR); ve = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode='same'))
active = np.convolve((ve > .02).astype(float), np.ones(int(.25 * SR)) / int(.25 * SR), mode='same')
duck = 1 - .45 * np.clip(active, 0, 1)
def rms(x): return np.sqrt(np.mean(x[np.abs(x) > 1e-5] ** 2)) if np.any(np.abs(x) > 1e-5) else 1
vr = rms(voice)
music *= (vr / rms(music)) * 10 ** (-17 / 20)
sfx *= (vr / max(rms(sfx), 1e-6)) * 10 ** (-16 / 20)
mix = voice + music * duck + sfx
fade = np.ones(N); fl = int(.4 * SR); fade[-fl:] = np.linspace(1, 0, fl); mix *= fade
out = story / 'audio'
save(out / 'music.wav', music * duck); save(out / 'sfx.wav', sfx)
save(out / 'premix.wav', mix / max(1e-6, np.abs(mix).max()) * .7)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out / 'premix.wav'), '-af', 'loudnorm=I=-14:TP=-2.3:LRA=11,aresample=48000', str(out / 'mix.wav')], check=True)
print('OK mix.wav', round(DUR, 2), 's')
