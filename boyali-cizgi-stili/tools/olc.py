#!/usr/bin/env python3
"""Boyalı çizgi stili: bir videoyu ölçer, JSON yazar.

    python tools/olc.py video.mp4 cikti.json [--kesme 0.32] [--plan "0,2.6,3.5,..."]

Ölçülenler (hepsi kare başına hesaplanıp plan ve video ortalamasına indirgenir):
  plan      : kesmeler, plan süreleri
  kamera    : plan içi global hareket (px/kare @1920 genişlik), zoom %/kare, dönme, sarsıntı
  ozne      : kamera hareketi çıkarıldıktan sonra kalan nesne hareketi
  ton       : luma yüzdelikleri, siyah/beyaz noktası, RMS kontrast
  renk      : doygunluk (HSV ve Lab kroma), ton aileleri (12 dilim, kroma ağırlıklı),
              sıcak/soğuk oranı, k-means palet (Lab'de)
  doku      : gren (düz bölgede kalıntı std), keskinlik (Laplace varyansı), kenar yoğunluğu
  derinlik  : kare içi keskinlik dağılımı (en keskin/en bulanık hücre oranı)
  vinyet    : köşe/merkez parlaklık oranı
  ses       : EBU R128 yüksekliği, sessiz aralıklar, spektral merkez
Sadece ffmpeg, numpy, opencv-python-headless gerekir.
"""
import json, subprocess, sys, argparse, re
import numpy as np
import cv2

W, H = 480, 270          # analiz çözünürlüğü (1920x1080'in 1/4'ü)
SCALE_TO_1080 = 1920 / W


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                         capture_output=True, text=True).stdout
    return json.loads(out)


def frames(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H}:flags=area",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


def hue_family(h_deg):
    # 12 aile, 30° dilim; kırmızı 345-15 arası
    return ((h_deg + 15) % 360 // 30).astype(int)


FAMILIES = ["kirmizi", "turuncu", "sari", "sari-yesil", "yesil", "yesil-cyan",
            "cyan", "gok-mavi", "mavi", "mor", "magenta", "pembe"]
WARM = {0, 1, 2, 11}
COOL = {5, 6, 7, 8}


def global_motion(prev_g, g):
    pts = cv2.goodFeaturesToTrack(prev_g, 400, 0.01, 8)
    if pts is None or len(pts) < 12:
        return None
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev_g, g, pts, None, winSize=(21, 21), maxLevel=3)
    ok = st.ravel() == 1
    a, b = pts[ok].reshape(-1, 2), nxt[ok].reshape(-1, 2)
    if len(a) < 12:
        return None
    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=1.5)
    if M is None:
        return None
    s = float(np.hypot(M[0, 0], M[1, 0]))
    rot = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
    # merkeze göre öteleme (zoom'un merkez dışı kaymasını ayır)
    c = np.array([W / 2, H / 2])
    cc = M[:, :2] @ c + M[:, 2]
    dx, dy = (cc - c) * SCALE_TO_1080
    inl = inl.ravel().astype(bool)
    # özne hareketi: kamera hareketi telafi edildikten sonra kalan kare farkı (0-255 ölçeğinde ortalama)
    warped = cv2.warpAffine(prev_g, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    ozne = float(np.abs(warped.astype(np.int16) - g.astype(np.int16))[8:-8, 8:-8].mean())
    return dict(dx=float(dx), dy=float(dy), zoom=(s - 1) * 100, rot=rot, inlier=float(inl.mean()), ozne=ozne)


def cell_sharpness(gray):
    lap = cv2.Laplacian(gray, cv2.CV_32F, ksize=3)
    gh, gw = 6, 8
    hs, ws = H // gh, W // gw
    v = np.array([[lap[i*hs:(i+1)*hs, j*ws:(j+1)*ws].var() for j in range(gw)] for i in range(gh)])
    return v


def ink_lines(gray):
    """İnce koyu çizgi (outline) yoğunluğu: 7 px black-hat > 40 olan piksel oranı (1920 genişliğe göre ölçeklenir)."""
    k = max(3, int(round(7 / SCALE_TO_1080)) | 1)
    bh = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    return float((bh > 40).mean())


def grain(gray):
    g = gray.astype(np.float32)
    med = cv2.medianBlur(gray, 5).astype(np.float32)
    res = g - med
    # düz bölge: yerel gradyanı düşük pikseller
    gx = cv2.Sobel(med, cv2.CV_32F, 1, 0); gy = cv2.Sobel(med, cv2.CV_32F, 0, 1)
    flat = np.hypot(gx, gy) < np.percentile(np.hypot(gx, gy), 30)
    return float(res[flat].std()) if flat.any() else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--kesme", type=float, default=0.18, help="kesme eşiği (iki yan farkı eksi plan içi fark)")
    ap.add_argument("--plan", default="", help="elle verilen kesme saatleri (sn, virgüllü); verilirse otomatik algı yerine kullanılır")
    ap.add_argument("--skor", action="store_true", help="kesme skorlarını stderr'e yaz (eşik ayarı için)")
    ap.add_argument("--palet", type=int, default=12)
    a = ap.parse_args()

    info = probe(a.video)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    num, den = map(int, vs["r_frame_rate"].split("/")); fps = num / den

    per = []          # kare başına ölçüler
    pal_samples = []
    hue_hist_total = np.zeros(12); chroma_total = 0.0
    mean_frame = np.zeros((H, W), np.float64)
    prev_g = prev_hist = prev_small = None
    hists, smalls = [], []
    for i, f in enumerate(frames(a.video)):
        g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
        hsv = cv2.cvtColor(f, cv2.COLOR_RGB2HSV_FULL)
        lab = cv2.cvtColor(f, cv2.COLOR_RGB2LAB).astype(np.float32)
        L = lab[..., 0] * 100 / 255; A = lab[..., 1] - 128; B = lab[..., 2] - 128
        C = np.hypot(A, B)
        hdeg = (np.degrees(np.arctan2(B, A)) + 360) % 360  # Lab ton açısı
        # HSV ton ailesi (insan sezgisine yakın)
        hh = hsv[..., 0].astype(np.float32) * 360 / 256
        fam = hue_family(hh)
        wts = C * (C > 8)
        hist = np.bincount(fam.ravel(), weights=wts.ravel(), minlength=12)
        hue_hist_total += hist; chroma_total += wts.sum()
        mean_frame += g

        # kesme skoru
        sm = cv2.resize(f, (64, 36), interpolation=cv2.INTER_AREA).astype(np.float32)
        hh2 = cv2.calcHist([hsv], [0, 1], None, [24, 8], [0, 256, 0, 256]); cv2.normalize(hh2, hh2, 1, 0, cv2.NORM_L1)
        cut = 0.0
        if prev_hist is not None:
            hd = cv2.compareHist(prev_hist, hh2, cv2.HISTCMP_BHATTACHARYYA)
            md = np.abs(sm - prev_small).mean() / 255
            cut = float(0.6 * hd + 1.6 * md)
        prev_hist, prev_small = hh2, sm
        hists.append(hh2); smalls.append(sm)

        mot = global_motion(prev_g, g) if prev_g is not None else None
        prev_g = g

        cs = cell_sharpness(g)
        rgb = f.reshape(-1, 3)
        d = dict(i=i, t=i / fps, cut=cut,
                 L_p1=float(np.percentile(L, 1)), L_p5=float(np.percentile(L, 5)), L_p50=float(np.percentile(L, 50)),
                 L_p95=float(np.percentile(L, 95)), L_p99=float(np.percentile(L, 99)), L_mean=float(L.mean()),
                 rms=float(L.std()),
                 rgb_min=[int(x) for x in np.percentile(rgb, 0.5, axis=0)], rgb_max=[int(x) for x in np.percentile(rgb, 99.5, axis=0)],
                 sat_hsv=float(hsv[..., 1].mean() / 255), chroma=float(C.mean()), chroma_p90=float(np.percentile(C, 90)),
                 warm=float(hist[list(WARM)].sum() / max(hist.sum(), 1e-6)), cool=float(hist[list(COOL)].sum() / max(hist.sum(), 1e-6)),
                 grain=grain(g), sharp=float(cv2.Laplacian(g, cv2.CV_32F).var()),
                 edge=float((cv2.Canny(g, 60, 140) > 0).mean()), cizgi=ink_lines(g),
                 dof=float(np.log10((cs.max() + 1) / (np.median(cs) + 1))),
                 sharp_cells=cs.round(1).tolist() if i % 25 == 0 else None,
                 mot=mot)
        per.append(d)
        if i % 5 == 0:
            idx = np.random.default_rng(i).choice(len(rgb), 3000, replace=False)
            pal_samples.append(lab.reshape(-1, 3)[idx])

    n = len(per)
    # ---- planlar
    if a.plan:
        cuts_t = [float(x) for x in a.plan.split(",") if x.strip()]
        cut_idx = sorted({int(round(t * fps)) for t in cuts_t if 0 < t * fps < n})
    else:
        # Karşılaştırmalı skor: kesmenin iki yanındaki kareler birbirinden, kendi plan içi
        # komşularından çok daha farklı olmalı. Sarsıntılı/hızlı planlar ve smear kareleri böylece elenir.
        def dist(i, j):
            i = min(max(i, 0), n - 1); j = min(max(j, 0), n - 1)
            return 0.6 * cv2.compareHist(hists[i], hists[j], cv2.HISTCMP_BHATTACHARYYA) + 1.6 * np.abs(smalls[i] - smalls[j]).mean() / 255
        sc = np.zeros(n)
        for i in range(2, n - 2):
            across = dist(i - 2, i + 2)
            within = max(dist(i - 6, i - 2), dist(i + 2, i + 6))
            sc[i] = across - within
        if a.skor:
            for i in range(n):
                if sc[i] > 0.05:
                    print("skor", round(i / fps, 2), round(float(sc[i]), 3), file=sys.stderr)
        cut_idx = []
        for i in range(2, n - 2):
            loc = sc[max(0, i - 4):i + 5]
            if sc[i] >= a.kesme and sc[i] == loc.max() and (not cut_idx or i - cut_idx[-1] >= 12):
                cut_idx.append(i)
    bounds = [0] + cut_idx + [n]
    shots = []
    for s, e in zip(bounds[:-1], bounds[1:]):
        seg = per[s:e]
        ms = [p["mot"] for p in seg[1:] if p["mot"] and p["mot"]["inlier"] > 0.35]
        def med(k, f=np.median):
            return float(f([m[k] for m in ms])) if ms else 0.0
        speed = [np.hypot(m["dx"], m["dy"]) for m in ms]
        # sarsıntı: hızın 5 karelik ortalamadan sapması
        if len(ms) > 6:
            dxs = np.array([m["dx"] for m in ms]); dys = np.array([m["dy"] for m in ms])
            k = np.ones(5) / 5
            shake = float(np.hypot(dxs - np.convolve(dxs, k, "same"), dys - np.convolve(dys, k, "same"))[3:-3].mean())
        else:
            shake = 0.0
        tot_zoom = float(np.sum([m["zoom"] for m in ms])) if ms else 0.0
        shots.append(dict(
            bas=round(s / fps, 2), son=round(e / fps, 2), sure=round((e - s) / fps, 2), kare=e - s,
            pan_px_kare=round(med("dx"), 2), tilt_px_kare=round(med("dy"), 2),
            hiz_px_kare_ort=round(float(np.mean(speed)) if speed else 0, 2),
            hiz_px_kare_maks=round(float(np.max(speed)) if speed else 0, 2),
            zoom_yuzde_kare=round(med("zoom", np.mean), 3), toplam_zoom_yuzde=round(tot_zoom, 1),
            donme_derece_kare=round(med("rot", np.mean), 3), sarsinti_px=round(shake, 2),
            ozne_hareket=round(med("ozne", np.mean), 2),
            L_ort=round(float(np.mean([p["L_mean"] for p in seg])), 1),
            kontrast_rms=round(float(np.mean([p["rms"] for p in seg])), 1),
            kroma=round(float(np.mean([p["chroma"] for p in seg])), 1),
            dof=round(float(np.mean([p["dof"] for p in seg])), 2),
            keskinlik=round(float(np.mean([p["sharp"] for p in seg])), 0),
        ))

    # ---- kesmelerdeki bulanık (smear) geçiş kareleri
    sh = np.array([p["sharp"] for p in per])
    smear = []
    for i in cut_idx:
        med_ = np.median(sh[max(0, i - 25):i + 25]) + 1e-6
        smear.append(int((sh[max(0, i - 4):i + 4] < 0.5 * med_).sum()))

    # ---- palet (Lab k-means)
    P = np.concatenate(pal_samples).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.5)
    _, lab_lbl, cent = cv2.kmeans(P, a.palet, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    share = np.bincount(lab_lbl.ravel(), minlength=a.palet) / len(lab_lbl)
    cent_rgb = cv2.cvtColor(cent.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_LAB2RGB).reshape(-1, 3)
    order = np.argsort(-share)
    palet = [dict(hex="#%02x%02x%02x" % tuple(int(c) for c in cent_rgb[k]), pay=round(float(share[k]), 3),
                  L=round(float(cent[k][0] * 100 / 255), 1), kroma=round(float(np.hypot(cent[k][1] - 128, cent[k][2] - 128)), 1))
             for k in order]

    # ---- vinyet
    mf = mean_frame / n
    ctr = mf[H // 3:2 * H // 3, W // 3:2 * W // 3].mean()
    cw, ch = W // 8, H // 8
    corners = np.mean([mf[:ch, :cw].mean(), mf[:ch, -cw:].mean(), mf[-ch:, :cw].mean(), mf[-ch:, -cw:].mean()])

    def avg(k):
        return round(float(np.mean([p[k] for p in per])), 3)

    def pct(k, q):
        return round(float(np.percentile([p[k] for p in per], q)), 3)

    hh = hue_hist_total / max(hue_hist_total.sum(), 1e-6)
    sure = [s["sure"] for s in shots]
    allm = [p["mot"] for p in per if p["mot"] and p["mot"]["inlier"] > 0.35]
    sp = np.array([np.hypot(m["dx"], m["dy"]) for m in allm]) if allm else np.zeros(1)
    zm = np.array([abs(m["zoom"]) for m in allm]) if allm else np.zeros(1)

    res = dict(
        dosya=a.video,
        format=dict(gen=vs["width"], yuk=vs["height"], fps=round(fps, 3), sure=float(info["format"]["duration"]),
                    kare=n, codec=vs["codec_name"], pix_fmt=vs.get("pix_fmt"), bitrate_kbps=round(int(info["format"]["bit_rate"]) / 1000)),
        plan=dict(sayi=len(shots), sure_ort=round(float(np.mean(sure)), 2), sure_medyan=round(float(np.median(sure)), 2),
                  sure_min=min(sure), sure_maks=max(sure), kesme_saatleri=[round(i / fps, 2) for i in cut_idx],
                  smear_kesme_orani=round(float(np.mean([x > 0 for x in smear])), 2) if smear else 0.0, smear_kare=smear),
        kamera=dict(hiz_px_kare_medyan=round(float(np.median(sp)), 2), hiz_px_kare_p90=round(float(np.percentile(sp, 90)), 2),
                    zoom_yuzde_kare_medyan=round(float(np.median(zm)), 3), zoom_yuzde_kare_p90=round(float(np.percentile(zm, 90)), 3),
                    duran_kare_orani=round(float(np.mean((sp < 0.3) & (zm < 0.03))), 3)),
        ton=dict(L_ort=avg("L_mean"), L_p1=avg("L_p1"), L_p5=avg("L_p5"), L_p50=avg("L_p50"), L_p95=avg("L_p95"), L_p99=avg("L_p99"),
                 rms_kontrast=avg("rms"),
                 en_koyu_rgb=[int(np.median([p["rgb_min"][c] for p in per])) for c in range(3)],
                 en_acik_rgb=[int(np.median([p["rgb_max"][c] for p in per])) for c in range(3)],
                 saf_siyah_kare_orani=round(float(np.mean([max(p["rgb_min"]) < 8 for p in per])), 3),
                 saf_beyaz_kare_orani=round(float(np.mean([min(p["rgb_max"]) > 250 for p in per])), 3)),
        renk=dict(doygunluk_hsv=avg("sat_hsv"), kroma_ort=avg("chroma"), kroma_p90=avg("chroma_p90"),
                  sicak=avg("warm"), soguk=avg("cool"),
                  ton_aileleri={FAMILIES[k]: round(float(hh[k]), 3) for k in range(12)}),
        palet=palet,
        doku=dict(gren=avg("grain"), gren_p10=pct("grain", 10), gren_p90=pct("grain", 90),
                  keskinlik=avg("sharp"), kenar_yogunlugu=avg("edge"), cizgi_yogunlugu=avg("cizgi")),
        derinlik=dict(dof_ort=avg("dof"), dof_p90=pct("dof", 90)),
        vinyet=dict(kose_merkez=round(float(corners / ctr), 3)),
        planlar=shots,
    )

    # ---- ses
    if any(s["codec_type"] == "audio" for s in info["streams"]):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-af", "ebur128=peak=true,silencedetect=n=-40dB:d=0.25",
                            "-f", "null", "-"], capture_output=True, text=True).stderr
        def grab(pat):
            m = re.findall(pat, r)
            return float(m[-1]) if m else None
        sil_s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
        sil_e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                             capture_output=True).stdout
        x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
        hop = 1600
        rms = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, "valid")[::hop]) if len(x) > hop else np.zeros(1)
        spec = np.abs(np.fft.rfft(x[: len(x) // 2048 * 2048].reshape(-1, 2048) * np.hanning(2048), axis=1))
        fr = np.fft.rfftfreq(2048, 1 / 16000)
        cent = float(np.median((spec * fr).sum(1) / (spec.sum(1) + 1e-9)))
        res["ses"] = dict(lufs=grab(r"I:\s+(-?[\d.]+) LUFS"), lra=grab(r"LRA:\s+([\d.]+) LU"), true_peak_dbfs=grab(r"Peak:\s+(-?[\d.]+) dBFS"),
                          sessiz=[[round(s, 2), round(e, 2)] for s, e in zip(sil_s, sil_e)],
                          spektral_merkez_hz=round(cent), rms_100ms=[round(float(v), 4) for v in rms])

    res["kare_basina"] = [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in p.items() if k not in ("sharp_cells",)}
                          for p in per]
    json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)
    # kısa özet
    s = {k: res[k] for k in ("format", "plan", "kamera", "ton", "renk", "doku", "derinlik", "vinyet")}
    print(json.dumps(s, ensure_ascii=False, indent=1))
    if "ses" in res:
        print(json.dumps({k: v for k, v in res["ses"].items() if k != "rms_100ms"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
