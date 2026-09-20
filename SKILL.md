---
name: video-to-h3-prompt
description: Reverse-engineer a reference video into a complete, ready-to-paste MiniMax H3 prompt (T2VA / I2VA / FL2VA / L2VA / Ref2VA) through dense frame sampling, audio onset/card-point cross-validation, causal event-chain reconstruction, film-type → camera-state-machine triage (continuous take / editorial snap-lock / multi-shot montage), edit-layer separation, multi-image character locking and long-clip multi-segment splitting. Covers prank/UGC/narrative/action/dance clips, freeze-frame and manga gags, off-camera actors, music card-point editing, and coser/character replacement without plot change. Use when the user provides a video (and optional reference images/audio) and asks to 反推视频 / 把图1替换进去 / 视频转H3提示词 / 卡点时间 / 节奏分析 / 多镜头分镜运镜 / 分段生成 / reverse this video for h3 / extract h3 prompt from this clip / 只换角色不改剧情. Always print the ready-to-paste English prompt block in the reply; save a .md only when the user or workflow explicitly requests file delivery.
---

# Video → H3 Prompt（视频反推 MiniMax H3 提示词）

End-to-end pipeline that turns a video file into a ready-to-paste H3 prompt. It is **not** "watch a few frames and write an atmosphere blurb" — it is a forensic workflow: `取证 → 交叉验证 → 因果重建 → 片型分流选状态机 → 选模式/分段 → 字段落点 → 自检交付`. Companion to `h3-prompt-writing` / `h3-prompt-master`; reuse their field templates and shot syntax.

## 0. 输入与输出

- **输入**：参考视频（可选：多张参考图、分段音频、用户剧情说明、角色/coser 替换要求）。
- **输出三件套**：
  1. 中文反推报告（片型 / 场景 / 人物 / 因果动作链 / 机位分镜 / 剪辑特效 / 节奏卡点 / 声音结论 / 推测项）；
  2. 字段完整、时间戳精确、可直接粘贴的**英文** H3 prompt（长片按段给多份）；
  3. 换角色任务必须附「替换对照表」。
- **交付形态**：默认在回复中直接打印可整段复制的英文文本块；只有用户或工作流明确要求落盘时，才把结果存为 `<video-stem>_h3_prompt.md` 于视频同目录。

## 1. 反推六条铁律（每次先过一遍）

1. **先判「连续运镜」还是「离散快切」**：转折段 8fps 以上密帧，别让稀疏采样跨过整个 burst；在帧序列里找「运动—完全静止」的台阶。
2. **音频做时间轴对账**：每个切换/定格/冲击是否挂在 onset 上？是→编辑式快照/卡点剪辑；否→才考虑自由运镜。
3. **有参考图就别写外貌**：图锁外观，文字只写相机/时间/状态机/环境道具。
4. **静态与爆发写成两个互斥状态**：静态段把「不许慢动作/漂移/继续运动」在时间轴、相机段、negative 三处反复写死。
5. **横置先怀疑相机 Roll**：看地平线与身体的相对关系，别轻易判定人物躺/转。
6. **冲击要可数、不可糊**：连续冲击逐个可读（位移/前推/旋转），明确「不是连续震动」，且只动相机、不变形人物。

## 2. 核心原理：细颗粒度为什么可能（五个证据通道）

细度来自五条独立证据链互相锁死，而不是"看得更用力"：

1. **密度采样通道**：全片稀疏网格建骨架；转折区间 4fps（必要时 8fps）密帧；关键瞬间原分辨率单帧终核。只持续 3–5 帧的动作（一只手掰头盔、一次枪口火光）在稀疏采样下会彻底消失或被误判。
2. **音频取证通道（两级粒度）**：频谱图判有无 BGM；0.5s **RMS** 包络找能量峰；**onset 音头检测**给每个弹拨/重音的精确时刻用于卡点。每个能量峰/强 onset 必须在画面里找到成因。
3. **因果链通道**：每个状态变化回答 trigger → action → reaction（谁先动、力朝哪、结果落哪）。罗列画面 = 摆拍；重建因果 = 可执行事件链。
4. **状态表通道**：逐帧维护道具/身体状态（面罩开合、杯瓶位置、头发干湿、液体方向颜色、谁的手在画内、墙是否已炸开），状态翻转点就是时间戳锚点。
5. **分层通道**：现场动作层 / 运镜层 / 后期剪辑特效层 / 声音层分离。定格、白闪、漫画线、拟声字、RGB 故障、黑翼属于后期/特效层，绝不写成现场可拍摄动作。

### 交叉验证铁律
任何断言至少被两个通道支持才写成事实；单通道支持标「推测」；通道矛盾时以物理证据为准并记录证伪（例：算法报 117 BPM，但 onset 间隔不匀且频谱无 kick 网格 → BPM 误检，判自由散板/无 BGM）。

### 反推是一对多的逆问题
脚本→画面是多对一映射：不同脚本可以拍出几乎相同的画面（自呛 vs 被掰头误伤；相机 Roll vs 人物躺下）。因此画面→脚本欠定，**稀疏采样后必须并列多个候选剧情，用密帧做判别性取证**，而不是用最常见模板直接填满。用户给的剧情是行动者清单/意图链/剪辑意图，用于收敛解空间；收到后回帧序列逐条验证，不盲信、不拒绝。

## 3. 硬性原则

- H3 可执行内容一律**英文**；对用户的分析讨论用用户语言。
- `[Shot 1]` 不带时间戳；其后时间戳严格递增（Ref2VA 用两位小数 `00:03.200`，14 字段式可用一位；**多段生成时每段从 00:00 重新计时**），只标真实状态变化。
- 三层声音分离：动作同期声内嵌动作句；环境/特效音进 `overall_soundscape`；音乐只进 `non_diegetic_music`，原片无 BGM 写 explicit silence / `N/A`，禁止脑补配乐。
- **自由散板（轮指独奏等）禁止写 BPM/拍号**：写 `on the strong accent of <Audio 1>` + 时间码锚点；固定节拍才可写 BPM/Beat。
- **有目的运动的非身体物体必有控制者**：伸入画面的手、袖子、车头、杯瓶归并到一个画外行动者，不当杂物。第一人称拍摄者默认是潜在剧中行动者。
- 每个视觉结果必须有物理路径（水从哪含、沿什么方向、喷在透明还是镀膜面罩）；路径不通回查帧。
- 纯反推以忠实复现为目标；换角色任务走 `references/04-coser-replacement.md`，只换皮不动骨。
- 工程坑：中文/空格源路径先复制为纯英文工作副本再喂 ffmpeg；新版 Python（如 3.14）librosa 常无 wheel，用 `scripts/onset_probe.py`（numpy/scipy）即可，不必强装。

## 4. 工作流（按序执行）

### Step 1 — 媒资建档
`ffprobe` 取 duration / width×height / r_frame_rate / codec / 音轨，判画幅、时长、有无音轨。Windows 跑 `scripts/forensic_probe.ps1`（参数 `-Video`，建议 `-NoProfile`），跨平台跑 `forensic_probe.sh`。命令见 `references/01-forensics-commands.md`、`ffmpeg-cheatsheet.md`。

### Step 2 — 全片稀疏采样建骨架（只建假设，不下结论）
按片长选间隔（<5s 用 0.2s；5–10s 用 0.3–0.4s；10–15s 用 0.15–0.2s；>15s 用 0.2s + 转折补抽），拼 contact sheet 一次看全。产出场景、人数、机位关系、粗略段落和一张**歧义点清单**。此阶段禁止锁定唯一剧情。

### Step 3 — 音频取证（与 Step 2 并行，两级粒度）
1. 提单声道 wav；2. 频谱图判音乐/现场；3. `audio_probe.py` 出 0.5s RMS 能量峰；4. `onset_probe.py` 出分级音头（S/H）与逐秒密度轮廓；5. 判固定节拍还是自由散板（见 `references/07`）。每个 RMS 峰、每个强 onset 都要与画面事件对账。

### Step 4 — 转折区间密帧判别取证
对每个歧义点/能量峰/强 onset 区间用 4–8fps 密帧+网格逐格读：动作发起物、受力方向、液体/道具轨迹、入画的手、表情、地平线与身体关系。目标是在多个候选剧情/机位假设间裁决。必要时导原分辨率单帧或烧时间码网格（命令见 `07`）。

### Step 5 — 建因果事件链
每事件按 `触发 → 发起 → 扩张 → 重音 → 回收` 写，相邻事件用残余动量衔接。逐帧三问：谁先动？力/方向？下一状态由什么导致？重复结构（三次反击三次被打断、连续臀部中弹）提炼成 N-beat。

### Step 6 — 片型分流与相机状态机（关键决策门）
按 `references/06-film-type-and-state-machine.md` 判定片型并选定相机机制，**动笔前必须分流**：
- **A 一镜到底**：一条手持/锁定基线 + 每次运镜动机，定格作为同镜头内事件；
- **B 编辑式快照 snap-lock**：两态互斥状态机 `HARD LOCK ↔ INSTANT BURST`，静态段绝对零运动、禁令三处重复、可数冲击、相机 Roll 纪律；
- **C 多镜头快剪 montage**：**命名机位语法**（如 GUNNER/BUTT/PRONE/ORBIT/STINGER）+ 切镜纪律，**不可套 LOCK/BURST**；机位编码权力关系与喜剧，切镜挂 onset。
同时判 cut vs 连续（`shot-syntax.md`），并排除枪口火光/爆炸造成的 scene 检测伪 cut（`07`）。

### Step 7 — 剪辑特效层识别
按 `references/03-edit-effects.md` 区分一镜到底/硬切/定格/白闪/漫画叠加/变速/RGB 故障/能量爆发。每个定格记录四要素：入点、时长、叠加层、回到实拍方式；硬切与特效爆发对齐 onset。

### Step 8 — 主体、道具与多图锁定
逐角色登记年龄感/发型面部/全套服装/鞋袜手套/剧情手持道具/静态佩戴道具/湿身演化；画外行动者登记可见部分、控制物件、每次入画时间与结果。**用户喂多张参考图时走 `references/08`：图1锁角色1、图2锁角色2，只锁身份+服装（all-purpose），环境/灯光/道具由文字定义，正文零外貌文字**；剧情手持武器/道具仍由文字写。

### Step 9 — 选 H3 模式、长片分段与输出模板

| 用户会喂给 H3 的素材 | 模式 | 用哪套模板 |
|---|---|---|
| 只有视频/纯文本重建 | T2VA | 14 字段式（`02`） |
| 视频 + 首帧图 | I2VA | 14 字段式 + 首帧锚定句/visual_anchor |
| 视频 + 首尾帧 | FL2VA | 14 字段式 + 首末帧连续路径 |
| 视频 + 仅尾帧 | L2VA | 14 字段式 + 从尾帧反推开场 |
| 视频 + 1~N 张参考图/视频/音频 | **Ref2VA（最常用）** | 六段式（`shot-syntax.md`）/ 多图 all-purpose（`08`） |

- **源片 >约 15s 必须分段**：切点选气口、每段段内时钟从 00:00、各喂同一套图+分段音频、音乐 CONTINUES 不重启、段末写 hand-off state 下段开场复述。完整 SOP 与字段继承见 `references/08`。
- 用户说"图1同时锁人物和场景"时，把 `<Picture 1>` 定义为 universal visual anchor（`shot-syntax.md`）。

### Step 10 — 自检、交付
跑 `references/05-pitfalls-checklist.md` 与所选片型在 `06` 末尾的分流自检；默认在回复打印最终英文文本块（长片逐段给），所有推测项显式标注；仅在明确要求时存盘。

## 5. 中文反推报告固定结构

片型（画幅/时长/镜头形态/片种/**A连续·B快照·C快剪 分流结论**）→ 场景 → 人物（含画外行动者证据）→ 因果动作链（按时间戳讲因果）→ **机位分镜表（景别·机位角度·运镜·动机）** → 剪辑特效（每点入点/时长/叠加/音效）→ **节奏分析（固定节拍/自由散板、逐段密度曲线、onset↔画面卡点对账表、一级卡点锚点）** → 声音结论（有无 BGM 及判据、底噪、同期声、能量峰对账）→ 推测与待确认。

## 6. 什么时候必须停下来问用户

密帧后仍无法在候选因果/机位间裁决；遮挡/分辨率不足；分不清现场动作还是后期特效；横置无法确定是相机 Roll 还是人物转身；换角色时新角色缺少原动作部件（如原动作依赖可掀面罩而新角色是封闭头盔）且有多种改法；切点无法落在气口。提问要给：候选解释、各自支持/反对证据、你的倾向、需要拍板的具体问题。

## 7. Bundled Resources

- `references/01-forensics-commands.md` — 抽帧/网格/频谱/RMS/onset/BPM 命令库 + 音画交叉验证矩阵
- `references/02-h3-field-mapping.md` — 观察→14 字段映射、时间戳纪律、T2VA/I2VA 英文骨架
- `references/03-edit-effects.md` — 定格四要素、白闪/漫画叠加/RGB 故障写法、特效音、防漂移
- `references/04-coser-replacement.md` — 只换皮不动骨 SOP、动作兼容性、道具入画纪律、真人 cos 转译、对照表
- `references/05-pitfalls-checklist.md` — 高频陷阱、六条铁律、认知自检、交付清单
- `references/06-film-type-and-state-machine.md` — **片型分流（A连续/B快照/C快剪）、两态状态机、命名机位、可数冲击、相机 Roll、反幻觉七要素**
- `references/07-onset-and-card-points.md` — **onset 音头检测、散板判定、卡点对账表、火光伪 cut、烧时间码网格、路径坑**
- `references/08-multi-image-and-segmentation.md` — **多图 all-purpose 角色锁定、零外貌纪律、>15s 分段 SOP、段内时钟、音乐连续、hand-off**
- `references/shot-syntax.md` — Ref2VA 六段式骨架、cut 语法、运镜词库、reference label 纪律
- `references/audio-heuristics.md` — volumedetect 响度表、配乐 recipe、频谱/RMS/BPM 判据
- `references/ffmpeg-cheatsheet.md` — Windows PowerShell 为主的 ffprobe/ffmpeg 命令速查
- `scripts/forensic_probe.ps1` / `forensic_probe.sh` — 一键取证（含 onset）；`scripts/audio_probe.py` — RMS 包络 + BPM 误检判定；`scripts/onset_probe.py` — **音头/卡点检测（numpy/scipy，无需 librosa）**
