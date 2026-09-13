# H3 Ref2VA Shot Syntax Reference

Concise skeleton for the `detailed_description` section. Reuse this when filling out any Ref2VA prompt (video + one or more reference images/videos/audio). For T2VA / I2VA / FL2VA / L2VA use the 14-field template in `02-h3-field-mapping.md`. The forensic workflow (dense sampling, audio cross-validation, causal event chain, freeze-frame gags) that *produces* the content lives in `SKILL.md` and `01-forensics-commands.md`; this file governs how that content is written into Ref2VA fields.

## Six-Section Skeleton

```text
subject_definitions:
<Subject 1> is the <identity> in <Picture 1>, with <appearance list>.
<Video 1> is the source video that defines the target video's shot structure, motion path, and pacing: <one-line source description>. <Video 1> is used only for temporal structure; <what is discarded>.

summary:
[<task-tag> + <asset-tag>] <one-paragraph task summary using <Subject 1>, <Picture 1>, <Video 1>>.

retention_analysis:
<Subject 1> (appears in [Shot X], ...): <fully_preserved | partially_preserved | transferred | reused> - <what is kept>.
<Video 1> (governs the whole video): reference - <what temporal/structural cues are kept>; <what is discarded>.
[add a row for every other reference]

detailed_description:
The target video uses <one-line style description>.

[Shot 1] <Composition with 6 elements (see below)>.

[Shot 2] At 00:XX.XXX, <transition verb> <rest of shot with 6 elements>.

overall_soundscape:
<ambience + physical SFX + non-verbal human sounds across the whole video; freeze-frame post-SFX belongs here>.

non_diegetic_music:
<audience-only score: instrumentation + tempo + dynamics> | N/A
```

## Per-Shot Six Elements

Every `[Shot N]` block must cover all six. Missing one is the most common reason H3 hallucinates.

| # | Element | Template |
|---|---|---|
| 1 | Composition | `a wide shot` / `a medium close-up` / `a tight close-up` / `an over-the-shoulder shot` |
| 2 | Subject appearance + position | `<Subject 1>, the <identity> with <key features>, <position phrase>` |
| 3 | Environment + lighting | `<setting> with <light source + quality + direction>` |
| 4 | Action + state change | `<Subject 1> <present-tense action> ... <visible state change>` (trigger → action → result, diegetic sound embedded) |
| 5 | Camera movement | `The camera pushes in with small amplitude at slow speed` / `holds steady` / `pulls out` |
| 6 | Current sound | `<short onomatopoeic or descriptive cue>` |

## Cut Syntax (Multi-Shot Only)

```
[Shot 1]                            <- no timestamp
[Shot 2] At 00:03.200, ...          <- first cut, strictly increasing
[Shot 3] At 00:06.400, ...
[Shot N] At 00:11.700, ...
```

Rules:

- Always two decimals, period separator.
- `0.00` is forbidden on `[Shot 1]` — `[Shot 1]` is the only shot without a timestamp.
- Each cut time must be **strictly greater than the previous** and **less than or equal to `duration`**.
- Final shot ends implicitly at `duration`; no need to repeat it.
- A freeze-frame gag is NOT a cut: keep it inside the same shot as a `FREEZE-FRAME GAG n` event with in-point, duration and snap-back (see `03-edit-effects.md`).

## Transition Verb Library

Pick one per cut; do not mix:

| Verb | When to use |
|---|---|
| `the camera cuts to` | Plain hard cut (default) |
| `the shot transitions to` | Soft cut, fade, dissolve |
| `the view shifts to` | Same camera, change in focal length or angle |
| `a hard cut reveals` | Hard cut that lands on a deliberately different scene state |
| `the angle switches to` | Quick angle flip with subject continuity |

## Single-Shot Videos (No Cuts)

```
[Shot 1] <initial composition>.

<Subject 1> <first action>. At 00:01.200 <Subject 1> <next action>.
At 00:02.500 <Subject 1> <next action>. ...
```

Tie every emote or beat with `At 00:XX.XXX` clauses inside the single `[Shot 1]` block. Most prank/UGC reversals are single-shot with freeze gags, not multi-cut.

## Camera Movement Vocabulary

- `the camera pushes in with small amplitude at slow speed` — gentle forward dolly
- `the camera pushes in with medium amplitude at moderate speed` — noticeable dolly
- `the camera pulls out with small amplitude at slow speed` — gentle back dolly
- `the camera trucks right with small amplitude at slow speed` — lateral slide
- `the camera holds steady` — locked-off
- `the camera pans right with small amplitude at slow speed` — horizontal rotation
- `the camera tilts down/up with small amplitude at medium speed` — vertical rotation
- handheld first-person: `subtle organic handheld shake throughout, never gimbal-smooth`

Always quantify amplitude (none / small / medium / large) and speed (slow / moderate / fast), and state the motivation for every move.

## Subject Opening Pattern

For continuity at every cut, open the new shot by echoing the subject's last known position:

```
[Shot 2] At 00:03.200, the camera cuts to a tight close-up of <Subject 1>,
who remains seated at the table from Shot 1, the bowl and spoon still in frame.
```

## Reference Label Discipline

Pick the right tag for each piece of reusable content:

| Label | Used for |
|---|---|
| `<Subject N>` | Reusable visible content (person, animal, object, scene, style, action) |
| `<Picture N>` | An image used as a frame anchor, keyframe, last frame, or composition reference |
| `<Video N>` | A reference video supplying editing source, continuation, or whole-video structure |
| `<Audio N>` | An audio signal that is copied or referenced for voice / music / ambience |

Once assigned, the label must mean the **same thing** in every section. Renaming, aliasing, or implicit reuse is a hard error.

## "Universal Picture 1" Variant

When one reference image defines both character and scene, use:

```
<Picture 1> is the universal visual anchor for the entire target video. It defines not only <Subject 1>'s appearance, costume, hair, and accessories, but also the scene's compositional layout, camera angle, lighting direction, color palette, prop placement, and background environment. Whenever the target video needs to decide what the room, props, window light, wall tones, or surrounding atmosphere look like, it must follow <Picture 1>.
```

Mark retention as `(governs the entire visual look)` and open shots as `framed and lit as defined by <Picture 1>`.
