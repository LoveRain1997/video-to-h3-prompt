#!/usr/bin/env bash
# forensic_probe.sh — H3 视频反推一键取证 (macOS/Linux)
# 用法: bash forensic_probe.sh "IN.mp4" [out_dir] [fps]
# 产出: ffprobe 信息 + 稀疏帧 + 4x4 网格 + audio.wav + 频谱图 + RMS/BPM 表
set -euo pipefail

IN="${1:?usage: bash forensic_probe.sh IN.mp4 [out_dir] [fps]}"
OUT="${2:-forensic_out}"
FPS="${3:-2}"
command -v ffmpeg >/dev/null  || { echo "ERROR: ffmpeg not found"; exit 1; }
command -v ffprobe >/dev/null || { echo "ERROR: ffprobe not found"; exit 1; }

mkdir -p "$OUT/frames"
echo "=== [1/6] ffprobe ==="
ffprobe -v error -show_entries format=duration,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels -of default=noprint_wrappers=1 "$IN" | tee "$OUT/probe.txt"

echo "=== [2/6] sparse frames at ${FPS}fps (width 480) ==="
ffmpeg -y -v error -i "$IN" -vf "fps=${FPS},scale=480:-1" "$OUT/frames/f_%02d.jpg"
echo "frames: $(ls "$OUT/frames" | wc -l)"

echo "=== [3/6] contact sheet 4x4 (yellow padding) ==="
ffmpeg -y -v error -framerate 1 -i "$OUT/frames/f_%02d.jpg" \
  -vf "scale=240:-2,tile=4x4:padding=4:color=yellow" "$OUT/grid_%03d.jpg"

echo "=== [4/6] audio 22050 mono ==="
if ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 "$IN" | grep -q audio; then
  ffmpeg -y -v error -i "$IN" -vn -ac 1 -ar 22050 "$OUT/audio.wav"
  echo "=== [5/6] spectrogram ==="
  ffmpeg -y -v error -i "$OUT/audio.wav" -lavfi showspectrumpic=s=1000x400:legend=1 "$OUT/spectrum.jpg"
  echo "=== [6/6] RMS + BPM credibility ==="
  python3 "$(dirname "$0")/audio_probe.py" "$OUT/audio.wav" | tee "$OUT/audio_stats.txt"
else
  echo "no audio stream - skip"
fi

echo
echo "DONE. Inspect $OUT/grid_*.jpg, then dense-extract ambiguous windows:"
echo "  ffmpeg -ss <start> -t <dur> -i \"$IN\" -vf 'fps=4,scale=360:-1' $OUT/seg/seg_%02d.jpg"
