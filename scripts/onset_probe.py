#!/usr/bin/env python3
"""
onset_probe.py — music ONSET / CARD-POINT detection for video reverse-engineering.

Why this exists:
  audio_probe.py gives a 0.5s RMS energy envelope (good for "where is energy").
  Card-point editing needs the exact pluck/attack INSTANTS (onsets) that cuts,
  hits and impacts land on — RMS at 0.5s is too coarse. This script detects
  note onsets from a high-frequency-weighted spectral-flux envelope, grades
  them strong(S)/hard(H)/tremolo(.) and reports a reference tempo.

  It uses ONLY numpy + scipy (no librosa), so it runs on Python versions where
  librosa has no wheel yet (e.g. Python 3.14). Feed it the mono wav produced by
  forensic_probe (ffmpeg -ac 1 -ar 22050); any sample rate works.

Usage:
  python onset_probe.py audio.wav
  python onset_probe.py audio.wav --csv onsets.csv
  python onset_probe.py audio.wav --min-spacing 0.055 --strong-q 0.85 --hard-q 0.70

Output:
  - reference tempo from envelope autocorrelation (LOW confidence on free-tempo
    rubato / lunzhi-tremolo solo instruments such as pipa — do NOT treat as a metronome)
  - strong(S)/hard(H) onset times = card-point candidates to reconcile against cuts
  - per-second onset density / max-strength contour = phrase/energy shape

Then build the onset<->picture reconciliation table (see references/07-onset-and-card-points.md):
every hard cut / freeze / impact / volley / aura-burst should land on an S/H onset;
if it does, the clip is EDITORIAL/phrase-synced; only then trust timed "on the accent"
direction. If picture changes do NOT track onsets, fall back to free camera timing.
"""
import argparse
import csv
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import stft, find_peaks


def load_wav(path):
    sr, y = wavfile.read(path)
    y = y.astype(np.float64)
    if y.ndim > 1:
        y = y.mean(axis=1)
    peak = np.abs(y).max()
    if peak > 0:
        y /= peak
    return y, sr


def spectral_flux(y, sr, nper=1024, hop=256):
    """High-frequency-weighted positive spectral flux (pluck/attack detector)."""
    f, _t, Z = stft(y, fs=sr, nperseg=nper, noverlap=nper - hop)
    mag = np.abs(Z)
    weight = 1.0 + 0.6 * (f / (sr / 2.0))          # gentle treble emphasis (pipa/plucks)
    flux = np.zeros(mag.shape[1])
    for k in range(1, mag.shape[1]):
        d = mag[:, k] - mag[:, k - 1]
        d[d < 0] = 0
        flux[k] = (d * weight).sum()
    if flux.max() > 0:
        flux /= flux.max()
    flux = np.convolve(flux, np.ones(3) / 3, mode="same")   # light smoothing
    return flux, sr / hop


def detect_onsets(flux, fps, min_spacing, strong_q, hard_q, prom=0.02):
    dist = max(1, int(min_spacing * fps))
    med, sd = np.median(flux), np.std(flux)
    pk, props = find_peaks(flux, height=med + 0.55 * sd,
                           distance=dist, prominence=prom)
    if len(pk) == 0:
        return np.array([]), np.array([]), 0, 0
    times = pk / fps
    strength = props["peak_heights"]
    strong_cut = np.quantile(strength, strong_q)
    hard_cut = np.quantile(strength, hard_q)
    return times, strength, strong_cut, hard_cut


def grade(v, strong_cut, hard_cut):
    return "S" if v >= strong_cut else ("H" if v >= hard_cut else ".")


def reference_tempo(flux, fps, lo=0.28, hi=1.1):
    """Autocorrelation of the flux envelope. Reference only; unreliable in rubato."""
    x = flux - flux.mean()
    ac = np.correlate(x, x, "full")[len(x) - 1:]
    a, b = int(lo * fps), int(hi * fps)
    if b >= len(ac):
        return None
    lag = a + int(np.argmax(ac[a:b]))
    return 60.0 / (lag / fps)


def per_second(times, strength, dur):
    rows = []
    for s0 in range(int(np.ceil(dur))):
        m = (times >= s0) & (times < s0 + 1)
        n = int(m.sum())
        mx = float(strength[m].max()) if n else 0.0
        rows.append((s0, n, mx))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Music onset / card-point detector (numpy+scipy only).")
    ap.add_argument("wav", help="mono wav, e.g. forensic_out/audio.wav")
    ap.add_argument("--csv", default=None, help="optional CSV output of every graded onset")
    ap.add_argument("--min-spacing", type=float, default=0.055, help="minimum seconds between onsets")
    ap.add_argument("--strong-q", type=float, default=0.85, help="quantile above which an onset is S")
    ap.add_argument("--hard-q", type=float, default=0.70, help="quantile above which an onset is H")
    args = ap.parse_args()

    y, sr = load_wav(args.wav)
    dur = len(y) / sr
    flux, fps = spectral_flux(y, sr)
    times, strength, sc, hc = detect_onsets(
        flux, fps, args.min_spacing, args.strong_q, args.hard_q)
    tempo = reference_tempo(flux, fps)

    print(f"sr={sr} dur={dur:.2f}s onsets={len(times)} "
          f"ref_tempo~{tempo:.1f} BPM" if tempo else
          f"sr={sr} dur={dur:.2f}s onsets={len(times)} ref_tempo=n/a")
    print("NOTE: ref_tempo is autocorrelation-only; free-tempo rubato/solo pipa has NO usable BPM.")
    print("S=strong(>%g) H=hard(>%g) .=weaker/tremolo" % (args.strong_q, args.hard_q))

    print("\n== STRONG / HARD onsets (card-point candidates) ==")
    line = [f"{t:5.2f}{grade(v, sc, hc)}" for t, v in zip(times, strength)
            if v >= hc]
    # wrap into readable rows
    for i in range(0, len(line), 12):
        print(" ".join(line[i:i + 12]))

    print("\n== per-1s density / max-strength (phrase contour) ==")
    for s0, n, mx in per_second(times, strength, dur):
        bar = "#" * int(mx * 30)
        print(f"{s0:5.1f}-{s0+1:<4.1f} n={n:2d} max={mx:.2f} {bar}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["time_sec", "strength", "grade"])
            for t, v in zip(times, strength):
                w.writerow([f"{t:.3f}", f"{v:.4f}", grade(v, sc, hc)])
        print(f"\nwrote {args.csv}", file=sys.stderr)


if __name__ == "__main__":
    main()
