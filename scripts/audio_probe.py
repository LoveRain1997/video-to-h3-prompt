#!/usr/bin/env python3
"""audio_probe.py — reverse-engineering forensics: 0.5s RMS envelope + BPM credibility.
Usage: python audio_probe.py audio.wav
Needs numpy (required); librosa optional (without it, only RMS/band energy is printed).
Cross-platform (Windows / macOS / Linux).
"""
import sys
import wave

import numpy as np


def load_wav(path):
    w = wave.open(path, "rb")
    sr, n, width, ch = w.getframerate(), w.getnframes(), w.getsampwidth(), w.getnchannels()
    raw = w.readframes(n)
    w.close()
    dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(width, np.int16)
    x = np.frombuffer(raw, dtype=dtype).astype(float) / (np.iinfo(dtype).max or 1)
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def rms_envelope(x, sr, hop_sec=0.5):
    hop = int(sr * hop_sec)
    return [(i / sr, float(np.sqrt((x[i:i + hop] ** 2).mean())))
            for i in range(0, len(x), hop) if len(x[i:i + hop])]


def band_energy(x, sr):
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    out = {}
    for lo, hi, name in [(0, 250, "low"), (250, 2000, "mid"), (2000, sr // 2, "hi")]:
        m = (freqs >= lo) & (freqs < hi)
        out[name] = round(float(spec[m].mean()), 3) if m.any() else 0.0
    return out


def tempo_check(x, sr):
    try:
        import librosa
    except ImportError:
        return None
    tempo, _ = librosa.beat.beat_track(y=x, sr=sr)
    oe = librosa.onset.onset_strength(y=x, sr=sr)
    bpm = float(np.atleast_1d(tempo)[0])
    mean, std = float(oe.mean()), float(oe.std())
    ratio = std / mean if mean > 1e-9 else float("inf")
    return bpm, mean, std, ratio, ratio < 0.8


def main():
    if len(sys.argv) < 2:
        print("usage: python audio_probe.py audio.wav")
        sys.exit(1)
    x, sr = load_wav(sys.argv[1])
    print(f"sr={sr} dur={len(x)/sr:.2f}s global_rms={np.sqrt((x**2).mean()):.4f} peak={np.abs(x).max():.3f}")
    print("\n-- 0.5s RMS envelope (find peaks and reconcile each with a picture event) --")
    for t, v in rms_envelope(x, sr):
        print(f"{t:5.1f}s {v:.4f} {'#' * int(v * 100)}")
    print("\n-- band energy --", band_energy(x, sr))
    tc = tempo_check(x, sr)
    print("\n-- BPM credibility --")
    if tc is None:
        print("librosa not installed: pip install librosa (RMS/band analysis works without it)")
        return
    bpm, mean, std, ratio, stable = tc
    print(f"estimated BPM={bpm:.1f}  onset mean={mean:.3f} std={std:.3f} std/mean={ratio:.2f}")
    if stable:
        print("=> regular onsets; with a matching kick grid in the spectrogram, treat as real BGM/BPM.")
    else:
        print("=> irregular onsets (std/mean>=0.8). If the spectrogram also lacks a regular low-freq grid,")
        print("   the BPM is a FALSE DETECTION -> conclude 'no stable BGM, diegetic field audio only'.")


if __name__ == "__main__":
    main()
