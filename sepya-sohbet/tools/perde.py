# perde.py — you recorded every line yourself, in one take: give each character its own voice by shifting the pitch per line.
#   python perde.py <in.wav> <words.json> <out.wav> '{"HOCA": -3, "CIRAK": 6}'
# words.json comes from kelime_saat.py on <in.wav> (it knows which line belongs to whom). Measured in the references:
# the mentor speaks at ~88 Hz (a deep voice), the young one at ~245 Hz; that is about 18 semitones apart.
# A typical male voice (~115 Hz) -> mentor -4 st, young one +8..+10 st; a female voice (~200 Hz) -> mentor -12 st, young one +3 st.
# The pitch is shifted with formants preserved for the mentor (natural) and shifted for the young one (smaller, cartoon-like).
import sys, json, subprocess
import numpy as np
src, wj, dst = sys.argv[1], sys.argv[2], sys.argv[3]
PERDE = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
SR = 48000
y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).copy()
lines = json.load(open(wj, encoding='utf-8'))['lines']
mentor = lines[-1]['spk']   # the sign-off line is the mentor's
PERDE = ({mentor: -4} | {s: 8 for s in dict.fromkeys(l['spk'] for l in lines) if s != mentor}) | PERDE
def shift(x, st, keep):
    if not st: return x
    out = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af',
                          f"rubberband=pitch={2 ** (st / 12):.4f}:formant={'preserved' if keep else 'shifted'}", '-f', 'f32le', '-'],
                         input=x.tobytes(), capture_output=True, check=True).stdout
    z = np.frombuffer(out, np.float32); return np.pad(z, (0, max(0, len(x) - len(z))))[:len(x)]
res = y.copy()
for i, l in enumerate(lines):
    a = int(max(0, l['start'] - .08) * SR)
    b = int(min(len(y) / SR, (lines[i + 1]['start'] - .02) if i + 1 < len(lines) else len(y) / SR) * SR)
    st = PERDE.get(l['spk'], 0)
    seg = shift(y[a:b], st, st < 0)
    f = min(int(.01 * SR), len(seg) // 2); r = np.ones(len(seg), np.float32); r[:f] = np.linspace(0, 1, f); r[-f:] = np.linspace(1, 0, f)
    res[a:b] = seg * r
    print(f"{l['spk']:>6} {st:+d} st  {l['start']:6.2f}-{l['end']:6.2f}  {l['text']}")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', dst], input=res.tobytes(), check=True)
print('->', dst, '(now run kelime_saat.py and zarf.py on it)')
