"""Kum Balıkçısı 2.5D: planları render eder.

    python render25.py kare --olcek 0.5 --plan 3,5 --t 0.5,1.0 --cikti onizleme/
    python render25.py hepsi                       # 12 klip -> ../klipler25/
"""
import argparse, os, subprocess
from multiprocessing import Pool
from PIL import Image
import sahne25 as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "klipler25")


def render_clip(args):
    idx, scale = args
    name, shot, n = S.SHOTS[idx]
    os.makedirs(OUT, exist_ok=True)
    w, h = int(1920 * scale), int(1080 * scale)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "25", "-i", "-",
                            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", os.path.join(OUT, name + ".mp4")],
                           stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(shot(i / S.FPS, scale).tobytes())
    enc.stdin.close(); enc.wait()
    return f"{name}: {n} kare"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mod", choices=["kare", "hepsi"])
    ap.add_argument("--olcek", type=float, default=1.0)
    ap.add_argument("--plan", default="")
    ap.add_argument("--t", default="0")
    ap.add_argument("--cikti", default="onizleme")
    a = ap.parse_args()
    plans = [int(x) - 1 for x in a.plan.split(",") if x] or list(range(len(S.SHOTS)))
    if a.mod == "kare":
        os.makedirs(a.cikti, exist_ok=True)
        for k in plans:
            for t in [float(x) for x in a.t.split(",")]:
                p = os.path.join(a.cikti, f"{S.SHOTS[k][0]}_{t:.2f}.png")
                Image.fromarray(S.SHOTS[k][1](t, a.olcek)).save(p); print(p, flush=True)
    else:
        # en uzun planlar önce: 4 çekirdeği dengeli kullan
        order = sorted(plans, key=lambda k: -S.SHOTS[k][2])
        with Pool(4) as pool:
            for r in pool.imap_unordered(render_clip, [(k, a.olcek) for k in order]):
                print(r, flush=True)
