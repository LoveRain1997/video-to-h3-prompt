<#
.SYNOPSIS
  H3 video reverse-engineering one-click forensics (Windows PowerShell).
.DESCRIPTION
  Produces: ffprobe summary, 2fps sparse frames, 4x4 contact sheet(s),
  mono audio wav, spectrogram, and (via audio_probe.py) RMS envelope + BPM credibility.
  After it finishes, use dense 4-8fps extraction on ambiguous windows.
  Note: parameter is named -Video (NOT -Input, which is a PowerShell automatic variable).
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File forensic_probe.ps1 -Video ".\clip.mp4" -OutDir forensic_out
#>
param(
  [Parameter(Mandatory = $true)][string]$Video,
  [string]$OutDir = "forensic_out",
  [int]$Fps = 2
)

$ErrorActionPreference = "Stop"
function Assert-Cmd($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { throw "ERROR: $name not found on PATH" }
}
Assert-Cmd ffmpeg
Assert-Cmd ffprobe

if (-not (Test-Path -LiteralPath $Video)) { throw "ERROR: video not found: $Video" }
New-Item -ItemType Directory -Force -Path (Join-Path $OutDir "frames") | Out-Null

Write-Host "=== [1/6] ffprobe ===" -ForegroundColor Cyan
ffprobe -v error -show_entries format=duration,bit_rate `
  -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels `
  -of default=noprint_wrappers=1 $Video | Tee-Object (Join-Path $OutDir "probe.txt")

Write-Host "=== [2/6] sparse frames at ${Fps}fps (width 480) ===" -ForegroundColor Cyan
ffmpeg -y -v error -i $Video -vf "fps=$Fps,scale=480:-1" (Join-Path $OutDir "frames/f_%02d.jpg")
$frameCount = (Get-ChildItem (Join-Path $OutDir "frames") -Filter *.jpg).Count
Write-Host "frames: $frameCount"

Write-Host "=== [3/6] contact sheet 4x4 (yellow padding) ===" -ForegroundColor Cyan
ffmpeg -y -v error -framerate 1 -i (Join-Path $OutDir "frames/f_%02d.jpg") `
  -vf "scale=240:-2,tile=4x4:padding=4:color=yellow" (Join-Path $OutDir "grid_%03d.jpg")

Write-Host "=== [4/6] audio extraction 22050 mono ===" -ForegroundColor Cyan
$hasAudio = ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 $Video
if ($hasAudio -match "audio") {
  ffmpeg -y -v error -i $Video -vn -ac 1 -ar 22050 (Join-Path $OutDir "audio.wav")

  Write-Host "=== [5/6] spectrogram ===" -ForegroundColor Cyan
  ffmpeg -y -v error -i (Join-Path $OutDir "audio.wav") `
    -lavfi showspectrumpic=s=1000x400:legend=1 (Join-Path $OutDir "spectrum.jpg")

  Write-Host "=== [6/6] RMS envelope + BPM credibility ===" -ForegroundColor Cyan
  $py = Join-Path $PSScriptRoot "audio_probe.py"
  python $py (Join-Path $OutDir "audio.wav") | Tee-Object (Join-Path $OutDir "audio_stats.txt")
} else {
  Write-Host "no audio stream - skip spectrogram / rms" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "DONE. Inspect $OutDir\grid_*.jpg to build the skeleton, then dense-extract ambiguous windows:" -ForegroundColor Green
Write-Host "  ffmpeg -ss <start> -t <dur> -i `"$Video`" -vf 'fps=4,scale=360:-1' $OutDir\seg\seg_%02d.jpg"
