# mix.py — original score + ambience, synthesized with numpy, mixed under the dialogue (analiz/ses.md).
#   python audio/mix.py stories/<story> [--muzik=my_licensed_track.mp3]
# Reads <story>/voice/voice.wav and <story>/audio/cues.json (written by `node render.mjs <story> --cues`),
# writes <story>/audio/mix.wav (+ muzik.wav / ambiyans.wav stems).
# Measured in the references: integrated loudness -14.1 LUFS in all six; a continuous, tonal, soft music bed
# (spectral flatness < .01, mostly 250-2000 Hz) that sits ~6-10 dB under the voice in the pauses; no hard silences.
import sys, json, subprocess, pathlib
import numpy as np

SR = 48000
args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--'))
story = pathlib.Path(args[0])
cues = json.load(open(story / 'audio' / 'cues.json', encoding='utf-8'))
DUR = cues['DUR']; N = int(DUR * SR)
rng = np.random.default_rng(5)

def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def save(p, x):
    st = np.stack([x, x], 1) if x.ndim == 1 else x
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', str(p)], input=st.astype(np.float32).tobytes(), check=True)
def fit(x, n): return np.pad(x, (0, max(0, n - len(x))))[:n]
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4), len(x))
def reverb(x, t60=2.4, wet=.35):
    n = int(t60 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-6.9 * t / t60); ir = band(ir, 200, 5000); ir /= np.sqrt((ir ** 2).sum())
    L = len(x) + n; F = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
    return x * (1 - wet) + y * wet
def rms(x): return float(np.sqrt(np.mean(x ** 2) + 1e-12))
def put(buf, t, x, gain=1.0):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if 0 <= i < len(buf): buf[i:j] += x[:j - i] * gain

# ------------------------------------------------------------------ piano (additive, slightly inharmonic, soft hammer)
def piano(freq, dur=3.5, vel=.6):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for k in range(1, 8):
        fk = freq * k * np.sqrt(1 + .0004 * k * k)
        if fk > 9000: break
        x += np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * (vel ** (k * .35)) / k ** 1.3 * np.exp(-t * (.6 + .55 * k))
    x *= np.minimum(1, t / .006)
    x[:int(.01 * SR)] += band(rng.standard_normal(int(.01 * SR)), 800, 4000) * .02
    return x * vel
def pad(freq, dur, amp=.05):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * freq * d * t) for d in (1, 1.003, .997, 2.001)) / 4
    return x * amp * np.minimum(1, np.minimum(t / 1.5, (dur - t) / 1.5))

NOTE = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'])}
def hz(name, octv): return NOTE[name] * 2 ** (octv - 4)
key = cues.get('music', {}).get('key', 'Am'); bpm = cues.get('music', {}).get('bpm', 66)
root = key.rstrip('m')
names = list(NOTE)
r = names.index(root)
def deg(semi): return names[(r + semi) % 12]
# i - VI - III - VII (natural minor): the melancholic loop of this genre
PROG = [[0, 3, 7], [8, 12, 15], [3, 7, 10], [10, 14, 17]]
beat = 60 / bpm; bar = beat * 4

def score():
    mus = np.zeros(N + SR * 4)
    t, b = 0.0, 0
    while t < DUR:
        ch = PROG[b % 4]
        base = hz(deg(ch[0]), 2 if ch[0] < 6 else 2)
        put(mus, t, piano(base * (1 if ch[0] < 6 else .5) * 2, 4.5, .55), .9)
        put(mus, t, pad(hz(deg(ch[0]), 3), bar + 1.5, .035))
        arp = [ch[0], ch[1], ch[2], ch[1] + 12 if ch[1] + 12 < 24 else ch[1]]
        for i, semi in enumerate(arp):
            nm = deg(semi); oc = 4 + (r + semi) // 12
            put(mus, t + i * beat + rng.uniform(-.015, .015), piano(hz(nm, oc - (1 if semi > 14 else 0)), 3.2, .38 + .08 * (i == 0)), .55)
        if b % 2 == 1:                                    # a sparse top note every other bar
            put(mus, t + beat * 2.5, piano(hz(deg(ch[2] + 12), 5), 3, .3), .35)
        t += bar; b += 1
    return reverb(mus[:N], 2.6, .42)

def ambience():
    amb = np.zeros(N)
    for s in cues['shots']:
        a, b = int(s['a'] * SR), int(s['b'] * SR); n = b - a
        if n <= 0: continue
        noise = rng.standard_normal(n)
        if s.get('set') == 'sokak':                        # winter wind
            lfo = .6 + .4 * np.sin(np.arange(n) / SR * .7 + rng.uniform(0, 6))
            x = band(noise, 150, 900) * lfo * .05
        elif s.get('set') == 'oda' or s.get('kind') == 'nesne':
            x = band(noise, 80, 400) * .02                 # room tone
        else:                                              # café: room tone + a far murmur
            x = band(noise, 100, 600) * .025 + band(rng.standard_normal(n), 300, 1200) * .008
        f = min(int(.05 * SR), n // 2); e = np.ones(n); e[:f] = np.linspace(0, 1, f); e[-f:] = np.linspace(1, 0, f)
        amb[a:b] += x * e
        for t0 in s.get('flash', []):                      # thunder after a flash
            m = int(3 * SR); tt = np.arange(m) / SR
            put(amb, t0 + .25, band(rng.standard_normal(m), 30, 200) * np.exp(-tt * 1.4) * np.minimum(1, tt / .2) * .5)
    return amb

voice = fit(load(story / 'voice' / 'voice.wav'), N)
voice = reverb(voice, .5, .08)                           # a little room, as in the references
mus = fit(load(opt['muzik']), N) if 'muzik' in opt else score()
# duck the music 3 dB while someone speaks (lines from cues), with 0.25 s ramps
env = np.ones(N)
for l in cues['lines']:
    a, b = int((l['start'] - .1) * SR), int((l['end'] + .15) * SR); env[max(0, a):min(N, b)] = .7
k = int(.25 * SR); env = np.convolve(env, np.ones(k) / k, mode='same')
# end card: the music rises a little and a low note lands when the title appears; everything fades with the picture
tE = cues['end']; t = np.arange(N) / SR
swell = 1 + .35 * np.clip((t - tE) / 3, 0, 1)
fade = np.clip((DUR - .5 - t) / 1.3, 0, 1)
put(mus, tE + 4.2, piano(hz(deg(0), 2), 5, .7) + piano(hz(deg(7), 3), 5, .4), 1.0)
amb = ambience()
v_rms = rms(voice[voice != 0]) if (voice != 0).any() else .1
mus *= v_rms * 10 ** (-7.0 / 20) / max(rms(mus), 1e-6)      # bed 7 dB under the voice (RMS); with ducking the pauses measure ~6-8 dB under
amb *= v_rms * 10 ** (-24 / 20) / max(rms(amb), 1e-6)
mix = (voice + mus * env * swell + amb) * fade
save(story / 'audio' / 'muzik.wav', mus * env * swell * fade); save(story / 'audio' / 'ambiyans.wav', amb * fade)
tmp = story / 'audio' / '_raw.wav'; save(tmp, mix / max(1e-6, np.abs(mix).max()) * .8)
# two-pass loudnorm to -14 LUFS (one pass lands ~0.7 LU low on speech this sparse)
meas = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(tmp), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(tmp), '-af', ln, '-ar', str(SR), str(story / 'audio' / 'mix.wav')], check=True)
tmp.unlink()
print('->', story / 'audio' / 'mix.wav', f'{DUR:.1f} s')
