# video-to-h3-prompt

Forensically reverse-engineer a reference video into a complete, ready-to-paste **MiniMax H3** prompt. Not "watch a few frames and write a vibe" — an evidence pipeline that reconstructs the causal event chain, triages the film type into the correct camera state machine, reconciles cuts against music onsets, separates live action / camera / edit-effects / sound layers, and compiles the exact H3 fields for every input mode.

## What it does

- **Dense frame forensics** — sparse contact sheet builds the skeleton; 4–8fps dense extraction on ambiguous windows adjudicates between competing plot/camera hypotheses; full-res key frames and timecode-burned sheets for final confirmation.
- **Film-type → camera state-machine triage** — classifies every clip as (A) continuous take, (B) editorial snap-lock (`HARD LOCK ↔ INSTANT BURST`, two mutually exclusive states) or (C) multi-shot montage (named camera setups + cut discipline), so you never suppress real cuts with a lock/burst template or let a static hero frame drift.
- **Music onset / card-point sync** — beyond the 0.5s RMS envelope, `onset_probe.py` detects graded note onsets (numpy+scipy only, no librosa) and reconciles every cut / freeze / impact / volley / aura-burst to a strong accent; distinguishes fixed tempo from free-tempo rubato (no fake BPM), and filters out muzzle-flash/explosion false cuts.
- **Causal event-chain reconstruction** — trigger → action → reaction for every state change; off-camera actors (a sleeve, a hand, a scooter fairing) are tracked as real agents instead of ignored clutter.
- **Edit-layer separation** — freeze-frame gags, white flashes, manga overlays, RGB-glitch and energy-burst effects and their post-SFX go to `editing` / `overall_soundscape`, never mistaken for on-set action.
- **Multi-image locking & long-clip segmentation** — `<Picture 1>` locks character 1, `<Picture 2>` locks character 2 (identity+costume only; environment/props stay text, zero appearance prose); clips over ~15s split into segments with per-segment clocks, non-restarting music, and hand-off states.
- **All five H3 modes** — T2VA / I2VA / FL2VA / L2VA use the 14-field template; Ref2VA uses the six-section template with `<Subject>/<Picture>/<Video>/<Audio>` label discipline.
- **Coser / character replacement without plot change** — swap appearance only, run action-compatibility checks, tier prop inclusion, translate anime designs into real-human cosplay, and emit a replacement table.

## The six reusable checks

1. Decide continuous-move vs discrete-cut first; dense-sample transitions at ≥8fps and look for the "motion → fully still" step.
2. Reconcile the timeline to audio: does each cut/freeze/impact land on an onset? Yes → editorial/card-point editing; only then consider free camera timing.
3. With a reference image, never describe appearance — the image locks looks; prose carries only camera / timing / state machine / environment & props.
4. Write static and burst as two mutually exclusive states; repeat the "no slow-mo / drift / residual motion" bans throughout static sections.
5. On a sideways frame, suspect camera Roll first — compare the horizon against the body before declaring the character lying/turning.
6. Impacts must be countable, not mushy: name each hit (positional / push / rotational), state "not continuous vibration", and move only the camera, never deform the person.

## Why dense reconstruction is possible (and why first passes fail)

Reverse-engineering is a **one-to-many inverse problem**: different scripts can produce near-identical frames. Sparse sampling plus a "most common plot" prior silently fills the gaps — e.g. reading a helmet-grab redirect as two girls spraying each other, missing a 3–5-frame off-camera hand, or mistaking a camera Roll for a character lying down. The skill keeps multiple candidate plots alive at the skeleton stage and uses dense frames, the state-machine triage and music onsets as *discriminative* evidence. A user-supplied plot is treated as an actor list / intent chain that shrinks the hypothesis space — then verified frame by frame, never blindly accepted or rejected.

## Layout

```
video-to-h3-prompt/
├── SKILL.md                          # main workflow: 5 channels, 6 checks, 10-step SOP, state-machine triage
├── README.md
├── LICENSE                           # MIT
├── agents/openai.yaml                # agent metadata
├── references/
│   ├── 01-forensics-commands.md      # sampling/grid/spectrogram/RMS/onset/scene-cut/timecode + reconciliation matrix
│   ├── 02-h3-field-mapping.md        # observation -> 14 fields, timestamp rules, EN assembly skeleton
│   ├── 03-edit-effects.md            # freeze-frame 4-tuple, white-flash & manga & glitch recipes, post-SFX
│   ├── 04-coser-replacement.md       # skin-only swap SOP, action compatibility, prop tiers, table
│   ├── 05-pitfalls-checklist.md      # 16 traps, six checks, cognitive + delivery checklists
│   ├── 06-film-type-and-state-machine.md  # A/B/C triage, LOCK↔BURST, named setups, countable impacts, Roll, anti-hallucination skeleton
│   ├── 07-onset-and-card-points.md   # onset detection, rubato vs fixed tempo, card-point table, false-cut filtering, timecode grids
│   ├── 08-multi-image-and-segmentation.md # multi-image all-purpose lock, zero-appearance rule, >15s splitting, hand-off
│   ├── shot-syntax.md                # Ref2VA six-section skeleton, cut syntax, camera vocabulary
│   ├── audio-heuristics.md           # spectrogram/RMS/BPM + volumedetect -> music recipe table
│   └── ffmpeg-cheatsheet.md          # PowerShell-first ffprobe/ffmpeg command reference
└── scripts/
    ├── forensic_probe.ps1            # one-click forensics on Windows (param: -Video), incl. onset
    ├── forensic_probe.sh             # one-click forensics on macOS/Linux, incl. onset
    ├── audio_probe.py                # RMS envelope + band energy + BPM credibility (numpy; librosa optional)
    └── onset_probe.py                # graded onset/card-point detection + phrase contour (numpy+scipy, no librosa)
```

## Requirements

- `ffmpeg` / `ffprobe` on PATH.
- Python 3 with `numpy` for `audio_probe.py`; `onset_probe.py` additionally needs `scipy`. `librosa` is optional throughout — onset analysis works without it (notably on Python versions such as 3.14 where librosa has no wheel yet).

## Quick start

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/forensic_probe.ps1 -Video ".\clip.mp4" -OutDir forensic_out
```

macOS / Linux:

```bash
bash scripts/forensic_probe.sh "clip.mp4" forensic_out
```

Then follow `SKILL.md`: read `grid_*.jpg`, dense-extract every ambiguous window, triage the film type (`references/06`), reconcile strong onsets in `onsets.txt` with cuts/hits (`references/07`), choose the H3 mode (split into ≤15s segments per `references/08` if long), and assemble the prompt. The agent prints the ready-to-paste English block in the reply (and saves a `.md` only if file delivery is requested).

## Trigger phrases

`反推视频` · `视频转H3提示词` · `卡点时间 / 节奏分析` · `多镜头分镜运镜` · `分段生成` · `把图1替换进去 / 只换角色不改剧情` · `reverse this video for h3` · `extract h3 prompt from this clip`.

## Companion skills

Pairs with an H3 prompt-writing / field-reference skill (e.g. `h3-prompt-master`): this skill produces the evidence, causal chain, state-machine decision and card points; the writer supplies field definitions. Output prompts are English; analysis can stay in the user's language.

## License

MIT — see [LICENSE](LICENSE).
