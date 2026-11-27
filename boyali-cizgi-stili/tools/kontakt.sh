#!/usr/bin/env bash
# Zaman damgalı kontakt sayfası: kesmeleri ve planları gözle kontrol etmek için.
#   tools/kontakt.sh video.mp4 cikti.png [kare/sn=2] [baslangic=0] [sure=tum]
set -e
V="$1"; O="$2"; R="${3:-2}"; SS="${4:-0}"; T="${5:-}"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
LEN=${T:-$DUR}
N=$(python3 -c "import math;print(max(1,math.ceil(float('$LEN')*float('$R'))))")
COLS=6; ROWS=$(( (N + COLS - 1) / COLS ))
ffmpeg -v error -y -ss "$SS" ${T:+-t "$T"} -i "$V" \
  -vf "fps=$R,scale=320:-1,drawtext=text='%{pts\:flt}':x=5:y=5:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.7,tile=${COLS}x${ROWS}" \
  -frames:v 1 "$O"
echo "yazıldı: $O ($N kare)"
