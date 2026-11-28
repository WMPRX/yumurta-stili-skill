# elevenlabs_ses.py — the voice from ElevenLabs: every script line in its character's voice, joined with the measured pauses.
#   python tools/elevenlabs_ses.py <script.txt> <sesler.json> <voice.wav> [--model=eleven_v4] [--yeniden]
#
# sesler.json (next to script.txt) gives each speaker tag a voice and an audio tag that sets the delivery, e.g.
#   { "HOCA":  { "voice_id": "Razqs3wH10dOkbWg5isY", "etiket": "[speaking very slowly, with long pauses]" },
#     "CIRAK": { "voice_id": "YSY5NSUfipZgHlzUBjKT", "etiket": "[nervously, in a higher voice]" } }
# Optional "perde": semitones of pitch shift after generation, formants kept (the mentor of the references sits at ~88 Hz).
# A line can carry its own tag in the script ("HOCA: [whispers] ..."); it replaces the speaker's default.
#
# The API key is NOT read from a file or a variable here: in a Claude cloud session the network proxy adds it to every request to
# api.elevenlabs.io. Elsewhere set ELEVENLABS_API_KEY.
# Every line is cached in voice/el_cache/ by (model, voice, tag, text): re-running spends credits only on lines that changed.
# --yeniden ignores the cache.
# --denetle[=2]: Whisper listens to every line; a misread word ("birbirimizin" for "birbirinizin", "yürüyen az" for "yürüyemez")
#   regenerates that line, up to 2 more times. Merged forms ("bitirmekse" for "bitirmek ise") pass.
#
# Measured on eleven_v4 (Nov 2026): `voice_settings.speed` has no effect; the pace comes from the audio tag. Plain text runs at
# 5.2-6.1 syllables/s; "[speaking very slowly, with long pauses]" gives ~4.0 (the references: 3.8-4.6) but lifts a deep voice
# to ~114 Hz, hence "perde": -3. "[nervously, in a higher voice]" puts the designed young voice at ~270 Hz (references ~245).
import sys, os, json, hashlib, pathlib, subprocess, urllib.request, urllib.error, time, re
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from metin import read_script, norm
import difflib

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opt = dict((a[2:].split('=', 1) + [''])[:2] for a in sys.argv[1:] if a.startswith('--'))
script, voices_path, out = args[0], args[1], args[2]
MODEL = opt.get('model', 'eleven_v4')
SR = 44100
V = json.load(open(voices_path, encoding='utf-8'))
L = read_script(script)
cache = pathlib.Path(script).parent / 'el_cache'; cache.mkdir(exist_ok=True)
missing = sorted({l['spk'] for l in L} - set(V))
if missing: raise SystemExit(f'sesler.json: no voice for {missing}')

def request(text, voice):
    body = json.dumps({'text': text, 'model_id': MODEL, 'language_code': 'tr'}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128', data=body, method='POST',
                                 headers={'Content-Type': 'application/json', 'xi-api-key': os.environ.get('ELEVENLABS_API_KEY', 'proxy-injected')})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=180) as r: return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode('utf-8', 'replace')
            if e.code == 429 and attempt < 5: time.sleep(2 + attempt * 3); continue       # concurrency / rate limit
            raise SystemExit(f'ElevenLabs {e.code}: {msg[:400]}')

def line_audio(i):
    l = L[i]; v = V[l['spk']]
    text = l['text'].strip()
    tag = '' if text.startswith('[') else (v.get('etiket', '') + ' ').lstrip()
    full = tag + text
    key = hashlib.sha1(f"{MODEL}|{v['voice_id']}|{full}".encode('utf-8')).hexdigest()[:16]
    f = cache / f'{i:02d}_{l["spk"]}_{key}.mp3'
    if not f.exists() or 'yeniden' in opt: f.write_bytes(request(full, v['voice_id']))
    # decode, trim leading / trailing silence
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-af',
        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse',
        '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32).copy()
    st = float(v.get('perde', 0))                         # optional pitch shift in semitones, formants kept (rubberband)
    if st:
        x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af',
            f'rubberband=pitch={2 ** (st / 12):.5f}:formant=preserved', '-f', 'f32le', '-'], input=x.tobytes(), capture_output=True, check=True).stdout, np.float32).copy()
    return x, f.name

def misread(text, mp3):
    """script words Whisper did not hear (merged / split forms that read the same are accepted)"""
    y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(mp3), '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
    heard = ' '.join(s.text for s in WHISPER.transcribe(y, language='tr', beam_size=5, temperature=0)[0])
    A = [norm(w) for w in re.sub(r'\[[^\]]*\]', '', text).split() if norm(w)]; B = [norm(w) for w in heard.split() if norm(w)]
    bad = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=A, b=B, autojunk=False).get_opcodes():
        if tag == 'equal': continue
        a, b = ''.join(A[i1:i2]), ''.join(B[j1:j2])
        if (i2 - i1) != (j2 - j1) and a and b and difflib.SequenceMatcher(a=a, b=b).ratio() >= .9: continue
        if a: bad.append(f"{' '.join(A[i1:i2])} -> {' '.join(B[j1:j2]) or '(yok)'}")
    return bad

with ThreadPoolExecutor(4) as ex:                       # the account allows 5 requests at once; keep one free
    parts = list(ex.map(line_audio, range(len(L))))

if 'denetle' in opt:
    from faster_whisper import WhisperModel
    WHISPER = WhisperModel('medium', device='cpu', compute_type='int8')
    tries = int(opt['denetle'] or 2)
    for i, l in enumerate(L):
        f = cache / parts[i][1]
        for k in range(tries + 1):
            bad = misread(l['text'], f)
            if not bad: break
            print(f"  satır {i} ({l['spk']}): {', '.join(bad)}" + (' -> yeniden' if k < tries else ' -> KALDI, elle dinleyin'))
            if k < tries:
                v = V[l['spk']]; t = l['text'].strip()
                f.write_bytes(request(t if t.startswith('[') else (v.get('etiket', '') + ' ' + t).strip(), v['voice_id']))
        parts[i] = line_audio(i)

# same loudness for every line (RMS of the voiced part), so the two characters sit level
def rms(x):
    if not len(x): return 1e-6
    fr = x[:len(x) // 441 * 441].reshape(-1, 441); e = np.sqrt((fr ** 2).mean(1)); e = e[e > e.max() * .1]
    return float(np.sqrt((e ** 2).mean())) if len(e) else 1e-6
ref = np.median([rms(x) for x, _ in parts])
pieces, prev = [np.zeros(int(SR * .25), np.float32)], None
for l, (x, name) in zip(L, parts):
    if prev is not None: pieces.append(np.zeros(int(SR * (.7 if l['spk'] != prev else .45)), np.float32))
    pieces.append(x * (ref / rms(x))); prev = l['spk']
    print(f"{l['spk']:>6} {len(x) / SR:5.2f} s  {name}  {l['text'][:60]}")
y = np.concatenate(pieces + [np.zeros(int(SR * .4), np.float32)])
y = y / max(1e-6, np.abs(y).max()) * .9
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', out], input=y.astype(np.float32).tobytes(), check=True)
print(f'-> {out}  {len(y) / SR:.1f} s   (now: kelime_saat.py and zarf.py)')
