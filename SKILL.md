---
name: video-to-h3-prompt
description: Reverse-engineer a video into a complete MiniMax H3 prompt (T2VA / I2VA / FL2VA / L2VA / Ref2VA) ready to paste into H3. Use when the user provides a video file and a reference image and asks to feed H3, swap the character, recreate the same motion path, or generate a reusable script for a known choreography. Triggers: "反推视频", "把图1替换进去", "我会输入视频1和图1进入h3", "reverse this video for h3", "extract h3 prompt from this clip". Always end by saving the final prompt as a .md file alongside the input video and printing the ready-to-paste text block.
---

# Video → H3 Prompt

End-to-end pipeline that turns a video file into a ready-to-paste H3 Ref2VA (or I2VA/FL2VA/L2VA/T2VA) prompt. Companion to `h3-prompt-writing`; reuse that skill's six-section template and shot syntax.

## Workflow

1. Probe the video with `ffprobe` and record duration, resolution, frame rate, codec, and color space.
2. Choose a sampling interval based on duration and complexity; extract frames at that interval.
3. View frames in batches of 6 to map the motion arc, locate cut points, and write a shot-by-shot table.
4. Probe the audio with `volumedetect` to classify it as music / dialogue / ambience.
5. Pick the H3 mode (usually Ref2VA) based on what assets the user is providing.
6. Assemble the six-section prompt per `h3-prompt-writing` skill, fill all cut times, define every `<Subject>` / `<Picture>` / `<Video>` / `<Audio>` reference, and keep label semantics consistent across all six sections.
7. Run the self-check, save the prompt as `<video-stem>_ref2va_prompt.md` next to the input, and print the final `text` block.

## Step 1 — Probe

```bash
ffprobe -v error -show_format -show_streams -of json "<video.mp4>"
```

Capture six fields that drive every later decision:

| Field | Why it matters |
|---|---|
| `duration` | Final duration written into H3 as `S.SS` (two decimals) |
| `width × height` | Aspect ratio (portrait 9:16 vs landscape) drives shot framing |
| `r_frame_rate` | 30 vs 60 fps changes how "snappy" motion feels |
| `nb_frames` | Sanity check on duration × fps |
| `codec_name` | h264 vs hevc affects ffmpeg compatibility |
| `has_b_frames` | If `> 0`, use `-noaccurate_seek` for cleaner frame extraction |

## Step 2 — Frame Sampling

Pick the interval by duration and complexity:

| Duration | Interval | Frames | When |
|---|---|---|---|
| < 5 s | 0.2 s | ~25 | Single expression / single action |
| 5–10 s | 0.3–0.4 s | 17–34 | Emote loop, dance clip |
| 10–15 s | 0.15–0.2 s | 50–75 | Multi-segment vlog, complex choreography |
| > 15 s | 0.2 s + targeted re-extracts at transitions | 70+ | Long-form |

Always downscale and silence logs:

```bash
for ($i=0; $i -le N; $i++) { 
  $t = "{0:F3}" -f ($i*$interval); 
  ffmpeg -y -ss $t -i "<video>" -frames:v 1 -vf "scale=iw/2:-1" -q:v 3 "out_$i.jpg" -loglevel error 
}
```

If the first pass misses transition details (e.g. an emote starts earlier than expected), **re-extract at half the interval** around the gap. This is the single biggest quality lever.

## Step 3 — Map the Motion Arc

View frames in batches of 6 (one batch per `view_image` call). For each key frame write a three-field note:

```
[t] 00:02.000
[s] Shot 1 / emote #3 / choreo segment 2
[m] Looks up at camera, eyes widen, lips push into pout
```

### Cut vs continuous motion

| Signal | Meaning |
|---|---|
| Frame-to-frame composition jump (angle or focal length) | **Cut** |
| Composition stable, only the subject moves | Continuous action |
| Composition shifts smoothly (push / pull / pan) | Camera move (not a cut) |
| File size drop on a frame | Possible cut — verify visually |

A video with no detected cuts is a single `Shot 1`; describe every emote inside that one block with `At 00:XX.XXX <Subject 1> ...` sentences.

## Step 4 — Audio Classification

```bash
ffmpeg -y -i "<video>" -vn -ac 1 -ar 8000 -f wav out.wav
ffmpeg -i out.wav -af "volumedetect" -f null - 2>&1 | grep volume
```

| mean_volume | max_volume | Likely content |
|---|---|---|
| -10 to -15 dB | -1 to -3 dB | Full music (dance-pop / electronic) |
| -16 to -20 dB | -5 to -8 dB | Music + ambience (live show, restaurant vlog) |
| -20 to -30 dB | -10 to -15 dB | Pure ambience, dialogue, light music |
| < -30 dB | < -15 dB | Near-silent |

This reading drives whether `non_diegetic_music` needs a real track description, a generic placeholder, or `N/A`.

## Step 5 — Pick the H3 Mode

| Inputs the user will feed H3 | Mode |
|---|---|
| Video only | T2VA (build timeline from motion arc) |
| Video + first-frame image | I2VA |
| Video + first and last frame | FL2VA |
| Video + last frame only | L2VA |
| Video + 1+ reference images (and/or audio) | **Ref2VA** (most common) |

If the user says "I'll feed a universal Picture 1 for both character and scene", pick **Ref2VA** and define `<Picture 1>` as a *universal visual anchor* (see reference template).

## Step 6 — Assemble the Prompt

Reuse the six-section template from `h3-prompt-writing/SKILL.md` + `references/ref-en.txt`:

1. `subject_definitions` — `<Subject N>`, `<Picture N>`, `<Video N>`, `<Audio N>`
2. `summary` — task type tag + one-line action summary
3. `retention_analysis` — per-reference retention status
4. `detailed_description` — shot-by-shot with six elements per shot
5. `overall_soundscape` — ambience, physical sounds, non-verbal human sounds
6. `non_diegetic_music` — audience-only score or `N/A`

### Per-shot six elements (mandatory)

| Element | Example phrasing |
|---|---|
| Composition | `a wide shot` / `a medium close-up` / `a tight close-up` |
| Subject appearance + position | `<Subject 1>, the young woman with ..., sits centered` |
| Environment + lighting | `inside an ornate hall with ... soft daylight` |
| Action + state change | `She extends both arms...` / `She whips her head around...` |
| Camera movement | `The camera pushes in with small amplitude at slow speed` |
| Current sound | `a soft whoosh` / `white-dot eyes widening` |

### Cut syntax (multi-shot only)

```
[Shot 1]                            <- no timestamp
[Shot 2] At 00:03.200, ...          <- strictly increasing, two decimals, in [0, duration]
[Shot 3] At 00:06.400, ...
```

Fixed transition verbs: `the camera cuts to` / `the shot transitions to` / `the view shifts to` / `a hard cut reveals`.

### Single-shot videos

No `[Shot 2]` ever starts. Put every emote inside `[Shot 1]` connected by `At 00:XX.XXX` clauses.

## Step 7 — Self-Check and Output

Run this checklist before printing the final block:

```
✅ Duration S.SS matches ffprobe within ±0.02
✅ Shot count = cut count + 1
✅ Every cut time in [0, duration] and strictly increasing
✅ Same <Subject 1> / <Picture 1> / <Video 1> semantics across all six sections
✅ <Subject 1> appearance defined exactly once (in subject_definitions)
✅ Each Shot in detailed_description contains all six elements
✅ Ambience / SFX → overall_soundscape; audience music → non_diegetic_music; no crossover
✅ Dialogue / lyrics wrapped in <d>[Language] text</d>
✅ No copyrighted lyrics, dialogue, or trademarked names reproduced
```

Then:

1. Save the full write-up (input table + motion arc + audio reading + final prompt block) to `<video-stem>_ref2va_prompt.md` in the same folder as the video.
2. Print the final `text` block in the response so the user can paste it directly into H3.

## Cross-Shot Continuity Rule

Every new `[Shot N]` must open by stating the subject's last position / pose from the previous shot, so H3 does not lose spatial continuity at the cut.

## "Universal Picture 1" Variant

When the user says their reference image defines both character and scene, override the standard `<Picture 1>` definition:

```
<Picture 1> is the universal visual anchor for the entire target video. It defines not only <Subject 1>'s appearance, costume, hair, and accessories, but also the scene's compositional layout, camera angle, lighting direction, color palette, tableware placement, and background environment. Whenever the target video needs to decide what the room, the table, the dishes, the window light, the wall tones, or the surrounding atmosphere look like, it must follow <Picture 1>.
```

Mark retention as `(governs the entire visual look)` and describe the shot opening as `framed and lit as defined by <Picture 1>`.

## Bundled Resources

- `references/shot-syntax.md` — Ref2VA six-section skeleton + cut syntax + per-shot six-element checklist
- `references/audio-heuristics.md` — volumedetect reading table + matching `non_diegetic_music` description recipes
- `references/ffmpeg-cheatsheet.md` — probe, extract, audio dump, downscale commands
