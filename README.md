# Video → H3 Prompt

End-to-end pipeline that turns a video file into a ready-to-paste **MiniMax H3** generation prompt (T2VA / I2VA / FL2VA / L2VA / Ref2VA).

Companion to [`h3-prompt-writing`](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing); reuse that skill's six-section template and shot syntax.

## What this skill does

1. Probes a video with `ffprobe` to capture duration, resolution, frame rate, codec, and color space.
2. Extracts frames at a duration-aware interval (0.15 s – 0.4 s).
3. Maps the motion arc shot-by-shot in batches of six.
4. Classifies the audio track with `volumedetect`.
5. Picks the right H3 mode (usually **Ref2VA**).
6. Assembles the six-section prompt with per-shot six-element coverage.
7. Runs a 9-point self-check, saves the result next to the input, and prints the ready-to-paste `text` block.

## Repository layout

```
video-to-h3-prompt/
├── SKILL.md                              # Workflow + invocation triggers
├── README.md                             # This file
├── LICENSE                               # MIT
├── agents/
│   └── openai.yaml                       # Codex Chat UI metadata
└── references/
    ├── shot-syntax.md                    # Ref2VA six-section skeleton + cut syntax
    ├── audio-heuristics.md               # volumedetect reading + music recipes
    └── ffmpeg-cheatsheet.md              # Probe, extract, dump, diff commands
```

## Trigger phrases

The skill loads automatically when the user writes any of:

- 反推下视频 + 用 H3 把图1替换进去
- 我会输入视频1和图1进入h3
- reverse this video for h3
- extract h3 prompt from this clip
- generate a reusable script for a known choreography

## How to install

Copy this folder into one of Codex's skill roots:

| Codex flavor | Path |
|---|---|
| Personal Codex | `~/.codex/skills/video-to-h3-prompt/` |
| Codex CLI project | `.codex/skills/video-to-h3-prompt/` |

Or symlink it. After the copy, restart Codex so it picks up the new `SKILL.md`.

## How to invoke

```
Use $video-to-h3-prompt to reverse-engineer <video.mp4> with <reference-image.png> into a MiniMax H3 generation prompt.
```

Or, in natural language:

> "反推下这个视频,用 H3 把图1 替换进去,我会输入视频1和图1进入h3"

The skill will:

1. Probe the video and audio.
2. Extract frames and map the motion arc.
3. Assemble the six-section H3 prompt.
4. Save `<video-stem>_ref2va_prompt.md` next to the input.
5. Print the final `text` block in the chat.

## Companion skill

- [`h3-prompt-writing`](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing) — Six-section template and shot syntax that this skill reuses.

## License

MIT — see [LICENSE](./LICENSE).
