# 02 — 观察 → H3 字段映射与组装骨架（T2VA / I2VA / FL2VA / L2VA）

> Ref2VA 全参考模式走另一套六段式，见 `shot-syntax.md`。本文件用于无参考图或仅首/尾帧参考的 14 字段式。

## 1. 字段顺序（顺序不可换；✓ 必填，○ 条件必填）

| # | 字段 | 必选 | 装什么（观察来源） |
|---|---|---|---|
| 1 | `subject_definitions` | ✓ | 每个可见/画外角色：年龄感、发型面部、全套服装、鞋袜手套、手持剧情道具、静态佩戴道具、职能；画幅 |
| 2 | `environment_definition` | ○ | 空间、建筑、地面、背景物件、静态载具、氛围与排除项（I2VA 首帧锁定时省略） |
| 3 | `lighting_definition` | ○ | 主光方向/软硬/色温、环境补光、阴影、湿反/高光、噪点、恒常性（I2VA 首帧锁定时省略） |
| 4 | `visual_anchor` | I2VA | 仅首帧锚定模式 |
| 5 | `audio` | 复用音频时 | supplied audio 标 fully_copy |
| 6 | `integrated_multimodal_description` | ✓ | 一句话结构前提 + N-beat payoff + [Shot 1] 开场态（无时间戳）+ 严格递增时间戳事件链，动作处内嵌同期声 |
| 7 | `camera_direction` | ✓ | 机位/视角/景别/基线晃动；每次运镜类型+幅度+速度+**动机**；禁用运镜清单 |
| 8 | `editing` | ✓ | 切换策略；每个定格/转场/特效的入点、时长、叠加配方、回到实拍方式；N-beat 节奏 |
| 9 | `performance` | ✓ | 逐角色情绪弧、反差、表情约束、夸张只允许出现在哪 |
| 10 | `body_mechanics` | ✓ | 蓄力规则、力传导链、喝/喷/被打动力学、双脚扎根 |
| 11 | `costume_hair_physics` | ○ | 发型/面料/眼镜/裙摆/面罩的滞后摆动、湿身演化、settle |
| 12 | `negative_constraints` | ✓ | 聚焦排除：人数/道具/风格化/运镜/剪辑/文字/漂移 |
| 13 | `overall_soundscape` | ✓ | 环境底噪 + 按时间同期声清单 + 定格特效音 + 录音质感 |
| 14 | `non_diegetic_music` | ✓ | fully_copy ／目标音乐设计 ／explicit silence 三选一 |

## 2. 时间戳纪律

1. `[Shot 1]` 永远无时间戳，只写开场状态。
2. 其后严格递增；14 字段式可用一位小数 `[00:09.8]`，Ref2VA 用两位 `00:09.80`。
3. 只在真实状态变化处打时间戳：动作发起、受力、镜头动机起点、声音事件、剪辑点。禁止抒情式时间戳。
4. 事件写法：`[时间] 触发 → 发起 → 扩张 → 重音 → 回收`，句中内嵌同期声（"with a small plastic click"、"audible pouring"）。
5. 相邻事件用残余动量衔接，禁止中性姿势复位。

## 3. 英文组装骨架（直接套）

```text
subject_definitions: <Subject 1> ... ; <Subject 2> ... ; <Subject N / off-camera actor> is NEVER fully shown: [可见部位/控制物件/每次入画职能]. Vertical/Horizontal X:Y.

environment_definition: [space, architecture, ground, background objects, parked static props, atmosphere, explicit exclusions].

lighting_definition: [key direction+quality+color temp, ambient/fill, shadow, wet/specular behavior, grain, constancy].

integrated_multimodal_description: [one sentence: structural premise + N-beat payoff + material rule]. [Shot 1] [opening state, NO timestamp, framing + every subject state + foreground/background anchors]. [00:00.5] trigger→action→expansion→accent→recovery with embedded diegetic sound. ... [final timestamp] ending state.

camera_direction: [POV/holder, framing, angle, baseline shake]; [range] movement type at [small/medium/large] amplitude, [slow/medium/fast] speed, motivated by [body/event]; ... ; explicit no-orbit/no-zoom list.

editing: [cut policy]; each deliberate effect: in-point, duration, overlay recipe, snap-back; N-beat rhythm; what is NOT allowed.

performance: [per-character arc]; contrast design; where exaggeration is allowed/forbidden; no posed faces / constant smiling / lip-sync as applicable.

body_mechanics: [wind-up before every release]; force transmission chain; drinking kinetics raise-arm→tilt-back→swallow→lower; grounded feet, no floating.

costume_hair_physics: [per-character hair lag & wet evolution]; [fabric weight, darken-and-cling]; [glasses slide/fog; visor resistance]; nothing animates independently.

negative_constraints: [focused list: no extra people, no added props beyond X, no costume swap, no style drift, no forbidden camera, no ordinary cuts, no subtitles/watermark, no blood, no effect residue, no freeze outside beats, no identity change].

overall_soundscape: [ambient bed]; ordered diegetic cues "at X.Xs ..."; per-freeze post-SFX; unpolished field-recording note.

non_diegetic_music: [fully_copy <Audio N>.] / [target music spec] / [No non-diegetic music. Explicit silence of the music layer throughout; ...].
```

## 4. 三层声音分离速查

| 声音类型 | 例子 | 唯一允许字段 |
|---|---|---|
| 动作同期声 | 吞咽、面罩咔哒、喷水、呛咳、脚步 | 内嵌进 `integrated_multimodal_description` 对应动作句 |
| 环境/特效总览 | 夜巷底噪、怠速、风、定格特效音序列 | `overall_soundscape` |
| 音乐层 | BGM、配乐、歌曲 | 只在 `non_diegetic_music`；无乐则 explicit silence / N/A |

## 5. I2VA / FL2VA / L2VA 调整

- **I2VA 首帧锚定**：开头加 `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`；加 `visual_anchor`；省略 environment/lighting 文本字段；subject 以图为唯一视觉权威，只留极短身份锚点（轮廓+运动结构+整体色调）。
- **FL2VA**：补 first-frame state → observable intermediate changes → 收敛到尾帧的连续路径，倾向单镜头。
- **L2VA**：从给定尾帧反推合理开场状态，让动作/物体/构图逐步收敛到尾帧。

## 6. 目标音乐设计字段（确需配乐时的十项写法）

`genre / BPM / key / instrumentation architecture / musical structure / dynamics arc / synchronization / vocals / production`，作为创作目标一次性写进 `non_diegetic_music`，音乐全程连续不中断、不分段割裂；不得把音乐写进画面描述。
