# metin.py — reads a dialogue script: one line per spoken line, "TAG: text". Shared by the other tools.
#   HOCA: Neden göndermiyorsun?
#   CIRAK: Doğru zamanı bekliyorum.
# Lines starting with # are comments; a line without "TAG:" continues the previous speaker.
import re

def read_script(path):
    lines, last = [], None
    for raw in open(path, encoding='utf-8'):
        s = raw.strip()
        if not s or s.startswith('#'): continue
        m = re.match(r'^([A-ZÇĞİÖŞÜa-zçğıöşü0-9_]+)\s*:\s*(.+)$', s)
        if m: last = m.group(1).upper().replace('İ', 'I').replace('Ç', 'C').replace('Ğ', 'G').replace('Ö', 'O').replace('Ş', 'S').replace('Ü', 'U'); text = m.group(2)
        elif last: text = s
        else: raise SystemExit(f'satırda konuşmacı yok / no speaker tag: {s}')
        lines.append({'spk': last, 'text': text.strip()})
    return lines

def norm(w):
    return re.sub(r"[^\wçğıöşüâîû']", '', w.replace('İ', 'i').replace('I', 'ı').lower())
