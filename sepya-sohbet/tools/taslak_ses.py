# taslak_ses.py — a DRAFT voice from the script with a local TTS (Piper), so the shots can be timed before you record.
#   python taslak_ses.py <script.txt> <out.wav> [--model=tr_TR-dfki-medium.onnx] [--hiz=1.0]
# Every line is spoken alone, pitch-shifted per speaker (PERDE below), then joined with the measured pauses:
# 0.7 s when the speaker changes, 0.45 s between two lines of the same speaker (analiz/metin.md).
# Replace it with your own recording later (see perde.py) and re-run kelime_saat.py + zarf.py.
import sys, subprocess, json, wave, pathlib, tempfile
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from metin import read_script

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--'))
script, out = args[0], args[1]
model = opt.get('model', str(pathlib.Path(__file__).parent / 'tr_TR-dfki-medium.onnx'))
hiz = float(opt.get('hiz', 1.0))
# semitones per speaker; the speaker of the LAST line is the mentor (the sign-off is always the mentor's), the other one the young one
PERDE = json.loads(opt.get('perde', '{}'))
SR = 24000
L = read_script(script)
mentor = L[-1]['spk']; others = [s for s in dict.fromkeys(l['spk'] for l in L) if s != mentor]
default = {mentor: -2.5} | {o: 9.0 for o in others}
PERDE = default | PERDE
tmp = pathlib.Path(tempfile.mkdtemp())
pieces, prev = [], None
for i, l in enumerate(L):
    raw = tmp / f'{i}.wav'
    subprocess.run([sys.executable, '-m', 'piper', '-m', model, '-f', str(raw), '--length-scale', str(1.12 / hiz), '--sentence-silence', '0.35'],
                   input=l['text'].encode('utf-8'), check=True, capture_output=True)
    st = PERDE.get(l['spk'], 0)
    af = f"rubberband=pitch={2 ** (st / 12):.4f}:formant=shifted" if st else 'anull'
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(raw), '-af', af + ',silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse',
                                      '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
    if prev is not None: pieces.append(np.zeros(int(SR * (.7 if l['spk'] != prev else .45)), np.float32))
    pieces.append(x); prev = l['spk']
    print(f"{l['spk']:>6} {st:+.1f} st  {len(x) / SR:5.2f} s  {l['text']}")
y = np.concatenate([np.zeros(int(SR * .25), np.float32)] + pieces + [np.zeros(int(SR * .4), np.float32)])
y = y / max(1e-6, np.abs(y).max()) * .9
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', out], input=y.tobytes(), check=True)
print(f'-> {out}  {len(y) / SR:.1f} s')
