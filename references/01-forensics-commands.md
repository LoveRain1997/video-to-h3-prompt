# 01 — 取证命令库与音画交叉验证

跨平台：Windows 用 PowerShell（本仓库 `ffmpeg-cheatsheet.md` 亦为 PowerShell 风格），macOS/Linux 用 bash。`IN.mp4` 替换为实际视频，路径含空格必须加引号。

## 1. 媒资建档

```powershell
# PowerShell
ffprobe -v error -show_format -show_streams -of json "IN.mp4"
```

记录：duration / width×height / r_frame_rate / 视频编码 / 音轨（codec、sample_rate、channels）。竖边更长=9:16，横边更长按 16:9、4:3 归类。

## 2. 全片稀疏抽帧（骨架层）

```powershell
# 2fps、统一宽 480
ffmpeg -y -i "IN.mp4" -vf "fps=2,scale=480:-1" frames/f_%02d.jpg
```

按片长定间隔：<5s→0.2s；5–10s→0.3–0.4s；10–15s→0.15–0.2s；>15s→0.2s + 转折补抽。

## 3. 拼 contact sheet 一次看全

```powershell
# 4 列 4 行，黄边便于读序；超过 16 帧会输出 grid_001/002 ...
ffmpeg -y -framerate 1 -i frames/f_%02d.jpg -vf "scale=240:-2,tile=4x4:padding=4:color=yellow" grid_%03d.jpg
```

## 4. 转折区间密帧（判别层）

```powershell
# -ss 起点 -t 持续；4fps，必要时 fps=8
ffmpeg -y -ss 8.5 -t 2.5 -i "IN.mp4" -vf "fps=4,scale=360:-1" seg/c_%02d.jpg
ffmpeg -y -framerate 1 -i seg/c_%02d.jpg -vf "scale=200:355,tile=5x2:padding=3:color=yellow" seg/c_grid.jpg
```

## 5. 原分辨率单帧终核

```powershell
ffmpeg -y -ss 9.8 -i "IN.mp4" -frames:v 1 -q:v 2 key_9_8.jpg
```

## 6. 提音频（22.05k 单声道足够分析；只做响度时 8k 即可）

```powershell
ffmpeg -y -i "IN.mp4" -vn -ac 1 -ar 22050 audio.wav
```

## 7. 频谱图（判音乐 vs 现场）

```powershell
ffmpeg -y -i audio.wav -lavfi showspectrumpic=s=1000x400:legend=1 spectrum.jpg
```

- **等间隔等宽低频竖纹贯穿全片** → 鼓机/节拍，存在 BGM；
- **宽带随机能量 + 偶发上扬谐波曲线** → 人声说/笑/喊；
- **全频段持续铺底** → 环境底噪（街道、风、发动机）；
- 定格/喷溅瞬间的竖向亮块 → 瞬时音效，与画面事件对齐。

## 8. RMS 能量包络 + BPM 可信度

```powershell
python scripts/audio_probe.py audio.wav
```

**BPM 误检判据（同时满足判"无稳定 BGM"）**：
1. `onset std / onset mean > 0.8`（节拍不规律）；
2. 频谱无等间隔 kick 网格；
3. RMS 高峰是离散瞬时峰而非周期性起伏。
三条齐备时 librosa 的 BPM 是把随机 onset 误当节拍，结论写「无 BGM，全同期声」。

## 9. 响度补充判据（volumedetect）

```powershell
ffmpeg -y -i "IN.mp4" -vn -ac 1 -ar 8000 -f wav out8k.wav
ffmpeg -i out8k.wav -af "volumedetect" -f null NUL 2>&1 | Select-String volume   # PowerShell
# bash: ... -f null - 2>&1 | grep volume
```

mean/max volume 与配乐 recipe 的对应见 `audio-heuristics.md`。

## 10. 音画交叉验证矩阵（工作模板）

| RMS 能量峰时刻 | 密帧画面证据（谁先动/方向/结果） | 候选解释 → 裁决结论 | 落点字段 |
|---|---|---|---|
| 5.5–7.0s | 绿手先按头盔，随后水糊在自己面罩 | 互喷？×／被打断自呛？√ | integrated + editing(freeze1) + soundscape |
| 9.5–10.5s | 绿手掰头盔向右转，随后 B 脸前水花 | B 自己喷？×／被改向误伤？√ | integrated + editing(freeze2) |
| 12.5–14.0s | B 仰头喝→绿手伸入→嘴边呛出 | 喝呛？×／反击被打断？√ | integrated + editing(freeze3) |
| 全程 | 无 kick 网格、onset std>mean | 117BPM 误检 → 无 BGM | non_diegetic_music=silence |

规则：**每个 RMS 峰都要在画面里找到成因；每个关键动作都要在音频里找到印证**。对不上的行就是待查歧义点，回 Step 4 密帧或进入提问流程。

## 11. 一键取证

```powershell
# Windows PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/forensic_probe.ps1 -Video "IN.mp4" -OutDir forensic_out
```
```bash
# macOS / Linux
bash scripts/forensic_probe.sh "IN.mp4" forensic_out
```

产出：2fps 帧、全片网格、audio.wav、spectrum.jpg、probe 信息与 RMS/BPM 表。之后人工进入密帧判别与因果重建。
