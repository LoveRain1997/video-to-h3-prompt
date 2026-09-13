# FFmpeg Cheatsheet for Video Reverse-Engineering

All commands assume **PowerShell on Windows** (backtick `` ` `` is the line-continuation). Swap loop style and `NUL`→`/dev/null` on bash. The whole first-pass pipeline is also wrapped in `scripts/forensic_probe.ps1`.

## Probe Video Metadata

```powershell
ffprobe -v error -show_format -show_streams -of json "<video.mp4>"
```

One-line summary:

```powershell
ffprobe -v error -show_entries format=duration,bit_rate `
  -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels `
  -of default=nw=1 "<video.mp4>"
```

Six fields that drive later decisions: `duration` (final H3 duration, ±0.02), `width×height` (portrait vs landscape), `r_frame_rate`, `nb_frames` (duration×fps sanity), `codec_name`, `has_b_frames` (>0 → add `-noaccurate_seek` for cleaner seeks).

## Extract Frames at Fixed Interval (sparse skeleton pass)

```powershell
$interval = 0.2; $count = 73; $out = "D:\path\frames"
New-Item -ItemType Directory -Force -Path $out | Out-Null
for ($i=0; $i -le $count; $i++) {
  $t = "{0:F3}" -f ($i * $interval)
  ffmpeg -y -ss $t -i "<video.mp4>" -frames:v 1 `
         -vf "scale=iw/2:-1" -q:v 3 "$out\f_$i.jpg" -loglevel error
}
```

Interval by duration: <5s→0.2s; 5–10s→0.3–0.4s; 10–15s→0.15–0.2s; >15s→0.2s + targeted re-extracts at transitions. The single biggest quality lever is **re-extracting a missed transition at half the interval**.

## Continuous-Rate Extraction (dense pass over a transition)

```powershell
# whole clip at 2fps, width 480
ffmpeg -y -i "<video.mp4>" -vf "fps=2,scale=480:-1" frames/f_%02d.jpg
# a 2.5s ambiguous window at 4fps (8fps if needed)
ffmpeg -y -ss 8.5 -t 2.5 -i "<video.mp4>" -vf "fps=4,scale=360:-1" seg/c_%02d.jpg
```

## Single Frame at Exact Time (full-resolution final check)

```powershell
ffmpeg -y -ss 9.800 -i "<video.mp4>" -frames:v 1 -q:v 2 "key_9_8.jpg"
```

## Contact Sheet / Grid (read the whole timeline at once)

```powershell
# 4x4 grid, yellow padding makes reading order obvious
ffmpeg -y -framerate 1 -i frames/f_%02d.jpg `
  -vf "scale=240:-2,tile=4x4:padding=4:color=yellow" grid_%03d.jpg
# dense window 5x2
ffmpeg -y -framerate 1 -i seg/c_%02d.jpg `
  -vf "scale=200:355,tile=5x2:padding=3:color=yellow" seg/c_grid.jpg
```

More than 16 input frames → ffmpeg emits multiple `grid_001/002...` sheets.

## Audio Dump + Spectrogram

```powershell
ffmpeg -y -i "<video.mp4>" -vn -ac 1 -ar 22050 audio.wav         # analysis grade
ffmpeg -y -i audio.wav -lavfi showspectrumpic=s=1000x400:legend=1 spectrum.jpg
ffmpeg -y -i "<video.mp4>" -vn -ac 1 -ar 8000 -f wav out8k.wav   # loudness grade
ffmpeg -i out8k.wav -af "volumedetect" -f null NUL 2>&1 | Select-String volume
python scripts/audio_probe.py audio.wav                          # RMS + BPM credibility
```

## Visual Difference Strip (auto-locate hard cuts)

```powershell
New-Item -ItemType Directory -Force -Path diff | Out-Null
for ($i=1; $i -le 73; $i++) {
  $prev = $i - 1
  ffmpeg -y -i "f_$i.jpg" -i "f_$prev.jpg" `
         -filter_complex "blend=all_mode=difference" -frames:v 1 "diff/d_$i.jpg"
}
```

Nearly black `diff` = identical (continuous); bright output = a hard cut. Composition jump (angle/focal length) also reads as a cut; smooth push/pull/pan is camera movement, not a cut.

## First and Last Frame (I2VA / L2VA anchors)

```powershell
ffmpeg -y -i "<video.mp4>" -vf "select=eq(n\,0)" -frames:v 1 first.jpg
$dur = (ffprobe -v error -show_entries format=duration -of csv=p=0 "<video.mp4>")
ffmpeg -y -ss $dur -i "<video.mp4>" -frames:v 1 last.jpg
```

## Common Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `q=0` and `-q:v` ignored | Output is `.png` | Use `.jpg` |
| Black frames at start | `-ss` seek placement | Move `-ss` after `-i` for accuracy, or `-noaccurate_seek` |
| `Permission denied` writing frames | Directory missing | `New-Item -ItemType Directory -Force` first |
| Frames off by ~1s | Input seek vs output seek | Add `-noaccurate_seek` or move `-ss` after `-i` |
| Audio dump silent | No audio stream | Check `ffprobe -show_streams`; skip audio analysis if no `codec_type: audio` |
| Grid only shows first 16 frames | tile fixed at 4x4 | Use `grid_%03d.jpg` pattern to emit multiple sheets |
| Path with spaces fails | Missing quotes | Always quote full paths |
