# 10 — JSON → H3 舞蹈 MV 方法论（对齐 JSON_to_H3_DanceMV_Prompt_Methodology Rev1.0）

> 本 reference 是 Rev1.0 方法论的操作浓缩，规定本 skill 在"节奏时间轴 JSON → 分段 H3 提示词"任务中的模板与纪律。**最终提示词必须是 Rev1.0 §11/§12 模板形态的分段提示词**——每段独立完整 H3 代码块，装在完整 MD 里交付。

## 1. 资料三层（不可混淆）
`[H3 官方]` 字段顺序/参考标签/Shot 标记/时间码/声音字段（决定语法）；`[动作库]` dance-motion-chain-h3.md 当前 Rev（决定可复用链+入出态+容量检查）；`[制作经验]` JSON/成品修订（决定拆分与排错）。Markdown 是交付容器，H3 字段是生成格式，动作库是编舞素材——K 编号不进 H3 正文，必须展开为可执行身体动作。

## 2. 十步工作流
JSON 解析 → 选段核验 → 资产映射 → MV 概念与段落差异矩阵 → 查动作链库当前版本 → 局部时间轴编舞（峰值/恢复/续写口）→ 摄影机设计 → 跨段转场图 → 按官方模式写每段自包含提示词 → 五层自检 → 输出完整 MD。

## 3. 每段 H3 正文必备模块
代码块外（Segment 元数据）：SEG 号/音频文件/全局区间/局部时长/歌词 local/phrase+downbeat/选用链/本段签名/前段出态/后段出态。
代码块内：官方模式结构（见 §4），正文按 `[Shot 1]`（无时间戳）→ `[Shot N] At MM:SS.mmm`（递增）展开，动作与机位写在同一 Shot 内，段尾出态写成可见事实。

## 4. 官方模式模板（选用规则）
| 模式 | 输入 | 字段 |
|---|---|---|
| T2VA | 纯文本 | integrated_multimodal_description / overall_soundscape / non_diegetic_music |
| I2VA | Picture 1=首帧 | 首帧对齐句 + 三字段 |
| FL2VA | 首帧+末帧 | 首末对齐说明 + 三字段（单镜连续优先） |
| L2VA | 仅末帧 | 尾帧对齐 + 三字段 |
| Ref2VA | 全参考图+音频切片 | **六段**：subject_definitions / summary / retention_analysis / detailed_description / overall_soundscape / non_diegetic_music（主时间线=detailed_description） |

混搭禁止：`summary+subject_definitions+integrated_multimodal_description` 是历史混合式，不是官方协议。

### Ref2VA 六段母本（默认；dance MV + 全参考图 + 独立音频切片）
```text
subject_definitions:
<Subject 1> is the exact same performer whose identity, face, hairstyle, body proportions, outfit, accessories and footwear are defined by <Picture 1>. Preserve these visual attributes throughout the entire target segment.
<Subject 2> is the complete environment shown in <Picture 1>, including the spatial layout, background architecture, fixed visible objects, lighting direction and established color palette. Preserve this environment without redesigning it.
<Audio 1> is the exact audio slice for this target segment. The supplied audio signal is reused as the complete soundtrack for this segment.

summary:
[reference generation + audio reuse] A <DURATION>-second live-action <STYLE> dance MV segment featuring <SUBJECT COUNT> performer(s). <PICTURE ROLE> remains the authority for the subject and scene, while <AUDIO ROLE> is reused 1:1. The choreography combines <PRIMARY DANCE VOCABULARY> with <SECONDARY STYLE>, using <CAMERA SIGNATURE>. The segment begins from <INCOMING STATE> and ends in <OUTGOING STATE>.

retention_analysis:
<Subject 1> (appears throughout [Shot 1]-[Shot N]): fully_preserved - preserve the same facial identity, hairstyle, body proportions, outfit, accessories and footwear.
<Subject 2> (appears throughout [Shot 1]-[Shot N]): fully_preserved - preserve the original spatial layout, architecture, fixed background elements, lighting direction and color palette.
<Audio 1>: fully_copy - reuse the complete supplied segment audio 1:1 as the target segment's soundtrack, preserving its exact duration, tempo, pitch, dynamics and lyric timing without restarting, looping, replacing or adding another music track.

detailed_description:
The target video is a <STYLE> dance performance with <VISUAL TREATMENT>. The camera language is <CAMERA PHILOSOPHY>. The same performer and original environment remain consistent throughout.

[Shot 1] <OPENING COMPOSITION>. Begin at the segment's first frame with <INCOMING STATE>. <PERSISTENT MOVEMENT ENGINE>. From 00.000 to <T1>, she <ACTION CHAIN 1: support, force, path, beat accents, technical peak, recovery>. The camera begins at <PHYSICAL START POSITION: height, distance, relative side>, then <PHYSICAL PATH> in direct response to <ACTION TRIGGER>, arriving at <END POSITION AND COMPOSITION> exactly as <MOVEMENT PEAK> completes.

[Shot 2] At 00:<CUT1>, the camera cuts to <NEW CAMERA POSITION AND NEW VISUAL INFORMATION>. From <T1> to <T2>, she <ACTION CHAIN 2: entry, weight transfer, body mechanics, beat accents, peak, recovery>. The camera <MOTION TYPE + PHYSICAL PATH + SPEED/AMPLITUDE> as the action unfolds, then stabilizes at <PEAK COMPOSITION> on <ONSET / DOWNBEAT>.

[Shot N] At 00:<CUTN>, the camera cuts to <FINAL SHOT COMPOSITION>. From <TN> to <DURATION>, she <FINAL ACTION / RELEASE / OPEN CONTINUATION>. Do not add a new ending pose unless this segment is the actual final segment. The segment ends with <EXACT VISIBLE OUTGOING STATE>.

OVERALL CONTINUITY:
<One concise paragraph: same person, same world, same outfit, no unintended props/characters, movement continuity, final state.>

overall_soundscape:
<1-4 English sentences: ambience, physical action sounds, non-verbal human sounds only.>

non_diegetic_music:
<Audio 1> is reused 1:1 as the complete non-diegetic music track for this segment. Preserve the original timing, tempo, pitch, dynamics and all lyric/onset positions exactly. Do not restart the full song, loop the slice, retime it, replace it or add another score.
```
占位符必须替换为真实值；`detailed_description:` 全小写。歌词用 `<d>[Language] 原文</d>`，按 lyric_events.local 分配口型；原音频是旁白/外部歌声时明确人物嘴部状态。

### 官方标签与写法细则（Rev1.0 §9.5-9.9 全量经验）
- **标签纪律**：`<Picture 1>`（非 `<picture1>`）大小写空格一致；一个标签一个含义全文不变；不创建未上传的 `<Picture 2>/<Video 3>/<Subject 4>`；仅定义外貌的图不必单做 retention 项；视频只参考镜头路径时明确"不复制其人物/服装/环境"；音频只参考节拍时标 `reference`，不写 `fully_copy`。
- **跨镜声音标签**：对白/歌声跨 Shot 连续用 `<scenetrans>`；音频/台词在片尾被截断用 `<cutoff>`。
- **Shot 切点语法**：`[Shot 1]` 无时间戳；`[Shot 2] At 00:03.500, the camera cuts to ...` 严格递增、位于时长内；正文动作切点与 Shot 切点必须同一套局部时钟（不得正文 3.700 切点写 3.415）。
- **运镜句式**：`The camera performs a [motion type] with [amplitude] at [speed] as [subject action].` 再补物理机位（起始位置/高度/距离/路径/触发/结束构图）。禁止 `[Zoom in][Pan left][Shake]` 式伪 token——`[Shot N]` 是结构标记，`[CAMERA]/[CUT 1]/[ACTION]` 只是普通文本标题。
- **语义准确**：Push in=机身前移≠Zoom（焦距）；Truck=机身横移≠Pan（原地摇）；Pedestal=机身升降≠Tilt（俯仰）；Arc 必须给出真实空间弧线路径；Static 要明写 fixed/locked；手持晃动要有动机与幅度。
- **声音字段分工**：`overall_soundscape`=环境声/脚步衣料接触声/非语言呼吸（1-4 句），不重复台词、不凭空加掌声人群；`non_diegetic_music`=`<Audio 1>` 1:1 复用明确句（不重启/不循环/不 retime/不替换/不加新配乐）或写具体风格参考；角色听得到音源（手机/音箱）属画内音，写进主时间线。
- **口型**：只在舞蹈设计+JSON 人声事件+用户要求共同支持时安排；speaker ID 如 `(S1)` 逐行按 `lyric_events.local_start/end` 分配；口型不破坏动作链完整性；原音频是旁白时明确嘴部状态（不无意对口型）。
- **语言**：H3 正文英文自然语言；歌词/对白保留原文包 `<d>[Language] ...</d>`；中文导演笔记、K 编号、未解释缩写不进 H3 正文。
- **OVERALL CONTINUITY 段**：一段话写同人物/同世界/同服装/无计划外道具角色/动作连续/终态；不复述大段 negative prompt，少量具体可验证约束+说明正确状态。

### Rev1.0 实战教训（来自《星星也在眨眼》SEG02-08 项目复盘，直接套用）
- **边界 onset**：距段尾 <0.1s 的鼓点（如 13.341s 鼓点 vs 13.385s 段尾）不安排需完整展开回收的大动作。
- **歌词稀疏≠停住**：某段只有 2 个 lyric_events 时中间仍有持续音乐——用持续层/重心/恢复填充，不让舞者定住。
- **phrase 贴片头**：第一个 phrase 在 0.079s 时只当乐句起点定义，不硬塞完整复杂动作（动作结果需真实完成时间）。
- **相邻段风格过近**：不平均改两段——保留一段签名、彻底改另一段的主动作语法+相机路径。
- **"不要直拍"类需求**：用实体机位/侧向运动/低位高位变化/空间关系落实，不写 "dynamic camera" 了事。
- **段尾错误清单**：每段都摆正面 Hero pose、每段末尾都甩发（甩发成唯一转场手段）、只写 "match cut to next segment" 无动作状态、出态只在 MD 表不进正文、删段后仍写"接下一段"、开放续写需求却做了定格鞠躬片尾卡。
- **回测归因表**（生成后按表定位问题层，一次只改一个变量）：脸/身材变=参考分配或视觉锁｜背景漂移=环境锁与机位冲突｜摆姿势无连接=链缺进入路径/重心/回收｜动作多变抱臂摇晃=时间窗过载｜没踩歌=local/global 或 beat phase 或 onset confidence｜相机迟到=相机与身体分家设计｜镜头一直正拍=分镜无新信息｜脚步看不清=景别与机位高度｜近景脸变=推拉过频｜切后动作重置=转场只写术语｜发/裙无惯性=物理层缺失｜多出道具=参考含糊或歌词字面化｜写真变慢摆=姿态占时过多｜段间像重复舞=无差异矩阵。

## 5. 项目级 MD 母模板（交付容器）
```markdown
# 《<项目名>》H3 <风格> MV 提示词（SEG__–SEG__）
**版本 / JSON / 动作库 Rev / 保留段 / 删除段 / 总时长 / 原曲区间 / BPM / 主风格 / 参考模式**
## 0. 输入素材与使用方法（<Picture 1>/<Audio 1>/<Video 1> 表）
## 1. JSON 解析与时间轴（分段总表：seg/start/end/length/file/歌词数）
## 2. 全片导演方案（风格语法/人物环境锁定/持续层/摄影机总原则/差异矩阵）
## 3. 动作链选择与改编（SEG|链号|来源|取用|入态|出态|时间窗）
## 4. 段间转场总表（转场六要素逐行）
## 5. 分段提示词（每段：SEG 元数据块 + H3 代码块全文）
## 6. 最终转场执行表
## 7. 生成前自检（五层）
```
段元数据块格式：`SEG__ — 主题 / 音频：<文件> / 原曲区间 / 本段时长 / 歌词事件(local) / 节奏锚点(phrase/downbeat/onset) / 动作链 / 入态 / 段尾出态`。

## 6. 核心纪律速记
- **动作三层**：持续层（每段一个主引擎：宅舞内八膝弹/抖舞胯八字/古风提沉呼吸/K-pop 胸肩隔离+重心弹性）+ 动链层（2-8 拍链，十要素展开）+ 微表情层（反拍眼神/腕指/肩/发丝）。
- **链接五步**：支撑预载→动力传递（脚→骨盆→胸→肩→肘→腕指）→唯一主要重拍→惯性回收→下动作入口。上链出态=下链入态；禁"站回正面"式无据重置。
- **时间窗容量**：0.3-0.6s 一个短促 hit；0.6-1.2s 短链；1.2-2.5s 复合句；Hero 动作独立容量。过载信号（抱臂摇晃/原地抖动/无完成点）→删动作，不靠形容词救。
- **旋转≤2/支**；跳跃写蹬地+腾空+落地吸收；静止写具体时间+音乐落点。
- **NO DEGREE LAW**：禁 `45-degree angle/low angle` 等角度标签；写承载方式+起始位置+离地高度+距离+朝向+路径(truck/dolly/arc/jib)+触发动作+结束构图。Push≠Zoom、Truck≠Pan、Pedestal≠Tilt。
- **相机 1:1**：同时启动/同步运动/峰值同步/同步恢复/连续衔接/绝对时间码。
- **转场六要素**：前段出态/动量/剪辑触发/剪辑机制(Match-on-Action|Hair-whip match|Foreground wipe|Whip-pan masked cut|Contact cut|Shape match|Continuous move)/后段入态/后段运镜。转场总表在 MD，入态出态必须各自写进相邻两段 H3 正文。
- **歌词**：语气与结构参考；仅需要口型时按 lyric_events 逐行对齐；空隙用持续层填充。
- **差异矩阵**：每段一个主动作语法+一次要语法+主机位签名+本段签名+禁止复用清单——编舞前完成，不等回测补救。
- **回测归因**：脸变=参考锁；动作摆拍化=链不完整/容量过载；没踩歌=local/global 或 beat phase 错；相机迟到=时间码分家；段间重置=转场只写术语。一次只改一个变量。

## 7. 交付与自检
最终交付：完整 MD 主文件 +（需要时）筛选后 JSON + 音频映射表 + 版本信息（MD Rev/JSON 来源/动作库 Rev/H3 模式/日期）。五层自检：A JSON 时间轴（length=end-start、local/global 不混、相位不归零、边界 onset 不排大动作）/ B 概念动作（差异矩阵、三层、容量、Hero、歌词不字面化）/ C 相机分镜（Shot 递增覆盖、物理机位、1:1、术语准确）/ D 段间转场（出态入态正文双写、惯性不清零）/ E H3 语法（模式字段顺序、标签一致、fully_copy vs reference、无中文分析入正文、无占位符残留）。
