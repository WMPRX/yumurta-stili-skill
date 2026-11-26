#!/usr/bin/env python3
"""Bir klibi ya da kurgulanmış videoyu referansın renk ve ton dağılımına yaklaştırır.

    python tools/renk_esle.py girdi.mp4 cikti.mp4 [--guc 0.6] [--ton 0.5] [--siyah 1]

Ne yapar (Lab uzayında, kare kare, plan içinde yumuşatılmış istatistiklerle):
  1. Ton: L'nin 1/50/99 yüzdeliklerini referansa doğru parça parça doğrusal eşler (--ton gücüyle).
  2. Bölünmüş ton: gölge / orta / ışık bantlarının a-b ortalamalarını referansa çeker
     (gölgeler mor-erik, ortalar okra, ışıklar teal; analiz/veri/renk_hedef.json).
  3. Doygunluk: ortalama Lab kromasını 24.5'e doğru ölçekler (--guc ile).
  4. Kontrast: RMS kontrastı 19.7'ye doğru ölçekler (--ton ile).
  5. Saf siyahı kaldırır: en koyu değerleri mor-siyaha (#221a1f) doğru yükseltir (--siyah 1).
Güç 0 = dokunma, 1 = tam eşle. Yapay zekâ ile üretilmiş klipler için 0.5-0.7 iyi çalışır;
1'e yaklaştıkça sahneler birbirine benzer ve renkler kirlenir.
Ses akışı olduğu gibi kopyalanır.
"""
import argparse, json, os, subprocess
import numpy as np
import cv2

here = os.path.dirname(os.path.abspath(__file__))
REF = json.load(open(os.path.join(here, "..", "analiz", "veri", "renk_hedef.json")))
# kare başına ortalama yüzdelikler (olc.py ile aynı tanım)
T_P1, T_P50, T_P99 = 8.6, 61.2, 89.0
T_RMS, T_KROMA = 19.7, 24.5
BANDS = [("golge", 0, 30), ("orta", 30, 70), ("isik", 70, 101)]
PLUM = np.array([22, 15, 19], np.float32)


def probe(path):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", path],
                                  capture_output=True, text=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    has_a = any(s["codec_type"] == "audio" for s in j["streams"])
    return int(v["width"]), int(v["height"]), v["r_frame_rate"], has_a


def stats(lab):
    """lab: float32 Lab (L 0..100, a/b işaretli)."""
    s = lab[::4, ::4, 0].ravel(); a = lab[::4, ::4, 1].ravel(); b = lab[::4, ::4, 2].ravel()
    out = dict(p=np.percentile(s, [1, 50, 99]), rms=np.array([s.std()]), kroma=np.array([np.hypot(a, b).mean()]))
    for n, lo, hi in BANDS:
        m = (s >= lo) & (s < hi)
        out[n] = np.array([a[m].mean(), b[m].mean()]) if m.sum() > 50 else np.array([np.nan, np.nan])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("girdi"); ap.add_argument("cikti")
    ap.add_argument("--guc", type=float, default=0.6, help="bölünmüş ton (renk) gücü 0..1")
    ap.add_argument("--ton", type=float, default=0.6, help="parlaklık eşleme gücü 0..1")
    ap.add_argument("--siyah", type=float, default=1.0, help="saf siyahı mor-siyaha kaldırma 0..1")
    ap.add_argument("--crf", type=int, default=16)
    a = ap.parse_args()
    W, H, fr, has_a = probe(a.girdi)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.girdi, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc_cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", fr, "-i", "-"]
    if has_a:
        enc_cmd += ["-i", a.girdi, "-map", "0:v", "-map", "1:a", "-c:a", "copy"]
    enc_cmd += ["-c:v", "libx264", "-crf", str(a.crf), "-preset", "medium", "-pix_fmt", "yuv420p", a.cikti]
    enc = subprocess.Popen(enc_cmd, stdin=subprocess.PIPE)
    n = W * H * 3
    ema = None; prev_small = None
    tgt = {k: np.array([REF["bantlar"][k]["a"], REF["bantlar"][k]["b"]]) for k, _, _ in BANDS}
    while True:
        buf = dec.stdout.read(n)
        if len(buf) < n:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        lab = cv2.cvtColor(f.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
        st = stats(lab)
        small = cv2.resize(f, (64, 36)).astype(np.float32)
        new_shot = prev_small is None or np.abs(small - prev_small).mean() > 28
        prev_small = small
        if new_shot or ema is None:
            ema = st
        else:
            k = 0.08
            ema = {key: (np.where(np.isnan(st[key]), ema[key], (1 - k) * ema[key] + k * np.nan_to_num(st[key], nan=0)))
                   for key in st}
        L = lab[..., 0]
        # 1) ton eşleme
        p1, p50, p99 = ema["p"]
        xs = [0, p1, p50, p99, 100]
        ys_t = [0, T_P1, T_P50, T_P99, 100]
        ys = [x + a.ton * (y - x) for x, y in zip(xs, ys_t)]
        if all(np.diff(xs) > 0):
            L2 = np.interp(L, xs, ys).astype(np.float32)
        else:
            L2 = L
        # kontrast: RMS'i hedefe (19.7) doğru, medyan etrafında ölçekle
        c = (T_RMS / max(float(ema["rms"][0]), 1)) ** a.ton
        c = float(np.clip(c, 0.75, 1.25))
        med = float(np.interp(p50, xs, ys))
        L2 = np.clip(med + (L2 - med) * c, 0, 100)
        # 2) bölünmüş ton: her bant için kaydırma, L'ye göre yumuşak ağırlıkla
        A = lab[..., 1]; B = lab[..., 2]
        wsh = np.clip((35 - L2) / 20, 0, 1)
        whi = np.clip((L2 - 65) / 20, 0, 1)
        wmid = np.clip(1 - wsh - whi, 0, 1)
        for w, key in ((wsh, "golge"), (wmid, "orta"), (whi, "isik")):
            cur = ema[key]
            if np.any(np.isnan(cur)):
                continue
            d = (tgt[key] - cur) * a.guc
            d = np.clip(d, -12, 12)
            A = A + w * d[0]; B = B + w * d[1]
        # 3) doygunluk: ortalama kromayı hedefe (24.5) doğru ölçekle
        k = (T_KROMA / max(float(ema["kroma"][0]), 1)) ** a.guc
        k = float(np.clip(k, 0.6, 1.3))
        A = A * k; B = B * k
        out = np.dstack([L2, A, B]).astype(np.float32)
        rgb = np.clip(cv2.cvtColor(out, cv2.COLOR_LAB2RGB), 0, 1) * 255
        # 4) siyah noktası: her kanalı mor-siyahın (#221a1f) altına inmeyecek şekilde yumuşak tabanla.
        #    Zaten doğru olan koyular (referans gibi) neredeyse değişmez; saf siyah mor-siyaha döner.
        if a.siyah > 0:
            P = PLUM * a.siyah
            rgb = (rgb + P + np.sqrt((rgb - P) ** 2 + 36.0)) / 2
        enc.stdin.write(np.clip(rgb, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); dec.wait()
    print("yazıldı:", a.cikti)


if __name__ == "__main__":
    main()
