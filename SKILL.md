---
name: video-to-h3-prompt
description: Reverse-engineer a reference video into a complete, ready-to-paste MiniMax H3 prompt (T2VA / I2VA / FL2VA / L2VA / Ref2VA) through dense frame sampling, audio-visual cross-validation, causal event-chain reconstruction and edit-layer separation. Covers prank/UGC/narrative/dance clips, freeze-frame and manga gags, off-camera actors, and coser/character replacement without plot change. Use when the user provides a video (and optional reference image) and asks to 反推视频 / 把图1替换进去 / 视频转H3提示词 / reverse this video for h3 / extract h3 prompt from this clip / 只换角色不改剧情. Always end by saving the final prompt as a .md file alongside the input video and printing the ready-to-paste text block.
---

# Video → H3 Prompt（视频反推 MiniMax H3 提示词）

End-to-end pipeline that turns a video file into a ready-to-paste H3 prompt. It is **not** "watch a few frames and write an atmosphere blurb" — it is a forensic workflow: `取证 → 交叉验证 → 因果重建 → 选模式 → 字段落点 → 自检交付`. Companion to `h3-prompt-writing` / `h3-prompt-master`; reuse their field templates and shot syntax.

## 0. 输入与输出

- **输入**：参考视频（可选：参考图、用户剧情说明、角色/coser 替换要求）。
- **输出三件套**：
  1. 中文反推报告（片型 / 场景 / 人物 / 因果动作链 / 剪辑特效 / 声音结论 / 推测项）；
  2. 字段完整、时间戳精确、可直接粘贴的**英文** H3 prompt；
  3. 换角色任务必须附「替换对照表」。
- 收尾动作（硬性）：把完整结果存为 `<video-stem>_h3_prompt.md` 放在视频同目录，并在回复里打印可直接粘贴的最终文本块。

## 1. 核心原理：细颗粒度为什么可能（五个证据通道）

细度来自五条独立证据链互相锁死，而不是"看得更用力"：

1. **密度采样通道**：全片稀疏网格建骨架；转折区间 4fps（必要时 8fps）密帧；关键瞬间原分辨率单帧终核。只持续 3–5 帧的动作（如一只手掰头盔）在稀疏采样下会彻底消失——这是把"被掰头误伤"误判成"自己喷过去"的根源。
2. **音频取证通道**：频谱图判有无 BGM；0.5s 粒度 RMS 包络找能量峰；每个能量峰必须在画面里找到成因。
3. **因果链通道**：每个状态变化回答 trigger → action → reaction（谁先动、力朝哪、结果落哪）。罗列画面 = 摆拍；重建因果 = 可执行事件链。
4. **状态表通道**：逐帧维护道具/身体状态（面罩开合、杯瓶位置、头发干湿、液体方向颜色、谁的手在画内），状态翻转点就是时间戳锚点。
5. **分层通道**：现场动作层 / 运镜层 / 后期剪辑特效层 / 声音层分离。定格、白闪、漫画线、拟声字、特效音属于后期层，绝不写成现场动作。

### 交叉验证铁律
任何断言至少被两个通道支持才写成事实；单通道支持标「推测」；通道矛盾时以物理证据为准并记录证伪（例：算法报 117 BPM，但 onset std/mean>0.8 且频谱无 kick 网格 → BPM 误检，判无 BGM）。

### 反推是一对多的逆问题
脚本→画面是多对一映射：不同脚本可以拍出几乎相同的画面（自呛 vs 被掰头误伤）。因此画面→脚本欠定，**稀疏采样后必须并列多个候选剧情，用密帧做判别性取证**，而不是用最常见的剧情模板直接填满。用户给的剧情不是新像素，而是行动者清单 / 意图链 / 剪辑意图，作用是收敛解空间；收到后必须回帧序列逐条验证，不盲信、不拒绝。

## 2. 硬性原则

- H3 可执行内容一律**英文**；对用户的分析讨论用用户语言。
- `[Shot 1]` 不带时间戳；其后时间戳严格递增（Ref2VA 用两位小数 `00:03.200`，14 字段式可用一位），只标真实状态变化。
- 三层声音分离：动作同期声内嵌动作句；环境/特效音进 `overall_soundscape`；音乐只进 `non_diegetic_music`，原片无 BGM 写 explicit silence / `N/A`，禁止脑补配乐。
- **有目的运动的非身体物体必有控制者**：伸入画面的手、袖子、车头、杯瓶归并到一个画外行动者，不当杂物。第一人称拍摄者默认是潜在剧中行动者，不得先验当成透明机位。
- 每个视觉结果必须有物理路径（水从哪含、沿什么方向、喷在透明还是镀膜面罩）；路径不通回查帧。
- 纯反推以忠实复现为目标；换角色任务走 `references/04-coser-replacement.md`，只换皮不动骨。

## 3. 工作流（按序执行）

### Step 1 — 媒资建档
`ffprobe` 取 duration / width×height / r_frame_rate / codec / 音轨。判定画幅、时长、有无音轨。Windows 下可直接跑 `scripts/forensic_probe.ps1`（参数为 `-Video`，建议带 `-NoProfile`），跨平台跑 `scripts/forensic_probe.sh`。命令见 `references/01-forensics-commands.md` 与 `references/ffmpeg-cheatsheet.md`。

### Step 2 — 全片稀疏采样建骨架（只建假设，不下结论）
按片长选间隔（<5s 用 0.2s；5–10s 用 0.3–0.4s；10–15s 用 0.15–0.2s；>15s 用 0.2s + 转折补抽），抽帧后拼 contact sheet 一次看全。产出：场景、人数、机位关系、粗略段落，以及一张**歧义点清单**。此阶段禁止锁定唯一剧情。

### Step 3 — 音频三检（与 Step 2 并行）
1. 提单声道 wav；2. 频谱图判音乐/现场；3. 0.5s RMS 表标能量峰；4. BPM 可信度校验（`scripts/audio_probe.py`）。volumedetect 响度表与配乐 recipe 见 `references/audio-heuristics.md`。

### Step 4 — 转折区间密帧判别取证
对每个歧义点/能量峰区间用 4–8fps 密帧+网格逐格读：动作发起物、受力方向、液体/道具轨迹、入画的手、表情。目标是在多个候选剧情间裁决，不是给既定假设找佐证。必要时导原分辨率单帧终核。

### Step 5 — 建因果事件链
每事件按 `触发 → 发起 → 扩张 → 重音 → 回收` 写，相邻事件用残余动量衔接。逐帧三问：谁先动？力/方向？下一状态由什么导致？重复结构（如三次反击三次被打断）提炼成 N-beat 写进剪辑字段。同时判定 cut vs 连续（规则见 `references/shot-syntax.md`）。

### Step 6 — 剪辑特效层识别
按 `references/03-edit-effects.md` 区分一镜到底/硬切/定格/白闪/漫画叠加/变速。每个定格记录四要素：入点、时长、叠加层、回到实拍的方式。

### Step 7 — 主体与道具锁定
逐角色登记年龄感/发型面部/全套服装/鞋袜手套/剧情手持道具/静态佩戴道具/湿身演化；画外行动者登记可见部分、控制物件、每次入画时间与造成结果。

### Step 8 — 选 H3 模式与输出模板

| 用户会喂给 H3 的素材 | 模式 | 用哪套模板 |
|---|---|---|
| 只有视频/纯文本重建 | T2VA | 14 字段式（`references/02-h3-field-mapping.md`） |
| 视频 + 首帧图 | I2VA | 14 字段式 + 首帧锚定句/visual_anchor |
| 视频 + 首尾帧 | FL2VA | 14 字段式 + 首末帧连续路径 |
| 视频 + 仅尾帧 | L2VA | 14 字段式 + 从尾帧反推开场 |
| 视频 + 1~N 张参考图/视频/音频 | **Ref2VA（最常用）** | 六段式（`references/shot-syntax.md`） |

- 14 字段式字段顺序与骨架：`references/02-h3-field-mapping.md`。
- Ref2VA 六段式（subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music）、`<Subject>/<Picture>/<Video>/<Audio>` 标签纪律、cut 语法：`references/shot-syntax.md`。
- 用户说"图1同时锁人物和场景"时，把 `<Picture 1>` 定义为 universal visual anchor（全文视觉权威）。

### Step 9 — 自检、存盘、打印
跑 `references/05-pitfalls-checklist.md` 清单；存 `<video-stem>_h3_prompt.md`；在回复中打印最终文本块；所有推测项显式标注。

## 4. 中文反推报告固定结构

片型（画幅/时长/镜头形态/片种）→ 场景 → 人物（含画外行动者证据）→ 因果动作链（按时间戳讲因果而非罗列画面）→ 剪辑特效（每点入点/时长/叠加/音效）→ 声音结论（有无 BGM 及判据、底噪、同期声、能量峰对账表）→ 推测与待确认。

## 5. 什么时候必须停下来问用户

密帧后仍无法在候选因果间裁决；遮挡/分辨率不足；分不清现场动作还是后期特效；换角色时新角色缺少原动作部件（如原动作依赖可掀面罩而新角色是封闭头盔）且有多种改法。提问要给：候选解释、各自支持/反对证据、你的倾向、需要拍板的具体问题。

## 6. Bundled Resources

- `references/01-forensics-commands.md` — 抽帧/网格/频谱/RMS/BPM 命令库 + 音画交叉验证矩阵
- `references/02-h3-field-mapping.md` — 观察→14 字段映射、时间戳纪律、T2VA/I2VA 英文骨架
- `references/03-edit-effects.md` — 定格四要素、白闪/漫画叠加写法、特效音、防漂移
- `references/04-coser-replacement.md` — 只换皮不动骨 SOP、动作兼容性、道具入画纪律、真人 cos 转译、对照表
- `references/05-pitfalls-checklist.md` — 十大陷阱、认知自检、交付清单
- `references/shot-syntax.md` — Ref2VA 六段式骨架、cut 语法、运镜词库、reference label 纪律
- `references/audio-heuristics.md` — volumedetect 响度表、配乐 recipe、频谱/RMS/BPM 判据
- `references/ffmpeg-cheatsheet.md` — Windows PowerShell 为主的 ffprobe/ffmpeg 命令速查
- `scripts/forensic_probe.ps1` / `forensic_probe.sh` — 一键取证；`scripts/audio_probe.py` — RMS 包络 + BPM 误检判定
