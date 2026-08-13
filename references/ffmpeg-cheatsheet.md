# FFmpeg Cheatsheet for Video Reverse-Engineering

All commands assume PowerShell on Windows. Swap the loop style for bash on Unix.

## Probe Video Metadata

```bash
ffprobe -v error -show_format -show_streams -of json "<video.mp4>"
```

For a one-line summary:

```bash
ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames -of default=nw=1 "<video.mp4>"
```

## Extract Frames at Fixed Interval

```bash
$interval = 0.2          # seconds between samples
$count = 73              # number of frames to extract
$out = "D:\path\frames"

for ($i=0; $i -le $count; $i++) {
  $t = "{0:F3}" -f ($i * $interval)
  ffmpeg -y -ss $t -i "<video.mp4>" -frames:v 1 `
         -vf "scale=iw/2:-1" -q:v 3 "$out\f_$i.jpg" -loglevel error
}
```

Adjust:

- `scale=iw/2:-1` → half resolution. Use `-1` for proportional, `360` to fix short side.
- `-q:v 3` → JPEG quality (1 best, 31 worst). 3 is a good balance for visual review.
- `-ss` before `-i` → fast seek, may be off by a frame. Use `-noaccurate_seek` if precision matters.

## Extract a Single Frame at Exact Time

```bash
ffmpeg -y -ss 4.500 -i "<video.mp4>" -frames:v 1 -q:v 2 "single.jpg"
```

## Extract a Range of Frames (Full Coverage)

```bash
ffmpeg -y -i "<video.mp4>" -vf "fps=10,scale=iw/2:-1" -q:v 3 "frame_%04d.jpg"
```

`fps=10` gives one frame every 100 ms. Use `fps=5` or `fps=2` for sparser sampling on long videos.

## Dump Audio for Analysis

```bash
ffmpeg -y -i "<video.mp4>" -vn -ac 1 -ar 8000 -f wav "audio.wav"
```

`-ac 1` mono, `-ar 8000` 8 kHz (small, fast to analyze, fine for volumedetect).

## Measure Audio Levels

```bash
ffmpeg -i "audio.wav" -af "volumedetect" -f null - 2>&1 | grep volume
```

Returns `mean_volume` and `max_volume` in dBFS.

## Build a Visual Difference Strip

Useful to spot cut frames automatically:

```bash
mkdir diff
for ($i=1; $i -le 73; $i++) {
  $prev = $i - 1
  ffmpeg -y -i "f_$i.jpg" -i "f_$prev.jpg" `
         -filter_complex "blend=all_mode=difference" -frames:v 1 "diff/d_$i.jpg"
}
```

Frames with very dark `diff/d_*.jpg` = identical (continuous). Frames with bright output = a hard cut.

## Extract Just the First and Last Frame

```bash
ffmpeg -y -i "<video.mp4>" -vf "select=eq(n\,0)" -frames:v 1 "first.jpg"
ffprobe -v error -show_entries format=duration -of csv=p=0 "<video.mp4>" | ForEach-Object {
  ffmpeg -y -ss $_ -i "<video.mp4>" -frames:v 1 "last.jpg"
}
```

## Concatenate Frames into a Contact Sheet

```bash
ffmpeg -y -i "f_%d.jpg" -vf "tile=6x4" -frames:v 1 "contact_sheet.jpg"
```

`tile=6x4` lays 6 columns × 4 rows. Adjust to match the number of frames.

## Common Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| `q=0` and `-q:v` ignored | Output is `.png` | Use `.jpg` |
| Black frames at start | `-ss` placement issue | Move `-ss` after `-i` for accuracy, or use `-noaccurate_seek` |
| `Permission denied` writing frames | Directory missing | `New-Item -ItemType Directory -Force -Path $out` first |
| Frames off by 1 s | `-ss` is doing input seek instead of output seek | Add `-noaccurate_seek` or move `-ss` after `-i` |
| Audio dump has no sound | Source has no audio stream | Check with `ffprobe ... -show_streams`; if no `codec_type: audio`, skip audio analysis |
