# video-to-h3-prompt

Forensically reverse-engineer a reference video into a complete, ready-to-paste **MiniMax H3** prompt. Not "watch a few frames and write a vibe" — a five-channel evidence pipeline that reconstructs the causal event chain, separates live action / camera / edit-effects / sound layers, and compiles the exact H3 fields for every input mode.

## What it does

- **Dense frame forensics** — sparse contact sheet builds the skeleton; 4–8fps dense extraction on ambiguous windows adjudicates between competing plot hypotheses; full-res key frames for final confirmation.
- **Audio cross-validation** — spectrogram (music vs field audio), 0.5s RMS envelope (every energy peak must have a picture cause), and a BPM false-detection guard (random transients must not be mistaken for a soundtrack).
- **Causal event-chain reconstruction** — trigger → action → reaction for every state change; off-camera actors (a sleeve, a hand, a scooter fairing) are tracked as real agents instead of ignored clutter.
- **Edit-layer separation** — freeze-frame gags, white flashes, manga overlays (concentration lines / screentone / onomatopoeia) and their post-SFX are written into `editing` / `overall_soundscape`, never mistaken for on-set action.
- **All five H3 modes** — T2VA / I2VA / FL2VA / L2VA use the 14-field template; Ref2VA uses the six-section template with `<Subject>/<Picture>/<Video>/<Audio>` label discipline.
- **Coser / character replacement without plot change** — swap appearance only, run action-compatibility checks, tier prop inclusion, translate anime designs into real-human cosplay, and emit a replacement table.

## Why dense reconstruction is possible (and why first passes fail)

Reverse-engineering is a **one-to-many inverse problem**: different scripts can produce near-identical frames. Sparse sampling plus a "most common plot" prior silently fills the gaps — e.g. reading a helmet-grab redirect as two girls spraying each other, or missing a 3–5-frame off-camera hand. The skill keeps multiple candidate plots alive at the skeleton stage and uses dense frames + audio peaks as *discriminative* evidence. A user-supplied plot is treated as an actor list / intent chain that shrinks the hypothesis space — then verified frame by frame, never blindly accepted or rejected.

## Layout

```
video-to-h3-prompt/
├── SKILL.md                          # main workflow: 5 channels, 9-step SOP, mode selection
├── README.md
├── LICENSE                           # MIT
├── agents/openai.yaml                # agent metadata
├── references/
│   ├── 01-forensics-commands.md      # sampling / grid / spectrogram / RMS / BPM + reconciliation matrix
│   ├── 02-h3-field-mapping.md        # observation -> 14 fields, timestamp rules, EN assembly skeleton
│   ├── 03-edit-effects.md            # freeze-frame 4-tuple, white-flash & manga recipes, post-SFX
│   ├── 04-coser-replacement.md       # skin-only swap SOP, action compatibility, prop tiers, table
│   ├── 05-pitfalls-checklist.md      # top-10 traps + delivery checklist
│   ├── shot-syntax.md                # Ref2VA six-section skeleton, cut syntax, camera vocabulary
│   ├── audio-heuristics.md           # spectrogram/RMS/BPM + volumedetect -> music recipe table
│   └── ffmpeg-cheatsheet.md          # PowerShell-first ffprobe/ffmpeg command reference
└── scripts/
    ├── forensic_probe.ps1            # one-click forensics on Windows (param: -Video)
    ├── forensic_probe.sh             # one-click forensics on macOS/Linux
    └── audio_probe.py                # RMS envelope + band energy + BPM credibility (numpy; librosa optional)
```

## Requirements

- `ffmpeg` / `ffprobe` on PATH.
- Python 3 with `numpy` for `audio_probe.py`; `librosa` is optional (without it the script still prints RMS and band energy and simply skips tempo estimation).

## Quick start

Windows:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/forensic_probe.ps1 -Video ".\clip.mp4" -OutDir forensic_out
```

macOS / Linux:

```bash
bash scripts/forensic_probe.sh "clip.mp4" forensic_out
```

Then follow `SKILL.md`: read `forensic_out/grid_*.jpg`, dense-extract every ambiguous window, reconcile RMS peaks with frames, choose the H3 mode, and assemble the prompt. The agent saves `<video-stem>_h3_prompt.md` next to the video and prints the ready-to-paste block.

## Trigger phrases

`反推视频` · `视频转H3提示词` · `把图1替换进去 / 只换角色不改剧情` · `reverse this video for h3` · `extract h3 prompt from this clip`.

## Companion skills

Pairs with an H3 prompt-writing / field-reference skill: this skill produces the evidence and causal chain; the writer supplies field definitions. Output prompts are English; analysis can stay in the user's language.

## License

MIT — see [LICENSE](LICENSE).
