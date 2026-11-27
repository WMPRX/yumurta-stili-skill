"""Kum Balıkçısı taslağı: SES.md'deki planı sentezler (kayıt yok, hepsi numpy ile).

    python ses.py   ->  ../ses/miks.wav (-21 LUFS)

Kesme saatleri render.py'nin kare sayılarından gelir (25 fps).
"""
import os, subprocess
import numpy as np
from scipy import signal

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
FR = [65, 23, 88, 50, 40, 45, 63, 100, 50, 70, 50, 100]
CUT = np.concatenate([[0], np.cumsum(FR)]) / 25.0      # plan başlangıçları
DUR = CUT[-1]
N = int(DUR * SR) + SR
rng = np.random.default_rng(7)
mix = np.zeros((N, 2), np.float32)


def at(plan, t):
    return CUT[plan - 1] + t


def place(x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    x = x[: N - i] * gain
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    mix[i:i + len(x), 0] += x * l * 1.41; mix[i:i + len(x), 1] += x * r * 1.41


def env(n, a=0.005, d=0.1, shape=3.0):
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / max(d, 1e-4) * shape / 3)
    return e.astype(np.float32)


def noise(dur):
    return rng.standard_normal(int(dur * SR)).astype(np.float32)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"); return signal.sosfilt(sos, x).astype(np.float32)


def lp(x, f, order=2):
    sos = signal.butter(order, f, "lowpass", fs=SR, output="sos"); return signal.sosfilt(sos, x).astype(np.float32)


def hp(x, f, order=2):
    sos = signal.butter(order, f, "highpass", fs=SR, output="sos"); return signal.sosfilt(sos, x).astype(np.float32)


def sine(freq, dur, phase=0.0):
    f = np.broadcast_to(np.asarray(freq, np.float32), (int(dur * SR),)) if np.ndim(freq) == 0 else np.asarray(freq, np.float32)
    return np.sin(2 * np.pi * np.cumsum(f) / SR + phase).astype(np.float32)


def saw(freq):
    ph = np.cumsum(np.asarray(freq, np.float32)) / SR
    return (2 * (ph % 1) - 1).astype(np.float32)


def glide(f0, f1, dur, curve=1.0):
    u = np.linspace(0, 1, int(dur * SR)) ** curve
    return (f0 * (f1 / f0) ** u).astype(np.float32)


def S(*xs):
    """Farklı uzunluktaki sesleri üst üste koy."""
    n = max(len(x) for x in xs); out = np.zeros(n, np.float32)
    for x in xs:
        out[: len(x)] += x
    return out


# ------------------------------------------------------------ ses nesneleri
def wind(dur):
    x = lp(noise(dur), 500, 2) * 0.6 + bp(noise(dur), 700, 1600) * 0.12
    t = np.arange(len(x)) / SR
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * t) * np.sin(2 * np.pi * 0.31 * t + 1)
    return x * mod


def tick(freq=1400, dur=0.05):
    x = sine(freq, dur) * env(int(dur * SR), 0.001, 0.012) + hp(noise(dur), 2000) * env(int(dur * SR), 0.0005, 0.004) * 0.5
    return x


def plop():
    d = 0.3
    x = sine(glide(380, 70, d, 0.6), d) * env(int(d * SR), 0.002, 0.12) + lp(noise(d), 900) * env(int(d * SR), 0.001, 0.05) * 0.6
    return x


def thump(f=60, d=0.5, k=1.0):
    return (sine(glide(f * 2, f, d, 0.4), d) * env(int(d * SR), 0.003, d * 0.5) + lp(noise(d), 300) * env(int(d * SR), 0.001, 0.08) * 0.8) * k


def whoosh(d=0.4, lo=400, hi=3000):
    x = noise(d)
    n = len(x)
    out = np.zeros(n, np.float32)
    seg = 512
    for i in range(0, n, seg):
        u = i / n
        f = lo + (hi - lo) * np.sin(np.pi * u)
        out[i:i + seg] = bp(x[max(0, i - 2048):i + seg], f * 0.7, f * 1.3)[-len(x[i:i + seg]):]
    return out * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5


def creak(d=0.45, f0=90):
    t = np.arange(int(d * SR)) / SR
    pulses = (np.random.default_rng(3).random(len(t)) < (f0 + 40 * np.sin(t * 20)) / SR).astype(np.float32)
    x = bp(pulses * 6, 400, 1800) + bp(pulses * 3, 2500, 4000)
    return x * np.sin(np.pi * np.linspace(0, 1, len(t))) * 0.8


def tin(f=420, d=0.8, k=1.0):
    x = sum(sine(f * r, d) * env(int(d * SR), 0.001, d * dd) * a for r, a, dd in ((1, 1, 0.5), (2.76, 0.6, 0.3), (5.4, 0.4, 0.18), (8.9, 0.25, 0.1)))
    return x * 0.5 * k


def pluck(freq, d=0.6):
    n = int(SR / freq); buf = rng.uniform(-1, 1, n).astype(np.float32)
    out = np.zeros(int(d * SR), np.float32)
    for i in range(len(out)):
        out[i] = buf[i % n]
        buf[i % n] = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * 0.994
    return lp(out, 3000)


def marimba(freq, d=1.2):
    return (sine(freq, d) * env(int(d * SR), 0.002, 0.5) + 0.35 * sine(freq * 4, d) * env(int(d * SR), 0.001, 0.08)) * 0.8


def sand(d, grain=0.6):
    x = bp(noise(d), 800, 6000) * 0.5 + lp(noise(d), 600) * 0.3
    g = (np.random.default_rng(5).random(len(x)) < grain * 0.02).astype(np.float32)
    x = x * (0.5 + 0.5 * lp(g * 30, 40))
    return x


def boing(d=0.35):
    t = np.linspace(0, 1, int(d * SR))
    f = 180 + 220 * t + 60 * np.sin(2 * np.pi * 14 * t * d) * (1 - t)
    return sine(f, d) * env(int(d * SR), 0.003, d * 0.7) * 0.9


def voice(pitch, vowel="a", d=None, breath=0.1):
    """Basit formant sesi: testere + formant bantları. pitch: Hz dizisi."""
    pitch = np.asarray(pitch, np.float32)
    src = saw(pitch) + breath * rng.standard_normal(len(pitch)).astype(np.float32)
    F = {"a": (800, 1200, 2700), "u": (330, 800, 2400), "i": (300, 2200, 3000), "e": (500, 1800, 2600), "o": (500, 900, 2500), "m": (250, 900, 2200), "h": (600, 1300, 2500)}[vowel]
    out = bp(src, F[0] * 0.8, F[0] * 1.2) * 1.0 + bp(src, F[1] * 0.85, F[1] * 1.15) * 0.6 + bp(src, F[2] * 0.9, F[2] * 1.1) * 0.25
    if vowel == "m":
        out = lp(out, 600)
    n = len(out)
    return out * np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5


def rumble(d):
    t = np.arange(int(d * SR)) / SR
    x = lp(noise(d), 90, 4) * 3 + sine(38 + 4 * np.sin(t * 3), d) * 0.6 + lp(noise(d), 250) * 0.4
    e = np.minimum(t / 0.35, 1) * np.minimum((d - t) / 0.4, 1)
    return x * e


def scream(d, f0=520, vowel="a"):
    t = np.linspace(0, 1, int(d * SR))
    f = f0 * (1 + 0.25 * np.sin(np.pi * t)) * (1 + 0.04 * np.sin(2 * np.pi * 7 * t * d))
    return voice(f, vowel)


# ------------------------------------------------------------ zaman çizelgesi
# ortam rüzgârı (sessiz duraklamada ve finalde kısılır)
w = wind(DUR + 1)
t = np.arange(len(w)) / SR
duck = np.ones_like(w)
for a, b in ((at(8, 1.4), at(9, 0.0)), (at(12, 0.6), at(12, 3.3))):
    duck *= 1 - 0.85 * np.clip((t - a) / 0.4, 0, 1) * np.clip((b - t) / 0.4, 0, 1)
place(w * duck, 0, 0.18)

# 1 arzu
place(creak(0.5, 70), at(1, 0.45), 0.35, 0.2)
place(whoosh(0.3, 600, 2500), at(1, 1.25), 0.25)
# 2 şamandıra
place(tick(1500), at(2, 0.1), 0.6); place(tick(1350), at(2, 0.28), 0.6)
place(plop(), at(2, 0.46), 0.9); place(sand(0.4), at(2, 0.48), 0.25)
# 3 küçük zafer
for k in range(6):
    place(bp(noise(0.07), 300, 1500) * env(int(0.07 * SR), 0.002, 0.03), at(3, 0.1 + k * 0.17), 0.35, 0.3)
place(hp(noise(0.28), 700) * env(int(0.28 * SR), 0.004, 0.12) + sand(0.28) * 0.6, at(3, 1.0), 0.7, 0.2)
place(voice(glide(260, 380, 0.25), "h", breath=0.6), at(3, 1.1), 0.35)
for b in (1.55, 1.75, 1.95):
    place(tick(2600, 0.03), at(3, b), 0.15)
place(pluck(392, 0.4), at(3, 2.4), 0.45); place(pluck(523, 0.5), at(3, 2.6), 0.45)
# 4 tırmanma
place(tin(520, 0.7), at(4, 0.33), 0.5, 0.5)
place(whoosh(0.4, 900, 4000), at(4, 0.42), 0.35, -0.3)
place(plop() * 0.6, at(4, 0.85), 0.45, -0.5)
for ty in (1.1, 1.55):
    place(creak(0.4, 110), at(4, ty - 0.05), 0.6, 0.3)
    place(voice(glide(200, 150, 0.3), "e", breath=0.4), at(4, ty), 0.3, 0.3)
    place(thump(70, 0.25), at(4, ty), 0.35, 0.3)
# 5 balina: en yüksek vuruş
place(rumble(1.9), at(5, 0.0), 1.0)
place(sand(1.7, 1.0) * np.minimum(np.arange(int(1.7 * SR)) / (0.3 * SR), 1), at(5, 0.1), 0.6, -0.4)
place(thump(45, 0.9, 1.4), at(5, 0.0), 0.9)
# 6 çekiliş
place(sine(glide(900, 220, 0.9, 0.7), 0.9) * env(int(0.9 * SR), 0.01, 0.6) * 0.5 + whoosh(0.9, 500, 3000), at(6, 0.0), 0.55, -0.3)
place(scream(0.8, 560), at(6, 0.1), 0.4, -0.2)
for k, ty in enumerate((0.3, 0.6, 0.9)):
    place(S(thump(160, 0.12), tick(700, 0.05)), at(6, ty), 0.3, 0.6)
place(sand(0.9, 1.0), at(6, 0.0), 0.4, -0.6)
# 7 kum kayağı
d7 = FR[6] / 25
x = sand(d7, 1.2) * (0.6 + 0.4 * np.abs(np.sin(7.5 * np.arange(int(d7 * SR)) / SR)))
place(x, at(7, 0.0), 0.55)
for k in range(6):
    place(thump(90, 0.15), at(7, k * 0.419), 0.25)
for k, a in enumerate((0.0, 0.6, 1.2, 1.8)):
    if k % 2 == 0:
        place(voice(np.concatenate([glide(330, 520, 0.2), glide(520, 600, 0.3)]), "u"), at(7, a + 0.05), 0.35)
    else:
        place(scream(0.45, 600), at(7, a + 0.05), 0.35)
# 8 sessiz duraklama
place(thump(55, 0.6, 1.2) + sand(0.6) * 0.5, at(8, 0.45), 0.8, -0.5)
place(S(tin(300, 0.5, 0.9), thump(120, 0.2) * 0.6), at(8, 1.25), 0.55, -0.2)
place(tin(300, 0.25, 0.4), at(8, 1.45), 0.25, -0.2)
for b in (2.3, 3.15):
    place(tick(3000, 0.02), at(8, b), 0.08)
# 9 ikinci deneme
place(bp(noise(0.3), 1500, 4000) * env(int(0.3 * SR), 0.01, 0.1) * 0.3, at(9, 0.3), 0.2)
place(tick(1800), at(9, 1.05), 0.35)
for k in range(5):
    place(tin(600, 0.08, 0.4), at(9, 1.5 + k * 0.07), 0.25, 0.4)
# 10 ters köşe 2
for k in range(4):
    place(tin(600, 0.08, 0.4), at(10, 0.42 + k * 0.05), 0.3, 0.5)
place(whoosh(0.35, 1500, 5000), at(10, 0.48), 0.35, 0.3)
place(S(thump(300, 0.08), tick(900, 0.06)), at(10, 0.82), 0.7)
place(voice(np.concatenate([glide(420, 650, 0.25), glide(650, 560, 0.45)]), "m", breath=0.2), at(10, 0.9), 0.6)
# 11 panik
for ty in (0.2, 0.9, 1.5):
    place(boing(0.4), at(11, ty + 0.05), 0.55)
    place(creak(0.25, 150), at(11, ty), 0.25)
for k in range(10):
    place(bp(noise(0.06), 400, 2000) * env(int(0.06 * SR), 0.002, 0.02), at(11, 0.05 + k * 0.19), 0.2, ((k % 3) - 1) * 0.5)
place(voice(glide(700, 500, 0.5), "i"), at(11, 0.6), 0.25)
place(voice(glide(720, 480, 0.5), "i"), at(11, 1.25), 0.25)
# 12 final
place(bp(noise(0.3), 800, 3000) * env(int(0.3 * SR), 0.02, 0.15), at(12, 0.15), 0.15)
place(marimba(523), at(12, 1.5), 0.45)
for b in (0.9, 2.42, 3.55):
    place(tick(3000, 0.02), at(12, b), 0.08)
place(rumble(1.3) * 0.7, at(12, 2.95), 0.5)

# ------------------------------------------------------------ çıkış
mix = mix[: int(DUR * SR)]
peak = np.abs(mix).max()
mix = mix / max(peak, 1e-6) * 0.89
os.makedirs(os.path.join(HERE, "..", "ses"), exist_ok=True)
ham = os.path.join(HERE, "..", "ses", "miks_ham.wav")
out = os.path.join(HERE, "..", "ses", "miks.wav")
import wave
with wave.open(ham, "wb") as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ham, "-af", "loudnorm=I=-21:LRA=18:TP=-1.5", "-ar", "44100", out], check=True)
print("yazıldı:", out, f"{DUR:.2f} sn")
