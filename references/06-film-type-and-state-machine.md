# 06 — 片型分流与相机状态机（连续运镜 / 编辑式快照 / 多镜头快剪）

取证做完、动笔写 H3 之前，**先判片型再选状态机**。同一段"镜头很快、很有冲击力"的画面，可能是三种完全不同的机制，套错状态机是反推提示词失败的首要原因——把多镜头快剪套进"硬锁/爆发"两态，会错误压制必要的切镜；把编辑式快照写成连续运镜，模型就会在该静止的地方漂移。

---

## 0. 六条可复用检查清单（每次反推先过一遍）

1. **先判「连续运镜」还是「离散快切」**：对转折段用 8fps 以上密帧，别让稀疏采样跨过整个 burst；在帧序列里找「运动 — 完全静止」的**台阶**。有台阶＝离散编辑；全程连续位移＝运镜。
2. **音频做时间轴对账**：每个切换 / 定格 / 冲击是否挂在节拍 onset 上（用 `scripts/onset_probe.py`）？**是 → 编辑式快照/卡点剪辑**；否 → 才考虑自由运镜。
3. **有参考图就别写外貌**：图锁外观（脸、发型、服装、配饰），文字只写相机 / 时间 / 状态机 / 环境道具。外貌文字与图并用会诱导模型重设计。
4. **静态与爆发写成两个互斥状态**：静态段把「不许慢动作 / 漂移 / 继续运动 / 残留动量」反复写死（在时间轴、相机规则、negative 多处重复）。
5. **横置先怀疑相机 Roll**：画面"人物躺了/横了"时，先看**地平线与身体的相对关系**——地平线一起转＝相机 Roll，身体没转；地平线水平、只有人物转＝人物真的躺/转。别轻易判定人物躺下。
6. **冲击要可数、不可糊**：连续三下冲击必须分别可读（如 IMPACT1 位移 / IMPACT2 前推 / IMPACT3 旋转微震），明确写「不是连续震动、不是随机抖动」，且**只动相机、不变形人物**。

---

## 1. 三型分流决策表

| 判据（密帧 + onset 对账） | 片型 | 相机机制怎么写 |
|---|---|---|
| 全程一条连续机位，景别靠手持/推拉变化，无 composition 台阶；可有定格 gag | **A 一镜到底 continuous take** | 一条 handheld/locked 基线 + 每次运镜的动机；定格作为同镜头内事件（见 `03-edit-effects.md`） |
| 画面由**离散的静态构图**组成，构图之间是极短爆发，静态段相机**绝对零运动**；切换/冲击精确挂 onset | **B 编辑式快照 editorial snap** | 两态互斥状态机 `HARD LOCK ↔ INSTANT BURST`（见 §3） |
| 多个机位/景别/角度**硬切正反打**，每个镜头有自己的机位，切镜挂乐句重音；无单一长镜 | **C 多镜头快剪 multi-shot montage** | **命名机位语法** named setups + 切镜纪律（见 §4），**不要**套两态 LOCK/BURST |

混合型按主导机制归类，少数异类镜头单独标注（例：多镜头快剪片里夹一个一镜到底的环绕长镜，或结尾转一个近锁定长镜）。

---

## 2. A 型 — 一镜到底（continuous take）

判据：contact sheet 上构图连续演变、无角度/景别跳变；`blend=difference` 相邻帧是平滑渐变而非整帧翻转。

写法要点：
- 开头定基线机位（POV / 第三人称、景别、角度、手持幅度）；
- 每次运镜给 `类型 + 幅度 + 速度 + 动机`（什么身体动作/事件触发）；
- 明确 `One unbroken take, no hard cuts, no dissolves, no speed ramps`；
- 定格/白闪/漫画 gag 是同镜头内的 `FREEZE-FRAME GAG n`，不是 cut（见 `03-edit-effects.md`）；
- 多数 prank/UGC 反转属此型。

---

## 3. B 型 — 编辑式快照（editorial snap）：两态互斥状态机

判据：帧序列里反复出现「极短高速重构图 → 立刻完全静止并保持」的台阶；每个台阶边界对齐 onset。代表作是身体部位逐级揭示（脚→膝→上身→脸）一类的 snap-lock 剪辑。

### 3.1 显式定义两个互斥状态（开头命名，全文复用）

```text
The camera alternates between exactly two states, never blended:
STATE A — HARD LOCK: camera = ABSOLUTE ZERO MOTION. No translation, zoom, push,
pull, pan, tilt, orbit, roll, drift, parallax, handheld motion, micro-shake or
residual momentum. The composition behaves like a still photograph held on screen.
STATE B — INSTANT BURST: camera movement occurs ONLY inside the named burst interval;
it starts immediately, is extremely fast, ends immediately, with strong directional
motion blur. No ease-in, no ease-out, no smooth interpolation. At the exact end of
every burst, CAMERA = ZERO MOTION.
Never blend the two; never interpolate continuously through a static section.
```

### 3.2 静态段把禁令反复写死（清单第 4 条）

每个静态时间块都重复一遍 `No zoom / push / pull / pan / tilt / drift / parallax / handheld / micro-shake / residual movement`，并在 `camera_direction` 与 `negative_constraints` 再各写一次。长 prompt 后半模型会弱化早期约束，**同一规则多处重复是故意的，不是啰嗦**。

### 3.3 可数冲击（清单第 6 条）

爆发收尾若有三下冲击，逐个命名、互不混淆：

```text
THREE DISCRETE CAMERA IMPACTS (not continuous vibration, not random jitter):
IMPACT 1 — a brief tiny positional jolt;
IMPACT 2 — a brief forward scale punch;
IMPACT 3 — a brief rotational micro-jolt.
Rhythm: THUMP → THUMP → THUMP → LOCK.
Only the camera receives the impacts; do not deform the face, head or body.
```

### 3.4 横置/ Roll 纪律（清单第 5 条）

- 需要"画面横过来"时写清楚是**相机 Roll**：`the character does NOT rotate, the body does NOT twist; the sideways look is created by camera orientation only`。
- 中段若要持续倾斜，写成一条持续规则（`maintain the tilted horizon through KNEE→...→NECK; do not level, do not counter-roll, do not alternate`），最终 Roll 只在结尾预留一次。

### 3.5 时间块与对账

- 每个 LOCK / BURST 给精确毫秒区间（`00:00.120–00:00.420 STATIC HERO 01`），块边界即 onset；
- 结尾给一张**时间预算总表**（逐块 start–end + 状态）+ 一张 NEGATIVE 大清单 + 一句话 final read（`PICTURE→SNAP→...→LOCK`）。

---

## 4. C 型 — 多镜头快剪（multi-shot montage）：命名机位语法

判据：硬切正反打、机位/角度在镜头间跳变（攻击者正面、被击者背面/俯拍等），切镜挂乐句重音；单个镜头内部可能手持运动，但**不存在跨镜头的单一连续相机旅程**。代表作：战斗/动作恶搞、MV 式快剪。

**关键：不要套 HARD LOCK / INSTANT BURST**——那会把必要的切镜当成"泄漏运动"压掉。C 型的"状态机"是**机位选择规则**。

### 4.1 先命名全片反复出现的机位（named setups）

在开头定义一套具名机位，规定每个叙事拍用哪个、角度景别、表达什么，禁止混用。例（战斗恶搞片）：

```text
GUNNER SHOT : frontal, camera slightly BELOW eye-level, medium/close, muzzle into lens (attacker POV) — dominant.
BUTT SHOT   : EXTREME LOW REAR camera near the floor at hip height looking up behind the victim, the hit zone centered — slapstick.
PRONE SHOT  : HIGH TOP-DOWN (~50°) on the victim when on the floor — weak.
WIDE SHOCK  : locked frontal/low wide for beam and explosion, action contained in a steady frame.
CLOSE INSERT: tight overhead / face / prop close-up.
ORBIT SHOT  : ONE continuous low-angle handheld arc circling the subject (front/back alternate).
STINGER CLOSE-UP : tight rear over-shoulder close-up, near-locked with a very slow push, background flips to bokeh — the turn/stare.
Use only the assigned setup per beat; never blend or invent camera moves.
```

### 4.2 机位编码权力关系与情绪

仰拍攻击者 / 俯拍或贴地仰拍被击者，是在用角度写强弱与喜剧；一个"帅气正面机位"紧接"狼狈俯拍/贴地机位"就是笑点机关。把这种**角度反差剪辑**显式写进 `camera_direction`，而不只是罗列景别。

### 4.3 切镜纪律（写进 editing）

- 切镜只在有意义的视觉变化（新机位/空间关系/运动状态/能量级/表演重点）时发生，并落在乐句重音 onset 上；
- `match-on-action`：跨切点保持运动方向、速度、身体焦点、手势轨迹、视觉动量；
- muzzle flash / 爆炸闪光**不是切镜**（见 `07` 的火光伪 cut）；
- 动静对比要写明：前段密集快切，某点之后**骤收成一个近锁定长镜**（如慢回头怒视），快→慢本身就是节奏设计。

### 4.4 每个 [Shot] 句首前置机位

每个镜头描述先给 `setup 名 + 景别 + 角度`，再给动作与同期声（六要素见 `shot-syntax.md`）。相机规则段再按时间码复述"哪一拍用哪个机位"，与时间轴互锁。

---

## 5. 反幻觉骨架：为什么"有效提示词"能一次跑通（七要素）

无论 B 型还是 C 型，高命中提示词共享同一套反幻觉结构：

1. **置顶权威声明**：图=唯一身份/服装来源；音频=唯一时间/节奏来源；（环境道具若由文字定义，也在此声明边界）。禁止自创节奏、禁止替换音频。
2. **显式状态机**：B 型命名 LOCK/BURST 两态；C 型命名机位集合。互斥、不混合、全文复用同一命名。
3. **精确时间块**：毫秒/0.1s 级，块边界对齐 onset；时间戳只标真实状态变化。
4. **相机绝对化**：把所有禁止项列全（zoom/pan/tilt/drift/parallax/handheld/orbit/slow-mo…），并说明唯一允许的例外。
5. **同一规则多处重复**：时间轴、相机规则、negative 各写一遍，防长 prompt 后半被弱化。
6. **零外貌文字**（有参考图时）：身份服装全归图，token 投给相机/时间/状态机；剧情手持道具（武器等）仍由文字定义。
7. **结尾三件套**：时间预算总表 + NEGATIVE 大清单 + 一句话 final read。

---

## 6. 分流自检（动笔前 30 秒）

- [ ] 密帧里有没有"运动→完全静止"的台阶？（有→倾向 B；全程连续→A；机位跳变→C）
- [ ] 切镜/定格/冲击是否对齐 onset？（对齐→B/C 卡点；不对齐→自由运镜 A）
- [ ] 我选的状态机和片型一致吗？（C 型绝不能套 LOCK/BURST）
- [ ] "横过来"是相机 Roll 还是人物转身？地平线核对了吗？
- [ ] 连续冲击是可数的几下，还是被我写成了"震动"？
- [ ] 有参考图时，外貌文字是否已删干净，只留相机/时间/状态机/环境道具？
- [ ] 静态段的禁令是否在时间轴、相机段、negative 三处重复？
