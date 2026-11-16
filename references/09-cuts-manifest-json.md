# 09 — cuts_manifest JSON：节奏时间轴的生成与读取（audio-lyric-splitter 能力）

> 本 reference 使本 skill 具备 `audio-lyric-splitter` 的完整能力：从音频（+SRT 歌词）生成 **节奏时间轴 JSON（cuts_manifest）**，再以该 JSON 为时序底稿反推/创作分段 H3 提示词。视频反推任务中，本 JSON 用于把 onset 卡点升级为**完整节拍网格 + 字位时间轴**；纯音频创作任务中它是唯一时序来源。

## 0. 什么时候走 JSON 管线（决策门）

| 任务形态 | 是否生成 cuts_manifest |
|---|---|
| 反推目标：固定节拍 BGM、需要逐拍编舞/分段创作 | **是**（Step 3B） |
| 反推目标：自由散板/无 BGM/环境声 | 否——onset_probe 锚点即可（禁止写 BPM） |
| 音频创作任务：用户提供整首歌+歌词，要做多段 MV | **是**（先 split 后反推/创作） |
| 用户已提供 cuts_manifest JSON | 直接读取（§2），跳过生成 |

**只出 JSON、不切割模式（反推任务默认）**：反推对象是视频时，音频只是节奏参考——只跑步骤 1-2（SRT/ASR + analyze_audio）产出 **manifest JSON（含 segments 时间轴/lyric_events/beats/drum_events）供下一步反推使用**；跳过 `cut_by_lyrics.py` 的实切与 zip 打包（如需段长度规划可跑 `--plan` 只看方案）。切割+zip 仅在用户要求"把整首歌切成 H3 多段素材"时执行。

## 1. 生成 cuts_manifest（三步管线）

依赖：`numpy`+`scipy`（分析）；`ffmpeg/ffprobe`；ASR 需 `mediakit-cli`。脚本位于 `audio-lyric-splitter/scripts/`（跨 skill 调用，路径以该 skill 安装目录为准）。

### 步骤 1 — 获取逐句歌词 SRT（有 SRT 跳过）
```
python audio-lyric-splitter/scripts/transcribe_lyrics.py --audio song.mp3 --language zh --content-type singing
```
产出同名 `.srt` 草稿 + `.asr.json`。**ASR 草稿必须人工校对后才能用**（唱歌错字/间奏误识别/长句合并三查：改字→删拟声→拆句核边界）。强伴奏识别差先 `mediakit-cli audio separate-voice` 分离人声再识别。宁可请用户补歌词，不拿未校对时间轴硬切。

### 步骤 2 — BPM 与节拍网格分析
```
python audio-lyric-splitter/scripts/analyze_audio.py song.mp3 --out analysis.json
```
输出 BPM 候选（含半速/加倍）、选定 BPM、首拍、beat/bar/phrase、低能量间奏。**慢板/古风常被报半速**：看候选半/倍速用 `--bpm`（必要时 `--first-beat`）锁定。间奏以 SRT 无唱句区间为准。

### 步骤 3 — 切段 + manifest
```
# 先看方案（不切文件）：
python audio-lyric-splitter/scripts/cut_by_lyrics.py --audio song.mp3 --srt song.srt --outdir out --plan
# 确认切词 0 处再实切 + zip：
python audio-lyric-splitter/scripts/cut_by_lyrics.py --audio song.mp3 --srt song.srt --outdir out --title "歌名"
```
切割规格：每段目标 12.5s、允许 10-15s（`--min/--max/--target` 可调；H3 上限 15s 对齐 max=15）。合法切点不落任何唱句开区间内；气口 gap≥0.15s 切点距句界留 0.06s 保护；DP 代价=段长偏离目标平方+贴近小节首拍偏好。**节拍对齐永远让位于"不切词"。** 实切后 ffprobe 自检（段长/求和/逐句完整/无切词），不通过退出码 1。

## 2. cuts_manifest schema 速查

`meta`：`source / srt / bpm / beat_sec / bar_sec / phrase_sec / first_downbeat_sec / min_sec / max_sec / target_sec / total_duration / segment_count / accent_legend / note`。
每段 `segments[]`：`seg / start / end / length / cut / file / lyrics[] / lyric_events[] / beats[] / drum_events[]`。

- `beats[] = {local, global, k, accent}`：accent 四级——`phrase`(k%8，乐句) / `downbeat`(k%4，小节) / `onbeat`(k%2) / `offbeat`。`local` 相对段头，供 H3 段内卡点。
- `lyric_events[] = {text, local_start, local_end, global_start, global_end}`：逐句字位；**散板/自由节奏以字位为准**。
- `drum_events[] = {local, time, type(kick/snare/hihat/other), confidence, strength, beat_index, grid_offset}`。

### 三种时间绝不混用
| 类型 | 字段 | 写进单段 H3？ |
|---|---|---|
| 原曲全局时间 | start/end/global* | 否（索引/对账/跨段定位） |
| 本段局部时间 | beats[].local / lyric_events.local_* | **是（动作+运镜唯一时钟）** |
| 相对拍位 | beats[].k / 链内"第几拍" | 判结构，不当秒数 |

换算：`local = global - segment.start`。JSON 已有 local 就直接用，不拿 BPM 网格重算覆盖。**局部时间归零 ≠ 节拍相位归零**：SEG02 第一拍可能在 0.361s，不为好看挪到 0.000。

### accent→动作职责映射
phrase=舞句转换/姿态峰值/母题回归/切点；downbeat=脚步落地/胯 hit/手臂完成位/方向变化；onbeat=次级肢体/重心交换；offbeat=头部/腕指/肩微 hit/惯性延续。**不要每拍都设计新动作。**

### drum_events 筛选
先 type 后 confidence；`other` 不得写成 kick。人工初筛：≥0.80 优先复核 / 0.70-0.79 结合拍网 / <0.70 仅参考。strength 不是动作力度。鼓点冲突时先保动作因果与歌词时序，再选一个主要视觉重音。

### lyric_events 使用
歌词=语气/情绪/结构参考，不是视觉道具清单（歌词"雪花"≠生成雪花）。找语气起点、重读字、句尾释放；歌词空隙用持续层/重心/恢复/视线/服装惯性填充。

### 选段纪律
按 `seg` 选段；保留原始 start/end/length/file；删段后复核相邻段真实相邻（缺口如实标注）；每段生成长度=真实 length，不统一成 target_sec。

## 3. 古风/散板/慢板的特殊规则（最长 15 秒分段）

1. **散板禁止 BPM/拍号**：`analyze_audio.py` 的候选在散板全部失效（自相关无周期）。判定=onset 间隔不匀+频谱无 kick 网格+lyric_events 字位驱动。散板段提示词写 `on the strong accent of <Audio 1>` + lyric_events 字位锚点，beats[] 仅作弱参考。
2. **rubato/弱网格**：自相关 std/mean >0.5 判弱网格——可给"参考 BPM"但动作锚点以 lyric_events 字位+强 onset 为主，beat grid 仅用于段落长度控制。
3. **15s 上限**：`--max 15`（H3 官方上限对齐）；古风长乐句常导致 DP 无解→允许 `--min 8 --max 15` 放宽下限，或按乐句手切+人工核验。
4. **不切词优先级最高**：古风拖腔/气口不明显时，宁可段长短于 10s 也不切断唱句；超短段并入邻段或单独生成。
5. **戏曲/戏腔**：ASR singing 模式识别差，优先请用户给 SRT；间奏"啊"类拟声全部删除。
6. **慢板动作容量**：慢歌不等于慢动作摆拍——持续层（提沉呼吸）+ 字位驱动的完整链；60+ BPM 时每 lyric_event 最多承载一条完整链，句间用呼吸/视线填充。

## 4. JSON→H3 的输出契约（与 Rev1.0 方法论对齐）

生成/反推的最终交付为**完整 MD**（项目说明+JSON 摘要+资产表+分段索引+转场表+每段 H3 代码块+自检），每段提示词用本 skill `references/10-json-to-mv-methodology.md` 的官方模式模板（基础三段 / Ref2VA 六段）。核心纪律速记：

1. JSON 先读全（meta/segments/lyric_events/beats/drum_events）→ 2. 选段核验连续性 → 3. 全曲时钟不重置（local 进 H3，global 定位）→ 4. 先定 MV 概念与段落差异矩阵 → 5. 查动作库当前版本（dance-motion-chain-h3.md Rev 号）→ 6. 时间窗容量先行（0.3-0.6s 短促重拍/0.6-1.2s 短链/1.2-2.5s 复合句）→ 7. 编舞写因果（支撑→传递→峰值→惯性→回收）→ 8. 摄影机写物理（NO DEGREE LAW：位置/高度/距离/路径/触发/构图，禁数字角度标签）→ 9. 动作与相机 1:1 同一套时间码 → 10. `[Shot 1]` 无时间戳，`[Shot N] At MM:SS.mmm` 递增 → 11. 转场六要素（出态/动量/切点/机制/入态/下镜机位）→ 12. Picture 是首帧(I2VA)还是全参考(Ref2VA)分清 → 13. Audio `fully_copy` 与 `reference` 不得互换 → 14. 每段自包含 → 15. 输出完整 MD+五层自检（JSON/动作/相机/转场/语法）。
