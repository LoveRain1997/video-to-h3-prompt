# 12 — 官方写作规范桥（h3-prompt-writing base-en / ref-en 集成）

> 本 skill 的**写提示词半场**已集成官方 `h3-prompt-writing` 技能：官方规范全文随包捆绑——
> - `references/base-en.txt`：T2VA / I2VA / FL2VA / L2VA 最终结构（对齐指令 + 三核心字段 + 完整案例）
> - `references/ref-en.txt`：Ref2VA 全参考模式六段格式（标签定义 / retention / detailed_description / 音频关系标记 / 完整示例）
> 分工：refs 01-08/11 产出**反推内容**（事实表/因果链/片型/节奏）；本 ref + 两份官方 txt 决定**怎么写进 H3 字段**；`02` 十四字段与 `shot-syntax` 六段是内部装配器。**冲突时官方规范优先。**

## 0. 写块路由（Step 9 强制）

| 模式 | 写块前必读 | 最终结构 |
|---|---|---|
| T2VA / I2VA / FL2VA / L2VA | `base-en.txt`（§2 结构、§3 关键帧、§4 三核心段规则） | 对齐指令行（如适用）+ `integrated_multimodal_description` / `overall_soundscape` / `non_diegetic_music` |
| Ref2VA | `ref-en.txt`（§2 标签、§4 retention、§5 detailed、§6 声音段） | `subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music` |

## 1. base 模式官方结构要点

- **对齐指令固定句式**（必须是提示词第一行，后接一个空行）：
  - I2VA：`For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
  - FL2VA：`How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
  - L2VA：`How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`（N=最终 Shot 序号，S.SS=有效时长两位小数）
- **三核心段篇幅纪律**：`overall_soundscape` 1–4 句连续一段（对白/唱歌/画内音乐不重复）；`non_diegetic_music` 1–3 句（乐器/速度/节奏/动态，禁抽象情绪词，禁解释配乐功能）；角色听得到的声音（手机/电视/广播）是画内事件，写进主时间线。
- **运镜官方三维度**：类型+幅度+速度；中等幅度/正常速度可省略。官方词表明确 **Zoom（焦距变化机身不动）≠ Push In（机身前移）**、Pan（原地摇）≠ Truck（机身横移）、Tilt（俯仰）≠ Pedestal（机身升降），另有 Arc Shot / Tracking Shot / Static Shot / Shake / POV / Roll Clockwise。运镜写成 Shot 内自然英语动作句，不在句尾堆标签。
- **画内文字**：实际可见的招牌/字幕/横幅用英文双引号原样保留，不翻译：`A red neon sign reading "营业中" glows above the doorway.`
- **切镜动词**：`the camera cuts to / the shot cuts to / the shot transitions to / the shot changes to / the shot switches to`；cross-dissolve/fade/wipe 仅用户明确要求时用；只改距离或小角度优先运镜不加 Shot。

## 2. 说话人、对白与歌声（官方 (S1) 体系，此前 v2h3 未收录）

- 说话/唱歌/画外人声的主体用稳定 ID `(S1)` `(S2)`；多个已编号主体同声用复合 ID `(S1,S2)`；**同一说话人跨 Shot 保持同 ID**；从不发声的角色不编 ID。
- 首次出现给足身份信息（角色类型/年龄/性别/是否在画内/音高/音色/语速/口音）。
- 身份短语、ID、动作、语气放 `<d>` 外；`<d>` 内只有语言标签+原文内容，逐字保留不翻译：`The young woman with a quiet, breathy voice (S1) says: <d>[English] I get off at the next station.</d>`
- 画外配音固定短语 `says in an off-screen voiceover`，且 `<d>` 块后紧跟画内角色闭嘴声明：`... while his lips remain completely closed.`
- **跨镜音频标签**：同一句对白/歌词跨切点，两侧用 `<scenetrans>` 并明说音频跨切继续（`continues seamlessly across the cut` 等）；片尾被截断用 `<cutoff>`。

## 3. Ref2VA 音频关系标记（四态，此前只收录了 fully_copy/reference 两态）

| 标记 | 含义 |
|---|---|
| `fully_copy` | 源音频整体 1:1 作为目标视频完整最终音轨 |
| `partially_copy` | 只拷部分时间轴/部分音频层，或拷后增删替换声音 |
| `reference` | 信号不拷贝，只参考音色/节奏/曲风/对白内容/声音质地 |
| `weak_reference` | 只保留大类或氛围相似 |

- 关系标记必须在 `subject_definitions` 已定义的参考角色范围内选择；目标视频新增的动作/背景/剧情**不算**参考保真损失。
- 音频标签映射说话人：`<Audio 1> is the voice-timbre reference for <Subject 1> (S1).`——Sx 来自目标视频全局说话人序，不在音频定义里重编。
- **同源视频双轨**：`<Video N>` 与 `<Audio N>` 独立编号，互不编码配对；同一参考视频可以是 `<Video 1>` + `<Audio 2>`。普通参考视频**不因含音轨就自动产生** `<Audio N>`；需要消歧时写明 `<Audio 2> is the synchronized audio track of <Video 1> and is reused in the target video.`

## 4. detailed_description 官方规则（Ref2VA 主时间线）

- 全参考模式与 T2VA 的五维差异：主字段=`detailed_description`；风格开场在 `[Shot 1]` **前**用 1-2 句独立成段（`The target video is in a cinematic, literary music-video style...`）；参考标签在首次出现处与作用处插入；音频关系在对应 Shot/语义阶段引用 `<Audio N>` 并写明拷贝还是参考。
- 篇幅：生成任务通常 **350-500 英文词**；对白密集内容优先保证完整说唱时间线，不机械凑词；剪辑描述随源片复杂度伸缩；单 Shot 不自动等于短描述——按信息量分配。
- 标签进 Shot：重要 `<Subject N>` 首次清晰出现处描述参考特征+画面位置+当前动作，后续 Shot 复用同标签不重定义；帧锚自然短语：`the shot begins from <Picture 1>` / `the shot's keyframe corresponds to <Picture 2>` / `the shot ends on <Picture 3>`。

## 5. 十四字段装配器 → 官方字段的折叠规则

`02-h3-field-mapping.md` 的 14 字段是**内容装配器**（保证反推信息不丢），最终输出必须折叠成官方结构：

| 内部字段 | 折进 |
|---|---|
| `environment_definition` / `lighting_definition` | 各 `[Shot]` 的环境与光线句（或 Ref2VA 的标签定义/主时间线开场） |
| `camera_direction` / `editing` / `performance` / `body_mechanics` / `costume_hair_physics` | `integrated_multimodal_description`（Ref2VA=`detailed_description`）对应 Shot 的动作/运镜/剪辑句 + 稳定要求句 |
| `negative_constraints` | 主时间线内的具体禁令句 + `OVERALL CONTINUITY`/continuity 段（少量可验证约束+正确状态说明），**不发明 `negative_prompt` 独立字段** |
| `visual_anchor` / `audio` | 官方对齐指令行 / `<Audio N>` 标签与关系标记 |
| `overall_soundscape` / `non_diegetic_music` | 原样保留（官方字段同名） |

## 6. 冲突裁决与自检增补

1. **官方规范 > 内部模板**：字段名/段落顺序/标签大小写空格/时间记法以官方 txt 为准；发现内部文档与官方冲突，改内部文档并记录，不发明第三种格式。
2. 五层自检（ref 10 §7）的 E 层增补三查：①说话人 ID 全局一致且从不发声者无 ID ②音频关系标记四态选对且不越出 subject_definitions 定义的角色 ③画内文字双引号原样、`<d>` 内逐字不翻译。
3. 复述确认门（ref 11 §8）确认的是**内容理解**；写块阶段的字段语法问题不回头重问用户，按官方规范直接修正。
