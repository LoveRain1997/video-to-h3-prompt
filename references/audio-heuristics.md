# Audio Heuristics for H3 Prompts

Two layers of audio analysis: **(A) forensic classification** — does the track even contain music, and where are its energy peaks; **(B) loudness → recipe mapping** — when music IS present, how to write `non_diegetic_music`. Run A before B; do not write a music recipe for a track that is actually pure field audio.

## A. Forensic classification (do this first)

### A1. Spectrogram — music vs field audio

```powershell
ffmpeg -y -i "IN.mp4" -vn -ac 1 -ar 22050 audio.wav
ffmpeg -y -i audio.wav -lavfi showspectrumpic=s=1000x400:legend=1 spectrum.jpg
```

- Evenly spaced low-frequency vertical stripes running through the whole clip → drum machine / beat, music present.
- Wide-band random energy with occasional rising harmonic arcs (≈800Hz→3kHz) → human speech / laugh / shout.
- Continuous full-band low-level wash → ambient bed (street, wind, engine).
- Vertical bright columns at freeze/spray moments → transient SFX; align them to picture events.

### A2. 0.5s RMS envelope + BPM credibility

```powershell
python scripts/audio_probe.py audio.wav
```

Mark every RMS peak and reconcile it with a picture cause (see the matrix in `01-forensics-commands.md`). A BPM readout is trustworthy ONLY when ALL hold:

1. `onset std / onset mean < 0.8` (regular beats);
2. the spectrogram shows a regular kick grid;
3. RMS rises/falls cyclically rather than in isolated spikes.

Otherwise the BPM is a false detection of random transients → conclude **no stable BGM, diegetic field audio only**, and set `non_diegetic_music` to explicit silence / `N/A`.

### A3. Dialogue vs music vs ambience (when you cannot listen)

- **Visible speech** (mouth open, gesturing, mic visible) → dialogue; wrap in `<d>[Language] text</d>` inside the timeline, keep music low or `N/A`.
- **Synchronized dance / coordinated movement** → expect music; describe it in `non_diegetic_music`.
- **Empty scene / talking head / quiet prank** → ambience + light underscore at most.
- An off-camera arm interacting with people, plus isolated RMS spikes and no kick grid → field audio (pouring, spray, choke, laughter), NOT music.

## B. Loudness → recipe mapping (volumedetect)

```powershell
ffmpeg -y -i "IN.mp4" -vn -ac 1 -ar 8000 -f wav out8k.wav
ffmpeg -i out8k.wav -af "volumedetect" -f null NUL 2>&1 | Select-String volume   # PowerShell
# bash: ffmpeg -i out8k.wav -af volumedetect -f null - 2>&1 | grep volume
```

| Metric | Meaning |
|---|---|
| `mean_volume` | Average loudness across the full track |
| `max_volume` | Peak transient — above -3 dB risks clipping |

| mean_volume | max_volume | Likely content | `non_diegetic_music` recipe |
|---|---|---|---|
| -8 to -12 dB | 0 to -2 dB | Loud club / electronic / EDM | `An energetic electronic track at a fast tempo with heavy kick, layered synth lead, and side-chained bass.` |
| -10 to -15 dB | -1 to -3 dB | Pop / dance-pop / K-pop | `A bright pop track at a moderate tempo with synth lead, four-on-the-floor kick, and bright claps.` |
| -13 to -17 dB | -3 to -6 dB | Anime / chiptune / cute pop | `A bright Japanese-style anime dance-pop track at a moderate tempo with bouncy synth leads, four-on-the-floor kick, and cute chiptune flourishes.` |
| -16 to -20 dB | -5 to -8 dB | Live show / restaurant / cafe vlog | `A warm light-pop backing track at a relaxed tempo with soft acoustic-guitar arpeggios, gentle brushed snare, and a subtle piano lead.` |
| -20 to -25 dB | -8 to -12 dB | Cinematic score / underscore | `A restrained orchestral score at a slow tempo with sustained low strings and no swell.` |
| -25 to -35 dB | -12 to -18 dB | Ambient drone / nature | `A quiet ambient drone with soft room tone and no melodic development.` |
| < -35 dB | < -18 dB | Near-silent | `N/A` |

## overall_soundscape recipes

| Venue | Template |
|---|---|
| Indoor restaurant / cafe | `Soft indoor <type> ambience fills the space: a faint ceiling-fan hum, the muffled clatter of dishes from neighboring tables, and a brief distant shout from the kitchen.` |
| Outdoor urban night | `Steady night-alley ambience: distant traffic hum, faint scooter idle vibration, and damp pavement room tone.` |
| Concert / club | `A live performance ambience with a soft crowd murmur beneath the music.` |
| Quiet room | `A quiet room tone with soft ambient detail.` |
| Forest / nature | `Birdsong and a soft breeze filter through the leaves.` |

Add a **diegetic action sound** for every visible action:

| Visible action | Add this line |
|---|---|
| Pouring liquid onto foot/ground | `audible pouring water, a dark wet patch spreading` |
| Liquid hitting a plastic visor | `a wet splat bursts across the plastic visor` |
| Spinning / turning | `costume fabric rustles softly as <Subject 1> turns` |
| Walking on wet ground | `soft footstep splashes under the heels` |
| Choking after a sip | `a choked cough-spit with water spurting from the lips` |
| Freeze-frame gag | `record-scratch squeal → punchy impact hit → half-second near-silence → ambient snap-back` (see `03-edit-effects.md`) |

## When the source is silent / pure field audio

Set `non_diegetic_music: N/A` (14-field style: `No non-diegetic music. Explicit silence of the music layer throughout; the soundtrack is diegetic field audio plus the freeze-frame comedic SFX hits only.`) and put ALL sonic detail in `overall_soundscape`.

## Do Not

- Do not name songs, artists, or copyrighted scores; do not transcribe lyrics.
- Do not mix music with ambience in one block; keep them in their own fields.
- Do not write music louder than the original — H3 scales it up automatically.
- Do not trust a BPM number without the three-condition check in A2.
