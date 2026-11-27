"""Kum Balıkçısı taslağı: planları render eder.

    python render.py klip [--olcek 1.0] [--plan 3,5] [--kare 0.5]   # tek kare önizleme (sn)
    python render.py hepsi                                            # 12 klip -> ../klipler/
"""
import argparse, os, subprocess, sys, math
from multiprocessing import Pool
import numpy as np
from PIL import Image
import boya as B
import sahneler as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "klipler")


def frame(shot, t, scale):
    fr = B.Frame(scale)
    spec = shot(t, fr)
    return B.composite(fr, spec)


def render_clip(args):
    idx, scale = args
    name, shot, n = S.SHOTS[idx]
    os.makedirs(OUT, exist_ok=True)
    w, h = int(B.W * scale), int(B.H * scale)
    path = os.path.join(OUT, name + ".mp4")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", "25", "-i", "-",
                            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(frame(shot, i / S.FPS, scale).tobytes())
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
        ts = [float(x) for x in a.t.split(",")]
        os.makedirs(a.cikti, exist_ok=True)
        for k in plans:
            for t in ts:
                img = frame(S.SHOTS[k][1], t, a.olcek)
                p = os.path.join(a.cikti, f"{S.SHOTS[k][0]}_{t:.2f}.png")
                Image.fromarray(img).save(p); print(p)
    else:
        with Pool(4) as pool:
            for r in pool.imap_unordered(render_clip, [(k, a.olcek) for k in plans]):
                print(r, flush=True)
