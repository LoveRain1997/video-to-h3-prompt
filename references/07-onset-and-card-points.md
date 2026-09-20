# 07 — 音头检测与卡点时间对账（onset / card points）

音频通道有两种粒度，用途不同，不能混用：

- **RMS 能量包络（0.5s，`audio_probe.py`）**：回答"哪里响、能量峰在哪"，用于判有无 BGM、对账大爆炸/齐射等能量事件。
- **音头 onset（`onset_probe.py`）**：回答"每一次弹拨/重音精确发生在哪一帧"，用于把**切镜、定格、命中、冲击、爆发**逐个钉到时间轴。卡点剪辑必须用 onset，RMS 太粗会把相邻两个重音糊成一个峰。

---

## 1. 跑音头检测（仅依赖 numpy + scipy，无需 librosa）

```powershell
# 先取单声道 wav（forensic_probe 已产出 audio.wav）
ffmpeg -y -i "IN.mp4" -vn -ac 1 -ar 22050 audio.wav
python scripts/onset_probe.py audio.wav
python scripts/onset_probe.py audio.wav --csv onsets.csv        # 导出每个分级音头
```

输出三块：

1. `ref_tempo`：包络自相关估的参考速度。**自由散板/轮指独奏（琵琶、古筝、散板戏曲）不可信**，仅作记录。
2. `STRONG / HARD onsets`：强(S，>85 百分位)/硬(H，>70 百分位)音头时间，就是卡点候选；`.` 是轮指等弱音头（造密度，不卡大切）。
3. `per-1s density / max-strength`：逐秒音头密度与最强音，画出乐句/能量轮廓（哪里密=高潮，哪里疏=留白）。

阈值可调：`--strong-q 0.85 --hard-q 0.70 --min-spacing 0.055`。

> 环境注记：Python 3.14 等新版本上 librosa 常无预编译 wheel（依赖 numba/llvmlite）。**不要强装**，直接用本脚本；它用 STFT→高频加权 spectral flux→find_peaks 自写检测，结论与 librosa onset_detect 在卡点用途上等价。

---

## 2. 固定节拍 vs 自由散板（决定能不能写 BPM）

| 观察 | 结论 | 提示词写法 |
|---|---|---|
| onset 间隔近似等距、自相关 tempo 稳定、频谱有低频 kick 网格 | 固定节拍 | 可写 BPM/拍号，事件可挂 `Beat N strong/weak` |
| onset 间隔不匀（std/mean 大）、自相关 tempo 低置信、无 kick 网格、轮指密集 | **自由散板 rubato** | **禁止写 BPM/拍数/节拍器**；写 `on the strong pipa accent of <Audio 1>`，再用时间码把关键卡点钉死 |

散板不等于没有卡点——它是"跟乐句重音卡点"（phrase-synced），重音位置不匀但剪辑照样逐个对齐。

---

## 3. 音画卡点对账表（核心工作模板）

把 S/H onset 与密帧/分镜表逐点对账，每行一个卡点：

| onset 时间(源) | 强度 | 画面事件 | 是否硬切/特效 | 段内时间(分段后) |
|---|---|---|---|---|
| 1.75 | S | 反打受害者正面警觉 | ✅硬切 | 01.75 |
| 6.69 | S | 首轮连射重击 | | 06.69 |
| 12.04 / 12.26 | S/S | 火力高潮双重击 | | 12.04 / 12.26 |
| 22.55 | H | 硬切背肩近景、开始回头、转暖调 | ✅关键硬切 | 07.55 |
| 28.51 | S | 白光气场 + 故障 + 黑翼爆发 | 特效 | 13.51 |

规则：
- **每个硬切 / 定格 / 冲击 / 齐射 / 爆发都应能在 ±0.1s 内找到一个 S/H onset**；找不到的切点要回查帧（可能是误判 cut）或标为"动作内切换"。
- 反过来，每个强 onset 不一定要切镜，但**大段落转折（硬切、爆发、情绪转场）几乎必踩强 onset**。
- 挑出 6–10 个**一级卡点锚点**（最大硬切、火力高潮、情绪转场、结尾爆发），写进提示词最显眼处；其余交给"on the accent"。

---

## 4. 把卡点写进 H3

- 时间轴每个关键镜头/事件后挂音频：`[00:06.6] on the strong accent of <Audio 1>, she opens fire ...`；硬切点写 `a hard cut lands exactly on the <Audio 1> accent at 00:07.5`。
- 顶部音频权威声明：`Use <Audio 1> as the ONLY temporal and rhythmic reference ... every cut, hit, freeze and burst synchronizes to <Audio 1>. Do not invent a separate rhythm.`
- 散板在 `non_diegetic_music` 写 `fully_copy <Audio 1>`（提供音频时），并描述其自由节奏性格（lunzhi tremolo / saoxian sweep / free-tempo rubato），**不写 BPM**。
- 节奏曲线与剪辑同构：用逐秒密度轮廓描述"紧→松→爆"，并写成剪辑指令。例：前段 onset 密集→快切；硬切后 onset 变疏、间隔拉长→近锁定长镜（慢回头/怒视），只在单音重弹上给极小动作；结尾一个最强 onset→爆发。

---

## 5. 自动切镜检测与"火光伪 cut"排除

```powershell
# scene 检测（0.3 宽松找候选，0.4 严格找硬切）
ffmpeg -i "IN.mp4" -filter:v "select='gt(scene,0.4)',showinfo" -f null - 2>&1 |
  Select-String "pts_time"
```

- **枪口火光、爆炸闪光、能量光束、白闪会被 scene 检测误报成切镜**（亮度突变但机位连续）。每个候选切点必须密帧核对：闪光前后机位/构图/角度连续＝同一镜头，不是 cut；只有机位、角度或景别真正跳变才算硬切。
- 战斗片常在齐射瞬间产生一簇伪 cut（如 7.0/10.7/14.1 附近），不要照单全收进镜头数。
- 最终 `镜头数 = 真硬切数 + 1`，与 ffprobe 时长 ±0.02 校验。

---

## 6. 烧时间码 contact sheet（机位/卡点一图核对）

逐格判机位与卡点时，抽帧并把时间码烧进画面再拼网格，避免数帧错位：

```powershell
# 4fps、烧时间码（左上）、缩放后拼 4x4，每张覆盖 4 秒
ffmpeg -y -i "IN.mp4" -vf "fps=4,scale=320:-1,drawtext=text='%{pts\:hms}':x=6:y=6:fontcolor=yellow:fontsize=18:box=1:boxcolor=black@0.6,tile=4x4:padding=3:color=yellow" -vsync 0 sb_%02d.jpg
```

Windows 无中文字体时 drawtext 用默认字体即可；时间码格式按 ffmpeg `pts` 支持的写法。用这组带码网格逐段定机位，再与 onset 表对账。

---

## 7. 工程坑

- **中文/空格路径**：源文件名含中文、空格（如 `琵琶曲 _ xxx.mp4`）直接喂 ffmpeg/ffprobe 易乱码或断参。先复制成纯英文工作副本再分析：
  `Copy-Item "源.mp4" ".\work\input.mp4"`，所有取证对 `input.mp4` 做。
- 路径含空格一律加引号；PowerShell 反引号续行。
- onset 只给"时间点"，不给"该拍什么"——画面内容仍以密帧分镜为准，二者对账后才落提示词。
