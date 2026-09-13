# 04 — 角色/Coser 替换 SOP（只换皮，不动骨）

适用指令：「用下面 coser 替换提示词里的 A/B，不要改任何动作剧情，只换外貌」。

## 1. 两层切分

### 冻结层（逐字保留）
全部时间戳与事件顺序、因果关系、谁先动/受力方向/payoff；运镜与机位；剪辑点与定格特效；声音事件与能量峰；音乐层。`camera_direction` / `editing` / `body_mechanics` / `overall_soundscape` / `non_diegetic_music` 原则上整体保留。

### 允许改动层（只改三处）
1. `subject_definitions`：整体外观重写；
2. `costume_hair_physics`：新发型/面料/眼镜/配饰的二次运动与湿身演化；
3. 动作句中**被动作点带到的服装/身体词**（水倒在 sandal → 倒在 tall boot；水溅到 white tee → uniform collar）。

超出这三处即剧情改动，必须在对照表「连带改动」显式声明原因。

## 2. 动作兼容性检查（新角色是否具备原动作部件）

| 原动作依赖 | 新角色情况 | 处理 |
|---|---|---|
| 可掀起的透明面罩 | 同样有可掀透明面罩 | 原样保留掀/合路径 |
| 可掀起的透明面罩 | 封闭镀膜面罩/无头头盔 | 改为「从面罩下缘缝隙吸入与喷出」；情绪用头盔朝向、姿态、特效（如黑烟）表达 |
| 露脸表情戏 | 头盔/面罩遮挡 | 用头盔朝向、身体姿态、闷声替代，不强行写面部 |
| 被喷脸 | 戴眼镜 | 加镜片挂水/起雾/下滑到物理字段与该动作句 |
| 长发甩动 | 短发/卷发 | 改物理字段：短卷发小团弹动、回弹更快 |
| 凉鞋/短裙 | 长靴/长裤 | 同步替换被动作带到的词（倒水点、湿身点） |

## 3. 道具入画纪律

- **剧情手持道具**（杯子、瓶子等推动剧情的）原样保留，不随角色换。
- **角色专属道具**分三级：
  1. 可静态佩戴（腰带、对讲机、胸袋钢笔、徽章）→ 写进 subject，注明不动、不参与打闹；
  2. 会引入新动作（刀剑、大型工具）→ 背在身后/收着，明确 never drawn / never used in the prank；
  3. 会引入新场景（专属载具、实验台）→ 原环境没有位置就**一律不入画**，对照表说明，避免改环境。
- negative 同步：no added props beyond ... / no drawing or using X as a weapon。

## 4. 动漫造型 → 真人 coser 现实化转译

1. subject 开头锁：`REAL-LIFE HUMAN COSPLAYER in photorealistic live-action footage — real skin, real wig hair, real fabric, NOT anime, NOT cel-shaded, NOT illustrated.`
2. 面料写实：呢料制服/金属扣/ABS 烤漆头盔/PC 透明面罩/真皮/树脂镜片/假发层次。
3. 敏感标识（警徽、制服标识）写 `fictional costume-replica insignia`；约束器具写 `toy/prop`。
4. 气质用真人可演的词（composed / gentle / wary），不写二次元滤镜词。
5. negative 兜底：`no anime/cartoon/cel-shaded look, photorealistic real cosplayers only; helmet stays on (only visor flips); no costume swap; no removing glasses.`

## 5. 替换后必附对照表（中文）

| 维度 | 原角色 | → 新角色（真人 cos） |
|---|---|---|
| 发型 / 面部·眼镜 / 头部（头盔帽） / 上装 / 下装 / 鞋袜 / 手部手套 / 静态配件 / 剧情手持道具（保留不变） / 未入画专属道具及原因 / 湿身物理 / 气质 | | |

表后声明：未改动层（时间戳/动作/运镜/定格/声音/音乐）零改动；列出全部连带改动点。

## 6. 操作顺序（防止顺手改剧情）

1. 复制底本，定位所有外貌词与服装词；
2. 整体重写 `subject_definitions`；
3. 逐句扫动作时间线，只替换被动作带到的外貌词，动作结构不动；
4. 重写 `costume_hair_physics`；
5. 最小增量更新 `negative_constraints`；
6. 其余字段逐字保留；
7. 随机抽 3 个时间戳与底本逐字比对动作描述，出对照表。
