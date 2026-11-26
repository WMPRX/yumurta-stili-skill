#!/usr/bin/env python3
"""Plan kliplerini stilin kurgu kurallarıyla birleştirir.

    python tools/kurgu.py kurgu.json cikti.mp4

kurgu.json (örnek: sablonlar/kurgu_ornek.json):
{
  "fps": 25, "boyut": [1920, 1080],
  "ses": "ses/miks.wav",                 # isteğe bağlı; yoksa sessiz
  "planlar": [
    {"klip": "klipler/01.mp4", "bas": 0.2, "sure": 2.6,
     "itme": 3,                           # plan boyunca toplam zoom yüzdesi (+ itme, - çekme). Referans: -12..+8, çoğu ±1..3
     "kay": [0, 0],                       # plan boyunca toplam kayma, px (1920 genişlikte) [x, y]
     "gecis": "kesme",                    # bu plana giriş: "kesme" | "smear"
     "smear_kare": 2, "smear_yon": 0,     # smear: kaç kare, bulanık yönü (derece, 0 = yatay)
     "sarsinti": [[1.2, 6]]               # [plan içi saniye, genlik px] darbe sarsıntıları; 0.3 sn'de söner
    }
  ]
}
Bütün kareler 1920x1080 (ya da "boyut") içine KIRPILARAK sığdırılır (letterbox yok).
Zoom/kayma alt-piksel hassasiyetle, kare kare uygulanır (ffmpeg zoompan'ın titremesi olmadan).
"""
import json, subprocess, sys, os
import numpy as np
import cv2


def read_frames(path, start, dur, fps, W, H):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur + 0.5), "-i", path,
           "-vf", f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = W * H * 3
    fr = [np.frombuffer(raw[i:i + n], np.uint8).reshape(H, W, 3) for i in range(0, len(raw) - n + 1, n)]
    need = int(round(dur * fps))
    if not fr:
        raise SystemExit(f"klip okunamadı: {path}")
    while len(fr) < need:          # klip kısa kalırsa son kareyi tut (uyarı ver)
        fr.append(fr[-1])
    if len(fr) > need:
        fr = fr[:need]
    return fr


def motion_blur(img, length, ang):
    length = max(1, int(length))
    k = np.zeros((length * 2 + 1, length * 2 + 1), np.float32)
    c = length
    dx, dy = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    for t in np.linspace(-length, length, length * 4 + 1):
        k[int(round(c + t * dy)), int(round(c + t * dx))] = 1
    k /= k.sum()
    return cv2.filter2D(img, -1, k, borderType=cv2.BORDER_REFLECT)


def main():
    cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    fps = cfg.get("fps", 25); W, H = cfg.get("boyut", [1920, 1080])
    s1080 = W / 1920
    enc = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    ses = cfg.get("ses")
    if ses:
        enc += ["-i", os.path.join(base, ses), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    enc += ["-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out]
    p = subprocess.Popen(enc, stdin=subprocess.PIPE)
    rng = np.random.default_rng(7)
    prev_last = None; t_total = 0.0; log = []
    for k, pl in enumerate(cfg["planlar"]):
        fr = read_frames(os.path.join(base, pl["klip"]), pl.get("bas", 0), pl["sure"], fps, W, H)
        n = len(fr)
        z_tot = pl.get("itme", 0) / 100.0
        kx, ky = [v * s1080 for v in pl.get("kay", [0, 0])]
        shakes = pl.get("sarsinti", [])
        sm = pl.get("smear_kare", 2) if pl.get("gecis") == "smear" else 0
        ang = pl.get("smear_yon", 0)
        for i, f in enumerate(fr):
            u = i / max(n - 1, 1)
            z = 1 + z_tot * u if z_tot >= 0 else 1 + abs(z_tot) * (1 - u)   # çekme: büyükten 1'e
            ox, oy = kx * (u - 0.5), ky * (u - 0.5)
            for (ts, amp) in shakes:
                dt = i / fps - ts
                if 0 <= dt < 0.3:
                    a = amp * s1080 * (1 - dt / 0.3)
                    ox += rng.normal() * a; oy += rng.normal() * a
            # kayma kadraj dışına taşmasın diye en az gereken zoom
            need = 1 + 2 * max(abs(ox) / W, abs(oy) / H)
            z = max(z, need)
            M = np.float32([[z, 0, (1 - z) * W / 2 + ox], [0, z, (1 - z) * H / 2 + oy]])
            g = f if (z == 1 and ox == 0 and oy == 0) else cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            if i < sm:
                L = (1 - i / sm) * 70 * s1080 + 12 * s1080
                g = motion_blur(g, L, ang)
                if i == 0 and prev_last is not None:
                    g = cv2.addWeighted(g, 0.7, motion_blur(prev_last, L, ang), 0.3, 0)
            p.stdin.write(np.ascontiguousarray(g).tobytes())
        prev_last = g
        log.append(f"plan {k+1:2d}  {t_total:6.2f}-{t_total + n / fps:6.2f}  {n / fps:4.2f} sn  {pl.get('gecis', 'kesme')}  {pl['klip']}")
        t_total += n / fps
    p.stdin.close(); p.wait()
    print("\n".join(log)); print(f"toplam {t_total:.2f} sn, {len(cfg['planlar'])} plan, ort {t_total / len(cfg['planlar']):.2f} sn -> {out}")


if __name__ == "__main__":
    main()
