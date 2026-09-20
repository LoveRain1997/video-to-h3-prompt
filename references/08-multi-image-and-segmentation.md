# 08 — 多图角色锁定与长片分段（all-purpose reference / multi-segment）

处理两类高频需求：① 多个角色各给一张参考图（图1锁角色1、图2锁角色2……）；② 源片超过单次生成时长（约 15s），要切成多段连续生成。

---

## 1. 多角色 all-purpose reference：图锁身份服装，文字写环境道具

当用户"喂图1=角色1、图2=角色2"，且要保留反推出的场景时，用 **all-purpose（角色）参考**，不是首帧锚定：

- 每张 `<Picture N>` 只锁**对应角色**的身份与服装；**不锁环境、灯光、构图、首帧姿势**（这些由文字定义）。
- 一个角色一张图、一个 `<Subject N>`，标签全文语义一致，不得改名/别名。

### subject_definitions 写法（逐角色）

```text
subject_definitions: Use <Picture 1> as the SOLE and COMPLETE authority for <Subject 1>'s
identity and costume: exact face, facial structure, eyes, hairstyle and hair color, skin,
body proportions, and the ENTIRE outfit/accessories/footwear in every shot.
Use <Picture 2> identically as the sole authority for <Subject 2>'s identity and costume.
The pictures lock CHARACTER IDENTITY AND COSTUME ONLY — they do NOT define the environment,
lighting, camera, composition or starting pose; those are defined entirely by the text below.
Preserve each character exactly across all shots, including back views, prone/crouching/
hopping poses and any glitch effect; do not redesign, swap, beautify or add any appearance
or clothing detail.
```

### 图锁什么 / 文字写什么（边界表）

| 元素 | 归谁 |
|---|---|
| 脸、五官、发型发色、肤色、体型 | 图（零文字） |
| 全套服装、鞋帽、手套、静态配饰 | 图（零文字） |
| **剧情手持道具/武器**（双枪、刀、杯瓶、载具） | **文字**（道具不属于服装，参考图里往往没有） |
| 场景、建筑、地面、背景物件、氛围 | 文字 `environment_definition` |
| 灯光方向/色温/特效光 | 文字 `lighting_definition` |
| 机位、景别、角度、时间轴、状态机 | 文字（见 `06`） |

### 置顶权威声明（多图版）

```text
Use <Picture 1>/<Picture 2> as the ONLY identity-and-costume source.
Use <Audio 1> as the ONLY temporal and rhythmic source.
Environment, props, lighting, camera and the state machine are defined by the text.
Do not invent appearance; do not invent a separate rhythm.
```

纪律：**有图就删外貌文字**——再写一遍发型/瞳色/服装会诱导模型在图与文字之间"二创"。极端姿势（劈叉、趴地、环绕、回头）若担心身份漂移，最多加一句与图一致的"轮廓+整体色调"极短锚点，且冲突时以图为准（与 h3-prompt-master 的 minimal-anchor 规则一致）。

---

## 2. 长片分段（>约 15s）

### 2.1 切点选择

- 每段目标 10–15s；切点选在**动作连续的气口**、镜头段落边界或两次重音之间，**不要切在一个爆发/硬切的正中间**。
- 切点本身不必是强 onset；让上段收在某个重音后的姿态、下段在下一个强 onset 给第一个事件，衔接最顺。
- 记录每段对应的**源片全局时间区间**，但段内提示词用**段内时钟**（见 2.3）。

### 2.2 每段独立生成、各自喂素材

- 每段都喂同一套 `<Picture 1>…<Picture N>`（角色锁定每段重复，不能假设模型记得上段）。
- 每段喂该时间区间切出的音频，仍标 `<Audio 1>`；**音乐必须连续不中断、不从头重启**。
- 共享规则（机位命名/状态机、环境、灯光、negative、声音基调）在每段**重复写全**——各段独立生成，不能依赖"上一段说过"。

### 2.3 段内时钟从 00:00 起（避免全局时间误读）

- 段内所有 `[Shot]`/时间戳从该段 `00:00` 重新计；只在段头标注它覆盖源片的全局区间（`covers source 00:15–00:29.3`）。
- 不要在第 2 段里继续写源片的 00:17、00:22，模型会把它当成"该段第 17、22 秒"而错位。
- 段内 onset 时间 = 源 onset − 段起点（例：源 22.55 的硬切，在第 2 段（起点 15.0）写作 07.55）。

### 2.4 hand-off continuation state（段末=下段首）

- 除末段外，每段结尾显式写一个**可被下段第一拍接住的身体/场面状态**：人物姿态、朝向、道具位置、灯光、正在发生的动作。
- 下段 `[Shot 1]`（无时间戳）开场**复述同一状态**再接新动作，保证跨段连续。
- 段边界**不用硬切**表达，而用机位变化/能量级变化/音乐密度变化；如源片在该点本就有硬切（如转场到近景长镜），则照实写。

示例（战斗片切两段，切点源 15.0s）：

```text
PART 1 (source 00:00–00:15, 15.0s) ...
[00:14.9] CONTINUATION STATE: low-rear, he is half-kneeling and staggering in front of
the red breach, a fresh spark glowing on his buttock, debris still falling — Part 2 opens on this.

PART 2 (covers source 00:15–00:29.3, segment clock restarts at 00:00) ...
audio: <Audio 1> is the supplied segment (source 00:15–00:29.3); the music CONTINUES Part 1
and does NOT restart.
[Shot 1] OPEN ON THE HAND-OFF STATE: half-kneeling and staggering at the red breach, fresh spark ...
[00:00.7] on the strong accent, another tracer sparks on his rear (source 15.74) ...
```

### 2.5 段间字段继承（哪些重复、哪些段专属）

| 字段 | 处理 |
|---|---|
| subject_definitions / 图权威声明 | 每段重复（可写 "inherit identity-lock rules from Part 1"，但独立生成时建议写全） |
| environment / lighting / props | 每段重复，保持连续；只写本片内真实发生的变化（如墙被炸开、色调转暖） |
| negative / overall_soundscape 基调 | 每段重复 + 段专属增补 |
| integrated 时间轴 / camera / performance / body_mechanics | **段专属**，各自重写 |
| audio / non_diegetic_music | 每段 `fully_copy <Audio 1>`，第 2 段起注明 CONTINUES、不重启 |

---

## 3. 分段自检

- [ ] 每段时长在模型上限内（约 ≤15s），切点在气口而非爆发中间
- [ ] 每段都重复了图权威、机位/状态机、环境灯光、negative（各段可独立成片）
- [ ] 段内时间从 00:00 起，段头标注源片全局区间；onset 已换算成段内时间
- [ ] 每段音乐注明连续/不重启；分段音频与源区间一一对应
- [ ] 上段末 hand-off state ＝ 下段 [Shot 1] 开场状态
- [ ] 多角色外貌零文字，剧情手持道具/武器由文字定义
- [ ] 跨段身份、服装、道具、空间方位不漂移
