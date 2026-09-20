# 01 — 取证命令库与音画交叉验证

跨平台：Windows 用 PowerShell（本仓库 `ffmpeg-cheatsheet.md` 亦为 PowerShell 风格），macOS/Linux 用 bash。`IN.mp4` 替换为实际视频，路径含空格/中文必须加引号（中文路径建议先复制为纯英文副本，见 §12）。

## 1. 媒资建档

```powershell
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
# -ss 起点 -t 持续；4fps，判别 burst/掰头/火光时上 fps=8
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
- **定格/喷溅/命中瞬间的竖向亮块** → 瞬时音效，与画面事件对齐。

## 8. RMS 能量包络 + BPM 可信度（粗粒度：哪里响）

```powershell
python scripts/audio_probe.py audio.wav
```

**BPM 误检判据（同时满足判"无稳定 BGM"）**：
1. `onset std / onset mean > 0.8`（节拍不规律）；
2. 频谱无等间隔 kick 网格；
3. RMS 高峰是离散瞬时峰而非周期性起伏。
三条齐备时 librosa 的 BPM 是把随机 onset 误当节拍，结论写「无稳定 BGM」。

## 9. onset 音头检测 + 卡点（细粒度：每个重音在哪一帧）

RMS 0.5s 太粗，卡点剪辑（切镜/定格/命中/爆发对齐音乐）必须用音头：

```powershell
python scripts/onset_probe.py audio.wav
python scripts/onset_probe.py audio.wav --csv onsets.csv
```

输出：强(S)/硬(H)音头时间（卡点候选）、`.` 轮指弱音、逐秒密度/强度轮廓（乐句形状）、自相关参考 tempo。**自由散板/轮指独奏（琵琶等）的 tempo 低置信度，不可当节拍器**。详见 `07-onset-and-card-points.md`。该脚本仅依赖 numpy+scipy，无需 librosa。

## 10. 硬切检测与"火光伪 cut"排除

```powershell
# scene 阈值 0.4 找硬切（0.3 宽松找候选）
ffmpeg -i "IN.mp4" -filter:v "select='gt(scene,0.4)',showinfo" -f null NUL 2>&1 | Select-String "pts_time"
```

**枪口火光、爆炸闪光、能量光束、白闪会被误报成切镜**（亮度突变但机位连续）。每个候选切点密帧核对：闪光前后机位/角度/景别连续＝同一镜头；只有机位真正跳变才算硬切。战斗片齐射瞬间常出现一簇伪 cut，不照单全收。最终 `镜头数 = 真硬切数 + 1`。

## 11. 烧时间码 contact sheet（机位/卡点一图核对）

```powershell
# 4fps、左上烧时间码、拼 4x4（每张覆盖 4 秒），逐段定机位再与 onset 对账
ffmpeg -y -i "IN.mp4" -vf "fps=4,scale=320:-1,drawtext=text='%{pts\:hms}':x=6:y=6:fontcolor=yellow:fontsize=18:box=1:boxcolor=black@0.6,tile=4x4:padding=3:color=yellow" -vsync 0 sb_%02d.jpg
```

## 12. 响度补充判据（volumedetect）

```powershell
ffmpeg -y -i "IN.mp4" -vn -ac 1 -ar 8000 -f wav out8k.wav
ffmpeg -i out8k.wav -af "volumedetect" -f null NUL 2>&1 | Select-String volume   # PowerShell
# bash: ... -f null - 2>&1 | grep volume
```

mean/max volume 与配乐 recipe 的对应见 `audio-heuristics.md`。

## 13. 音画交叉验证矩阵（工作模板）

| RMS 峰 / 强 onset 时刻 | 密帧画面证据（谁先动/方向/结果/机位） | 候选解释 → 裁决结论 | 落点字段 |
|---|---|---|---|
| 1.75s（S onset） | 反打受害者正面警觉，机位跳变 | 连续运镜？×／硬切？√ | editing(cut) + camera |
| 6.6–7.0s（S onset + RMS 峰） | 枪口火舌，随后贴臀机位冒火花 | 火光伪 cut？√（机位连续）／真切？× | integrated + soundscape |
| 11–12.5s（密集 S/H onset + RMS 最高峰） | 双枪齐射、高俯拍趴地连中 | 火力高潮，一串卡点 | integrated + editing + music |
| 22.55s（H onset） | 硬切背肩近景、转暖调、开始回头 | 关键硬切（情绪转场）√ | editing + camera + lighting |
| 28.51s（S onset） | 白光 + RGB 故障 + 黑翼爆发 | 后期特效爆发，对齐尾音 √ | editing(特效) + soundscape(boom) |
| 全程 | onset 间隔不匀、无 kick 网格 | 72.8BPM 误检 → 自由散板，不写 BPM | non_diegetic_music=fully_copy+rubato |

规则：**每个硬切/定格/冲击/爆发都要在 ±0.1s 内找到 S/H onset；每个 RMS 峰都要在画面里找到成因；每个关键动作都要在音频里找到印证**。对不上的行回 §4 密帧或进入提问流程。

## 14. 一键取证

```powershell
# Windows PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/forensic_probe.ps1 -Video "IN.mp4" -OutDir forensic_out
```
```bash
# macOS / Linux
bash scripts/forensic_probe.sh "IN.mp4" forensic_out
```

产出：2fps 帧、全片网格、audio.wav、频谱、probe 信息、RMS/BPM 表与 **onset 卡点表**。之后人工进入密帧判别、片型分流（`06`）与因果重建。
