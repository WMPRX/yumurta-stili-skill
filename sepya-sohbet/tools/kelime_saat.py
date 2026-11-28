# kelime_saat.py — word timings for a voice file, aligned back onto the exact script words, with the speaker of every word.
#   python kelime_saat.py <voice.wav> <script.txt> <words.json> [model=medium]
# Whisper (faster-whisper) hears the words and may misspell them; we keep the SCRIPT's spelling and take only the times.
# Output: { words: [{word, start, end, spk, line}], lines: [{spk, text, start, end}], duration }
import sys, json, difflib, subprocess, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from metin import read_script, norm
from faster_whisper import WhisperModel

wav, script, out = sys.argv[1], sys.argv[2], sys.argv[3]
model = sys.argv[4] if len(sys.argv) > 4 else 'medium'
y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', wav, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
m = WhisperModel(model, device='cpu', compute_type='int8')
segs, _ = m.transcribe(y, language='tr', word_timestamps=True, beam_size=5)
heard = [{'w': w.word.strip(), 's': w.start, 'e': w.end} for s in segs for w in s.words if w.word.strip()]

L = read_script(script)
words = [{'word': w, 'spk': l['spk'], 'line': i} for i, l in enumerate(L) for w in l['text'].split()]
A, B = [norm(w['word']) for w in words], [norm(h['w']) for h in heard]
sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
times = [None] * len(words)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        for k in range(i2 - i1): times[i1 + k] = (heard[j1 + k]['s'], heard[j1 + k]['e'])
    elif j2 > j1 and i2 > i1:
        s, e = heard[j1]['s'], heard[j2 - 1]['e']
        n = i2 - i1
        for k in range(n): times[i1 + k] = (s + (e - s) * k / n, s + (e - s) * (k + 1) / n)
for i, t in enumerate(times):
    if t is None:
        prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
        nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), prev + .3)
        times[i] = (prev, max(prev + .05, nxt))
for w, (s, e) in zip(words, times): w['start'], w['end'] = round(float(s), 3), round(float(e), 3)
lines = []
for i, l in enumerate(L):
    ws = [w for w in words if w['line'] == i]
    lines.append({'spk': l['spk'], 'text': l['text'], 'start': ws[0]['start'], 'end': ws[-1]['end']})
dur = round(len(y) / 16000, 3)
json.dump({'words': words, 'lines': lines, 'duration': dur}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
same = sum(i2 - i1 for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag == 'equal')
print('heard exactly:', same, '/', len(words), [(' '.join(A[i1:i2]), ' '.join(B[j1:j2])) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != 'equal'])
talk = sum(l['end'] - l['start'] for l in lines)
syl = sum(sum(c in 'aeıioöuüâî' for c in norm(w['word'])) for w in words)
print(f"OK {len(words)} words, {len(lines)} lines, {dur} s | {len(words) / (words[-1]['end'] - words[0]['start']):.2f} words/s, "
      f"{syl / talk:.2f} syllables/s while talking (target 3.8-4.6)")
