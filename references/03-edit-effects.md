# 03 — 剪辑/定格/漫画叠加特效识别与写法

## 1. 先分层：现场动作 ≠ 后期特效

成片拆四层分别落字段：
1. **现场动作层**（人物真实做了什么）→ `integrated_multimodal_description` / Ref2VA 的 `detailed_description`
2. **运镜层** → `camera_direction`
3. **剪辑特效层**（定格、白闪、漫画图形、变速、转场）→ `editing`
4. **声音层** → `overall_soundscape` / `non_diegetic_music`

最常见错误：把后期定格写成"人物停住不动"，把漫画集中线写成现场背景。

## 2. 定格 freeze-frame 识别

判据（同时满足）：连续多帧像素近乎不变持续约 0.3–0.8s；常伴一帧白/黑闪、微推 punch-in、图形叠加或声音"真空"；前后动作连续（不是硬切场景）。

每个定格记录**四要素**：
1. **入点**（精确到 0.1s，与 RMS 峰对齐校验）；
2. **时长**（一般 0.5–0.6s）；
3. **叠加层**（白闪/集中线/网点/拟声字/冲击星/汗滴/边框/accent 色）；
4. **回到实拍方式**（数帧内 snap off、无残留、恢复正常速度色彩）。

## 3. 简单白闪定格（无漫画元素）

时间线内：
```text
[00:06.2] FREEZE-FRAME GAG 1: the image locks for roughly half a second on [被定格画面], a tiny punch-in zoom and a single white flash mark the frozen frame, comedic shock hold.
[00:06.8] Motion resumes: [恢复动作].
```
`editing` 汇总：
```text
three deliberate comedic FREEZE-FRAME holds at [...], each about 0.5s, each accented by a micro punch-in zoom and a one-frame white flash, then cleanly resumes — a classic three-beat shock-gag rhythm.
```

## 4. 漫画叠加定格（需要漫画风时）

### 4.1 统一工艺写进 `editing`
```text
EVERY freeze follows the same manga post-VFX recipe:
(1) live action hard-freezes;
(2) the frozen frame is instantly stylized into a Japanese-manga panel — heavy black ink outlines, high-contrast B&W grading, screentone/halftone dot shading, a thick black panel border;
(3) 2D graphic elements burst on top — radial concentration lines / impact starburst / screeching speed lines, one bold outlined onomatopoeia word, one exaggeration symbol;
(4) exactly ONE accent color is preserved per gag while everything else goes manga monochrome;
(5) the graphics do a single quick pop-and-shake, then the overlay snaps away in a few frames and normal full-color photorealistic live action resumes with no residue.
```

### 4.2 三种递进漫画元素配方
| 情绪 | 线条 | 拟声字（可换日/中文） | 夸张符号 | accent 色 |
|---|---|---|---|---|
| 自作自受·震惊 | 放射集中線 | `!?` | 大汗滴、汗线 | 角色标识色 1 |
| 误伤·命中 | 锯齿星爆环+冲击放射线 | `SPLAT!!` | 叉形爆点、描边水滴 | 被打者服装色 |
| 急停·呛住 | 横向速度线堆叠成刹车感 | `COUGH!!` | 头顶裂痕闪电、青筋 | 道具色 |

拟声字可换日文 `ズビシャ!! / ゴホッ!!`、中文 `噗！！/ 咳咳！！`，但 negative 必须声明 `graphic SFX typography, never sentence subtitles`。

### 4.3 防漂移（写进 negative_constraints）
```text
no turning the whole video into anime — live action stays photorealistic outside the freeze frames;
no manga residue after each overlay snaps off;
no freeze frames or manga effects outside the specified beats;
onomatopoeia must be graphic SFX typography, never sentence subtitles;
no oversized cartoon water in live footage (cartoon stylization exists ONLY inside freeze overlays).
```

## 5. 其他剪辑形态

- **一镜到底**：`One unbroken take, no hard cuts, no dissolves, no speed ramps`；景别变化只通过手持运动。
- **硬切**：只在有意义的视觉变化时切并做 match-on-action（方向/速度/动量连续），禁止按秒数切；多镜头 cut 语法见 `shot-syntax.md`。
- **变速**：slomo 只在明确看到时写，写清减速区间与恢复点；定格 ≠ 慢动作。
- **转场**：优先用运镜/能量变化表达段落边界。

## 6. 定格特效音（写进 overall_soundscape，不是音乐字段）

```text
On EACH freeze frame: a short record-scratch/rewind squeal leading into a punchy impact hit
(a crisp percussive "DON" with comic pop tail), then a roughly half-second near-silence
vacuum while the hold lasts, ambient sound snapping back the instant it clears.
```
