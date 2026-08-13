# Audio Heuristics for H3 Prompts

How to read `volumedetect` output and translate it into the right `overall_soundscape` and `non_diegetic_music` lines.

## Measure First

```bash
ffmpeg -y -i "<video>" -vn -ac 1 -ar 8000 -f wav out.wav
ffmpeg -i out.wav -af "volumedetect" -f null - 2>&1 | grep volume
```

Two numbers you care about:

| Metric | Meaning |
|---|---|
| `mean_volume` | Average loudness across the full track |
| `max_volume` | Peak transient — anything above -3 dB risks clipping |

## Reading Table

| mean_volume | max_volume | Likely content | `non_diegetic_music` recipe |
|---|---|---|---|
| -8 to -12 dB | 0 to -2 dB | Loud club / electronic / EDM | `An energetic electronic track at a fast tempo with heavy kick, layered synth lead, and side-chained bass.` |
| -10 to -15 dB | -1 to -3 dB | Pop / dance-pop / K-pop | `A bright pop track at a moderate tempo with synth lead, four-on-the-floor kick, and bright claps.` |
| -13 to -17 dB | -3 to -6 dB | Anime / chiptune / cute pop | `A bright Japanese-style anime dance-pop track at a moderate tempo with bouncy synth leads, four-on-the-floor kick, and cute chiptune flourishes.` |
| -16 to -20 dB | -5 to -8 dB | Live show / restaurant / cafe vlog | `A warm light-pop backing track at a relaxed tempo with soft acoustic-guitar arpeggios, gentle brushed snare, and a subtle piano lead.` |
| -20 to -25 dB | -8 to -12 dB | Cinematic score / underscore | `A restrained orchestral score at a slow tempo with sustained low strings and no swell.` |
| -25 to -35 dB | -12 to -18 dB | Ambient drone / nature | `A quiet ambient drone with soft room tone and no melodic development.` |
| < -35 dB | < -18 dB | Near-silent | `N/A` (set to non_diegetic_music: N/A) |

## overall_soundscape Recipes

Always pair the music recipe with one ambience line. Templates by venue:

| Venue | Template |
|---|---|
| Indoor restaurant / cafe | `Soft indoor <type> ambience fills the space: a faint ceiling-fan hum, the muffled clatter of dishes from neighboring tables, and a brief distant shout from the kitchen.` |
| Outdoor urban night | `Steady light rain falls on the pavement and taps softly on umbrella fabric. Distant traffic hums beneath the music, with faint passing-car whooshes appearing during Shot N.` |
| Concert / club | `A live performance ambience with a soft crowd murmur beneath the music.` |
| Quiet room | `A quiet room tone with soft daylight ambience.` |
| Forest / nature | `Birdsong and a soft breeze filter through the leaves.` |

Add a **diegetic action sound** for every visible action:

| Visible action | Add this line |
|---|---|
| Spinning / twirling | `costume fabric rustles softly as <Subject 1> turns` |
| Walking on wet ground | `soft footstep splashes under <Subject 1>'s heels` |
| Opening umbrella | `the metallic click of the umbrella runner and the soft snap of the canopy opening` |
| Blowing nose / wiping | `the rustle of paper tissue when <Subject 1> wipes her face` |
| Glass breaking | `the sharp crash of glass fragments scattering across the floor` |

## Dialogue vs Music vs Ambience — How to Tell

If you cannot listen to the audio, infer from the video:

- **Visible speech** (mouth open, gesturing, microphone visible) → expect dialogue; use `<d>[Language] text</d>` inside `detailed_description` and keep `non_diegetic_music` low or `N/A`.
- **Synchronized dance / coordinated movement** → expect music; describe in `non_diegetic_music`.
- **Empty stage / talking head / quiet scene** → expect ambient + light underscore; both sections populated lightly.

## When the Source Audio Is Silent or Near-Silent

Set `non_diegetic_music: N/A` and put **all** sonic detail in `overall_soundscape` (room tone, fabric rustle, breath, footfall).

## Do Not

- Do not name specific songs, artists, or copyrighted scores.
- Do not transcribe lyrics.
- Do not mix music with ambience in the same section; keep them in their own blocks.
- Do not write `non_diegetic_music` that is louder than the original — H3 will scale it up automatically.
