# tts.py — ElevenLabs (eleven_v4) voice for the Bogdanov short, with exact word times from the API's alignment.
#   ELEVENLABS_API_KEY=... python tts.py <out_dir> [speed=1.0] [stability=0.5]
# Numbers are spelled out for the TTS only; words.json keeps the SCRIPT's spelling (voice/script.txt).
import sys, os, json, base64, urllib.request, pathlib, subprocess
OUT = pathlib.Path(sys.argv[1]); speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
stab = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
KEY = os.environ['ELEVENLABS_API_KEY']
VOICE = '2Urh65iQwqZQ1NE6qPag'      # "YouTube Shorts": Turkish male documentary narrator (the account's own voice)
MODEL = 'eleven_v4'
SAY = {"1920'lerde": "Bin dokuz yüz yirmilerde", "1924'ten": "Bin dokuz yüz yirmi dörtten", "11": "on bir", "20": "yirmi",
       "1928": "Bin dokuz yüz yirmi sekiz", "12.": "on ikinci", "54": "elli dört"}
script = (pathlib.Path(__file__).parent.parent / 'voice' / 'script.txt').read_text(encoding='utf-8').split()
spoken = [SAY.get(w, w) for w in script]
text = ' '.join(spoken)
body = json.dumps({'text': text, 'model_id': MODEL, 'language_code': 'tr',
                   'voice_settings': {'stability': stab, 'similarity_boost': .8, 'style': .35, 'use_speaker_boost': True, 'speed': speed}}).encode()
req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128',
                             data=body, headers={'xi-api-key': KEY, 'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=300))
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'raw.mp3').write_bytes(base64.b64decode(r['audio_base64']))
al = r.get('normalized_alignment') if False else r['alignment']
chars, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
assert ''.join(chars) == text, 'alignment text differs'
# character spans of every spoken token, then of every script word
pos, spans = 0, []
for w in spoken:
    n = len(w.split()); toks = []
    for _ in range(n):
        while text[pos] == ' ': pos += 1
        a = pos
        while pos < len(text) and text[pos] != ' ': pos += 1
        toks.append((a, pos - 1))
    spans.append((toks[0][0], toks[-1][1]))
words = [{'word': w, 'start': round(st[a], 3), 'end': round(en[b], 3)} for w, (a, b) in zip(script, spans)]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(OUT / 'raw.mp3'), '-ar', '48000', '-ac', '1', str(OUT / 'raw.wav')], check=True)
json.dump({'words': words, 'duration': words[-1]['end']}, open(OUT / 'raw_words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
gaps = [(words[i]['word'], round(words[i + 1]['start'] - words[i]['end'], 2)) for i in range(len(words) - 1) if words[i + 1]['start'] - words[i]['end'] > .3]
print('words', len(words), 'end', words[-1]['end'], 's ->', round(len(words) / words[-1]['end'], 2), 'w/s | gaps>.3:', gaps)
