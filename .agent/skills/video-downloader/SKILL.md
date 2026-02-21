---
name: video-downloader
description: 下载视频 + AI 内容摘要，支持画质选择、字幕下载、仅音频模式，自动判断语言并添加中文字幕，支持本地语音转录
---

# 视频下载与内容摘要 (Video Downloader & Summarizer)

使用 yt-dlp 下载网络视频，支持 YouTube、Bilibili、Twitter 等主流平台。**自动判断视频语言：非中文视频自动添加中文字幕。下载完成后自动生成 AI 内容摘要。**

## 触发方式

当用户请求下载视频时触发，识别以下关键词：
- "下载视频"、"下载这个视频"
- "download video"
- 直接粘贴视频链接

## 核心功能

| 功能 | 说明 |
|------|------|
| 🎬 视频下载 | 支持 1000+ 平台，自动选择最佳画质 |
| 🌐 自动中文字幕 | 非中文视频自动识别语音并添加中文字幕 |
| 📝 AI 内容摘要 | 自动获取转录文本，生成结构化中文深度摘要 |
| 🎙️ 本地语音转录 | 视频无字幕时，使用 faster-whisper 本地语音识别 |
| 📁 整理归档 | 自动创建结构化文件夹，按日期归档 |
| 🎵 音频提取 | 支持仅下载音频（MP3 格式） |
| 🧹 自动清理 | 临时文件超过 3 个时自动清理 |

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | ✅ | - | 视频链接 |
| `quality` | ❌ | `best` | 画质选项：`best`(最佳)、`1080`、`720`、`480` |
| `subtitle` | ❌ | `auto` | 字幕处理：`auto`(自动判断)、`true`、`false` |
| `audio_only` | ❌ | `false` | 仅下载音频：`true` / `false` |
| `output_dir` | ❌ | `download/` | 输出目录路径（自动创建子文件夹） |
| `subtitle_type` | ❌ | `1` | 字幕类型：0=不嵌入，1=硬字幕，3=硬双语字幕 |
| `source_lang` | ❌ | `en` | 源语言：`en`(英语)、`ja`(日语)、`ko`(韩语) |
| `summary` | ❌ | `auto` | AI摘要：`auto`(自动)、`true`(强制)、`false`(跳过) |

## 自动中文字幕规则

> **重要**：Agent 应自动判断视频语言，无需询问用户。

**判断逻辑**：
1. 获取视频标题后，分析标题语言
2. 如果标题为**英文、日文、韩文或其他非中文语言** → 自动执行字幕翻译
3. 如果标题为**中文（普通话或粤语）** → 跳过字幕翻译，直接完成下载

**语言代码对照**：
| 视频语言 | source_language_code |
|---------|---------------------|
| 英语 | `en` |
| 日语 | `ja` |
| 韩语 | `ko` |
| 法语 | `fr` |
| 德语 | `de` |

## AI 内容摘要规则

> **重要**：摘要功能默认开启，在视频下载完成后自动执行。

**判断逻辑**（当 `summary=auto` 时）：
1. 视频下载完成后，自动调用 Content Summarizer
2. 获取视频字幕/转录文本
3. **如果转录文本为空** → 使用 faster-whisper 进行本地语音识别（见 Step 8B）
4. 调用 AI 生成结构化中文摘要
5. 将摘要文件归档到下载目录

**摘要输出内容**：
- 📌 核心观点 (3-5条)
- 💡 关键洞察 (2-4条)
- ✨ 金句提取 (3-5条)
- 👤 嘉宾信息（如有）
- 📄 深度摘要正文 (~1500字)

## 文件夹命名规则

下载的文件会自动整理到结构化的文件夹中：

```
download/
└── {名称缩写}-{下载日期}/
    ├── 原始视频.mp4
    ├── 视频 [中文字幕].mp4（如有）
    ├── zh-cn.srt（中文字幕）
    ├── en.srt（英文字幕）
    ├── summary.md（AI 摘要）
    ├── transcript.md（原始转录）
    ├── transcript_raw.txt（原始语音转录，如有）
    ├── metadata.json（元数据）
    └── cover.jpg（封面图）
```

**命名规则**：
- **名称缩写**：从视频标题提取 1-3 个关键词，驼峰命名，如 `MultipleInterests`
- **下载日期**：格式为 `YYYYMMDD`，如 `20260128`
- **示例**：`download/MultipleInterests-20260128/`

## 使用示例

### 1. 基础下载（自动添加中文字幕 + AI 摘要）
```
下载这个视频：https://www.youtube.com/watch?v=xxxxx
```
> Agent 自动判断：若为英文视频，自动翻译中文字幕 + 生成 AI 摘要

### 2. 指定画质
```
下载这个视频，720p：https://www.youtube.com/watch?v=xxxxx
```

### 3. 仅下载音频
```
只下载音频：https://www.youtube.com/watch?v=xxxxx
```

### 4. 强制双语字幕（学习用）
```
下载视频，生成中英双语字幕：https://www.youtube.com/watch?v=xxxxx
```

### 5. 只下载不摘要
```
下载视频，不需要摘要：https://www.youtube.com/watch?v=xxxxx
```

---

## 执行流程

### Step 1: 获取视频信息

```powershell
# 获取视频标题
yt-dlp --get-title "<URL>"
```

**输出示例**：`If you have multiple interests, do not waste the next 2-3 years`

### Step 2: 判断语言并设置参数

根据标题语言自动判断：

| 标题语言 | 处理方式 |
|---------|---------| 
| 英文/日文/韩文等 | 设置 `need_subtitle=true`，确定 `source_lang` |
| 中文（简/繁） | 设置 `need_subtitle=false`，跳过字幕翻译 |

### Step 3: 创建输出文件夹

```powershell
# 从标题提取关键词，创建文件夹
# 示例：MultipleInterests-20260128
$folderName = "<名称缩写>-$(Get-Date -Format 'yyyyMMdd')"
New-Item -Path "download\$folderName" -ItemType Directory -Force
```

### Step 4: 下载视频

```powershell
# 下载最佳画质视频
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "download/<文件夹名>/%(title)s.%(ext)s" "<URL>"
```

**命令选项对照**：

| 用户需求 | yt-dlp 参数 |
|---------|-------------|
| 最佳画质 | `-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"` |
| 1080p | `-f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"` |
| 720p | `-f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"` |
| 仅音频 | `-x --audio-format mp3 --audio-quality 0` |

**后台执行**：
- 设置 `WaitMsBeforeAsync=500`，命令在后台运行
- 使用 `command_status` 每 15-30 秒检查进度
- 下载完成后继续下一步

### Step 5: 监控下载进度

```powershell
# 检查命令状态
command_status -CommandId <ID> -WaitDurationSeconds 15
```

等待 Exit code: 0 表示下载完成。

### Step 6: 添加中文字幕（如需要）

**仅当 `need_subtitle=true` 时执行此步骤**

使用 pyVideoTrans 进行语音识别和翻译：

```powershell
# 英译中，硬字幕（推荐）
D:\pyVideoTrans\.venv\Scripts\python.exe D:\pyVideoTrans\cli.py --task vtv --name "<视频完整路径>" --source_language_code en --target_language_code zh-cn --subtitle_type 1
```

**参数说明**：

| 参数 | 说明 |
|------|------|
| `--task vtv` | 视频翻译任务（识别→翻译→合成） |
| `--source_language_code` | 源语言代码（en/ja/ko 等） |
| `--target_language_code` | 目标语言：`zh-cn`(简体中文) |
| `--subtitle_type` | 1=硬字幕(烧录), 3=硬双语字幕 |

**监控翻译进度**：
- 使用 `command_status` 每 60 秒检查一次
- 翻译过程可能需要 10-30 分钟（视频长度相关）
- 等待 Exit code: 0 表示完成

### Step 7: 复制字幕输出文件

翻译完成后，将文件复制到下载目录：

```powershell
# pyVideoTrans 输出目录
$outputDir = "D:\pyVideoTrans\output\<视频名称-转义>\"

# 复制带字幕视频
Copy-Item -Path "$outputDir\*.mp4" -Destination "download\<文件夹名>\视频 [中文字幕].mp4"

# 复制字幕文件
Copy-Item -Path "$outputDir\zh-cn.srt" -Destination "download\<文件夹名>\"
Copy-Item -Path "$outputDir\en.srt" -Destination "download\<文件夹名>\"
```

### Step 8: 生成 AI 内容摘要

**当 `summary` 不为 `false` 时执行此步骤**

#### Step 8A: 尝试通过 Content Summarizer 获取转录和摘要

调用 Content Summarizer 生成 AI 摘要：

```powershell
# 进入 content-summarizer 目录并调用 URL 模式
cd content-summarizer
python -m src.main url "<URL>"
```

**后台执行**：
- 设置 `WaitMsBeforeAsync=500`，命令在后台运行
- 使用 `command_status` 每 30 秒检查进度
- 等待 Exit code: 0 表示完成

**Content Summarizer 内部流程**：
1. 自动检测 URL 类型（YouTube / Bilibili / 小宇宙）
2. 通过 yt-dlp 获取视频信息（标题、作者、发布时间）
3. 通过 yt-dlp 获取字幕/转录文本
4. 调用 AI（MiniMax API）生成结构化摘要
5. 输出到 `content-summarizer/output/<标题>_<ID>/` 目录

#### Step 8B: 本地语音转录回退（视频无字幕时）

> **关键流程**：当 Content Summarizer 无法获取字幕/转录文本（`transcript.md` 中显示"无转录"或摘要内容为错误提示）时，执行本地语音转录。

**判断条件**：检查生成的 `transcript.md`，如果内容包含 `（无转录）` 或 `summary.md` 中摘要正文为错误提示，则需要本地转录。

**Step 8B-1: 提取音频**

```powershell
# 使用 FFmpeg 从视频提取音频（16kHz 单声道 WAV，whisper 所需格式）
ffmpeg -i "<视频文件路径>" -vn -acodec pcm_s16le -ar 16000 -ac 1 "<输出目录>/audio_temp.wav" -y
```

**Step 8B-2: 语音转录**

```python
# 使用 faster-whisper 进行语音识别
from faster_whisper import WhisperModel

# 模型选择（按效果从高到低）：
# - large-v3: 最佳效果，需要大量内存和时间
# - medium: 良好效果，推荐有GPU时使用
# - small: 尚可效果，CPU友好，推荐默认选择
# - base: 基础效果，最快速度
model = WhisperModel("small", device="cpu", compute_type="int8")

segments, info = model.transcribe(
    "audio_temp.wav",
    language="zh",       # 指定语言可提高识别准确度
    beam_size=5,
    vad_filter=True,     # 启用 VAD 过滤静音段
    vad_parameters=dict(min_silence_duration_ms=500)
)

# 收集转录文本
transcript_lines = []
for segment in segments:
    transcript_lines.append(segment.text.strip())

full_transcript = "\n".join(transcript_lines)
```

**转录时间参考**（CPU, small 模型）：

| 视频时长 | 预计转录时间 |
|---------|------------|
| 10 分钟 | ~5 分钟 |
| 30 分钟 | ~15 分钟 |
| 1 小时 | ~30 分钟 |
| 3 小时 | ~2-3 小时 |

> **注意**：使用 GPU (CUDA) 可大幅加速，通常快 5-10 倍。

**Step 8B-3: 更新转录文件**

```python
# 更新 transcript.md
with open("transcript.md", "w", encoding="utf-8") as f:
    f.write(f"# {title}\n\n")
    f.write(f"**原始标题**: {title}\n")
    f.write(f"**来源**: {author}\n")
    f.write(f"**发布时间**: {published_at}\n")
    f.write(f"**链接**: {source_url}\n\n")
    f.write("---\n\n## 转录内容\n\n")
    f.write(full_transcript)
```

**Step 8B-4: 调用 AI 生成摘要**

```python
from openai import OpenAI

client = OpenAI(
    api_key="<API_KEY>",        # 从 sources.yaml 读取
    base_url="<BASE_URL>"       # 从 sources.yaml 读取
)

# 构建提示词（使用 rewrite-prompt.md 模板）
response = client.chat.completions.create(
    model="<MODEL>",            # 从 sources.yaml 读取
    messages=[
        {"role": "system", "content": "你是一个专业的内容分析师，擅长将长篇内容改写成结构化的中文摘要。"},
        {"role": "user", "content": prompt}  # 包含转录文本的完整提示词
    ],
    temperature=0.7,
    max_tokens=4000
)
```

**Step 8B-5: 人工校正（可选但推荐）**

> whisper 语音识别可能存在人名、专有名词识别错误。
> 建议完成后检查 `summary.md` 中的关键信息（尤其是人名、地名）。
> 
> 常见误识别示例：
> - 人名"许知远" → 可能被识别为"许志愿"
> - 专业术语可能被识别为同音词

**Step 8B-6: 清理临时文件**

```powershell
# 删除临时音频文件
Remove-Item "<输出目录>/audio_temp.wav" -ErrorAction SilentlyContinue
```

### Step 9: 复制摘要文件到下载目录

摘要生成完成后，将摘要文件复制到视频下载目录，实现统一归档：

```powershell
# 查找 content-summarizer 最新的输出目录
$summaryDir = Get-ChildItem -Path "content-summarizer\output" -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# 复制摘要文件到下载目录
Copy-Item -Path "$($summaryDir.FullName)\summary.md" -Destination "download\<文件夹名>\" -ErrorAction SilentlyContinue
Copy-Item -Path "$($summaryDir.FullName)\transcript.md" -Destination "download\<文件夹名>\" -ErrorAction SilentlyContinue
Copy-Item -Path "$($summaryDir.FullName)\metadata.json" -Destination "download\<文件夹名>\" -ErrorAction SilentlyContinue
Copy-Item -Path "$($summaryDir.FullName)\cover.jpg" -Destination "download\<文件夹名>\" -ErrorAction SilentlyContinue
```

> **注意**：如果是通过 Step 8B 本地转录生成的摘要，文件已经在正确的目录中，无需复制。

### Step 10: 返回结果

向用户报告完成情况：

**完整模式（下载 + 字幕 + 摘要）**：
```
✅ 视频下载、字幕翻译与内容摘要全部完成

📊 任务详情
| 项目 | 内容 |
|------|------|
| 视频标题 | <标题> |
| 源语言 | 英语 (en) |
| 目标语言 | 简体中文 (zh-cn) |
| AI 摘要 | ✅ 已生成 |
| 转录方式 | 在线字幕 / 本地语音识别 |

📁 输出文件
download/<文件夹名>/
├── <视频名>.mp4 (原始视频)
├── <视频名> [中文字幕].mp4 (带字幕)
├── zh-cn.srt (中文字幕)
├── en.srt (英文字幕)
├── summary.md (AI 摘要)
├── transcript.md (原始转录)
└── metadata.json (元数据)
```

**简化模式（下载 + 摘要，无字幕翻译）**：
```
✅ 视频下载与内容摘要完成

📊 任务详情
| 项目 | 内容 |
|------|------|
| 视频标题 | <标题> |
| 视频语言 | 中文 |
| AI 摘要 | ✅ 已生成 |
| 转录方式 | 在线字幕 / 本地语音识别 |

📁 输出文件
download/<文件夹名>/
├── <视频名>.mp4 (原始视频)
├── summary.md (AI 摘要)
├── transcript.md (原始转录)
└── metadata.json (元数据)
```

---

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------| 
| URL 无效 | 提示用户检查链接格式 |
| 视频不可用 | 提示视频可能已被删除或地区限制 |
| 网络超时 | 建议用户稍后重试 |
| 需要登录 | 提示该视频需要账号登录 |
| pyVideoTrans 失败 | 检查路径和 API 配置，提供手动烧录备选方案 |
| Content Summarizer 失败 | 检查 AI API 配置，视频下载不受影响 |
| 转录文本为空 | **自动回退到 faster-whisper 本地语音识别**（见 Step 8B） |
| whisper 模型下载慢 | 可切换到更小模型（small/base），或配置 HF_TOKEN 提速 |
| whisper 人名识别错误 | 提示用户校正关键人名、专有名词 |

> **重要**：摘要生成失败**不影响**视频下载结果。即使摘要失败，视频仍然保留。

## 备选方案：FFmpeg 直接烧录字幕

如果 pyVideoTrans 不可用或已有 `.srt` 文件：

```powershell
# 烧录中文字幕到视频
ffmpeg -i "<视频.mp4>" -vf "subtitles='<字幕路径.srt>':force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'" -c:a copy "<输出.mp4>"
```

> **注意**：路径中的 `\` 需改为 `/`

---

## 常用命令参考

```powershell
# 查看可用格式
yt-dlp -F "<URL>"

# 下载指定格式
yt-dlp -f <format_id> "<URL>"

# 下载播放列表
yt-dlp --yes-playlist "<PLAYLIST_URL>"

# 限速下载
yt-dlp --limit-rate 5M "<URL>"

# 使用代理
yt-dlp --proxy "http://127.0.0.1:7890" "<URL>"

# 运行 Content Summarizer（单独使用）
cd content-summarizer
python -m src.main url "<URL>"
python -m src.main batch

# 本地语音转录（独立使用 faster-whisper）
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('small', device='cpu', compute_type='int8')
segments, info = model.transcribe('audio.wav', language='zh', vad_filter=True)
for seg in segments:
    print(seg.text)
"
```

## 支持的平台

yt-dlp 支持 1000+ 网站，常用的包括：
- YouTube、Bilibili、Twitter/X、TikTok、Vimeo、抖音、西瓜视频等

完整列表：https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

---

## pyVideoTrans 环境配置

### 前置条件
- Python 3.10 - 3.12
- FFmpeg（已配置到 PATH）

### 安装路径
- 安装位置：`D:\pyVideoTrans`
- Python 环境：`D:\pyVideoTrans\.venv\Scripts\python.exe`
- CLI 入口：`D:\pyVideoTrans\cli.py`

### 翻译服务配置
- **翻译渠道**：DeepSeek
- **API URL**：`https://api.deepseek.com`
- **配置方式**：首次运行 GUI (`uv run sp.py`) 进行配置

### 验证安装

```powershell
D:\pyVideoTrans\.venv\Scripts\python.exe D:\pyVideoTrans\cli.py --help
```

---

## Content Summarizer 环境配置

### 安装路径
- 位置：项目根目录下 `content-summarizer/`
- Python 入口：`python -m src.main`

### AI 服务配置
- **配置文件**：`content-summarizer/config/sources.yaml`
- **当前 AI 提供商**：MiniMax (`abab6.5s-chat`)
- **API 地址**：`https://api.minimax.chat/v1`
- **提示词模板**：`content-summarizer/config/rewrite-prompt.md`

### Cookies 配置
- YouTube：`content-summarizer/cookies.txt`
- Bilibili：`content-summarizer/cookies.bilibili.txt`

### 摘要输出
- **输出格式**：Markdown
- **摘要长度**：medium（~1500字）
- **输出结构**：
  ```
  content-summarizer/output/<标题>_<ID>/
  ├── metadata.json    # 元数据
  ├── transcript.md    # 原始转录
  ├── summary.md       # AI 摘要
  └── cover.jpg        # 封面图
  ```

### 验证安装

```powershell
cd content-summarizer
python -m src.main --help
```

---

## faster-whisper 环境配置（本地语音转录）

### 前置条件
- Python 3.10+
- FFmpeg（已配置到 PATH）
- `pip install faster-whisper`

### 模型说明

| 模型 | 大小 | 中文效果 | GPU 内存 | 推荐场景 |
|------|------|---------|---------|---------|
| `large-v3` | ~3GB | ⭐⭐⭐⭐⭐ | ~10GB | 有高端 GPU 时 |
| `medium` | ~1.5GB | ⭐⭐⭐⭐ | ~5GB | 有中端 GPU 时 |
| `small` | ~500MB | ⭐⭐⭐ | ~2GB | **默认推荐（CPU 友好）** |
| `base` | ~150MB | ⭐⭐ | ~1GB | 快速预览 |

### 加速建议
- **GPU 加速**：安装 CUDA 工具包后，将 `device="cpu"` 改为 `device="cuda"`
- **模型缓存**：模型首次下载后会缓存到 `~/.cache/huggingface/`
- **HF_TOKEN**：设置 `HF_TOKEN` 环境变量可解除 HuggingFace 下载限速

### 验证安装

```python
python -c "from faster_whisper import WhisperModel; print('faster-whisper OK')"
```

---

## 自动清理临时文件

### 功能说明

项目配置了自动清理机制，当 `tmpclaude-*` 临时文件超过 3 个时自动清理，保持工作目录整洁。

### 实现方式

**1. 清理脚本**：`.claude/hooks/cleanup-temp-files.sh`

```bash
#!/bin/bash
# 自动清理临时文件的脚本
# 当 tmpclaude-* 文件超过 3 个时自动清理

WORK_DIR="$(pwd)"
TEMP_FILE_COUNT=$(find "$WORK_DIR" -maxdepth 1 -name "tmpclaude-*" -type f 2>/dev/null | wc -l)

echo "检测到 $TEMP_FILE_COUNT 个临时文件"

if [ "$TEMP_FILE_COUNT" -gt 3 ]; then
    echo "临时文件数量超过 3 个，开始清理..."
    find "$WORK_DIR" -maxdepth 1 -name "tmpclaude-*" -type f -delete
    REMAINING_COUNT=$(find "$WORK_DIR" -maxdepth 1 -name "tmpclaude-*" -type f 2>/dev/null | wc -l)
    echo "✅ 清理完成！删除了 $((TEMP_FILE_COUNT - REMAINING_COUNT)) 个临时文件"
else
    echo "临时文件数量未超过阈值，无需清理"
fi
```

**2. Hook 配置**：`.claude/config.json`

```json
{
  "hooks": {
    "postToolUse": {
      "enabled": true,
      "command": "bash .claude/hooks/cleanup-temp-files.sh"
    }
  }
}
```

### 工作流程

1. 每次 Claude Code 执行完工具操作后，自动触发 `postToolUse` hook
2. 运行清理脚本，检测临时文件数量
3. 如果超过 3 个，自动删除所有 `tmpclaude-*` 文件
4. 显示清理结果

### 手动清理

如需手动清理，可以运行：

```bash
bash .claude/hooks/cleanup-temp-files.sh
```

---

**参考链接**：
- pyVideoTrans 官网：https://pyvideotrans.com
- GitHub 仓库：https://github.com/jianchang512/pyvideotrans
- yt-dlp 文档：https://github.com/yt-dlp/yt-dlp
- faster-whisper：https://github.com/SYSTRAN/faster-whisper
