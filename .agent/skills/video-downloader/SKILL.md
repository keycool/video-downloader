---
name: video-downloader
description: 使用 yt-dlp 下载视频，支持画质选择、字幕下载、仅音频模式，以及中文字幕翻译
---

# 视频下载器 (Video Downloader)

使用 yt-dlp 工具下载网络视频，支持 YouTube、Bilibili、Twitter 等主流平台。

## 触发方式

当用户请求下载视频时触发，识别以下关键词：
- "下载视频"、"下载这个视频"
- "download video"
- 直接粘贴视频链接

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | ✅ | - | 视频链接 |
| `quality` | ❌ | `best` | 画质选项：`best`(最佳)、`1080`、`720`、`480` |
| `subtitle` | ❌ | `false` | 是否下载字幕：`true` / `false` |
| `audio_only` | ❌ | `false` | 仅下载音频：`true` / `false` |
| `output_dir` | ❌ | `download/` | 输出目录路径（自动创建子文件夹） |
| `translate` | ❌ | `false` | 下载后翻译中文字幕 |
| `subtitle_type` | ❌ | `3` | 字幕类型：0=不嵌入，1=硬字幕，3=硬双语字幕 |
| `source_lang` | ❌ | `en` | 源语言：`en`(英语)、`ja`(日语)、`ko`(韩语) |
| `pyvideotrans_path` | ❌ | - | pyVideoTrans 安装路径 |

## 文件夹命名规则

下载的文件会自动整理到结构化的文件夹中：

```
download/
└── {名称缩写}-{下载日期}/
    └── 视频文件.mp4
```

**命名规则**：
- **名称缩写**：从视频标题提取关键词，驼峰命名，如 `DopamineDetox`
- **下载日期**：格式为 `YYYYMMDD`，如 `20260127`
- **示例**：`download/DopamineDetox-20260127/`

## 使用示例

### 1. 基础下载（默认最佳画质）
```
下载这个视频：https://www.youtube.com/watch?v=xxxxx
```

### 2. 指定画质
```
下载这个视频，720p：https://www.youtube.com/watch?v=xxxxx
```

### 3. 下载带字幕
```
下载视频和字幕：https://www.youtube.com/watch?v=xxxxx
```

### 4. 仅下载音频
```
只下载音频：https://www.youtube.com/watch?v=xxxxx
```

### 5. 下载并翻译中文字幕
```
下载视频并翻译中文字幕：https://www.youtube.com/watch?v=xxxxx
```

### 6. 下载并生成双语字幕（推荐学习）
```
下载视频，生成中英双语字幕：https://www.youtube.com/watch?v=xxxxx
```

## 执行步骤

### Step 1: 解析用户请求

从用户输入中提取以下信息：
- **视频链接**：识别 URL 模式
- **画质要求**：识别 "1080p"、"720p"、"最高画质" 等关键词
- **字幕需求**：识别 "字幕"、"subtitle" 等关键词
- **音频模式**：识别 "音频"、"mp3"、"audio" 等关键词

### Step 2: 构建 yt-dlp 命令

根据解析结果构建命令：

```powershell
# 基础命令模板
yt-dlp [OPTIONS] <URL>
```

**命令选项对照表**：

| 用户需求 | yt-dlp 参数 |
|---------|-------------|
| 最佳画质 | `-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"` |
| 1080p | `-f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"` |
| 720p | `-f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"` |
| 480p | `-f "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]"` |
| 下载字幕 | `--write-subs --sub-langs all` |
| 仅音频 | `-x --audio-format mp3 --audio-quality 0` |
| 输出目录 | `-o "<目录>/%(title)s.%(ext)s"` |

### Step 3: 创建输出文件夹

下载前先创建结构化的输出文件夹：

1. **获取视频标题**：使用 `yt-dlp --get-title "<URL>"` 获取标题
2. **生成文件夹名称**：从标题提取关键词，格式为 `{名称缩写}-{YYYYMMDD}`
3. **创建文件夹**：

```powershell
# 创建下载目录（如 download/DopamineDetox-20260127）
$folderName = "<名称缩写>-$(Get-Date -Format 'yyyyMMdd')"
New-Item -Path "download\$folderName" -ItemType Directory -Force
```

### Step 4: 执行下载

使用 `run_command` 工具执行构建好的命令，输出到创建的文件夹：

```powershell
# 示例：下载最佳画质视频到指定文件夹
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "download/<文件夹名>/%(title)s.%(ext)s" "<URL>"

# 示例：下载 720p 带字幕
yt-dlp -f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]" --write-subs --sub-langs all -o "download/<文件夹名>/%(title)s.%(ext)s" "<URL>"

# 示例：仅下载音频
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "download/<文件夹名>/%(title)s.%(ext)s" "<URL>"
```

**重要**：
- 设置 `WaitMsBeforeAsync` 为 `500`，让命令在后台运行
- 使用 `command_status` 定期检查下载进度
- 下载完成后通知用户

### Step 5: 监控下载进度

由于视频下载可能耗时较长，需要：

1. 将命令发送到后台执行
2. 每隔 10-30 秒检查一次状态
3. 下载完成后，列出下载的文件并通知用户

```powershell
# 检查下载目录中的新文件
Get-ChildItem -Path "<output_dir>" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

### Step 6: 返回结果

下载完成后，向用户报告：
- ✅ 下载成功/失败状态
- 📁 文件保存位置
- 📊 文件大小
- ⏱️ 下载耗时（如有）

### Step 6.5: 合并视频与音频（如需要）

如果下载的视频文件只包含视频流（无音频），需要先用 FFmpeg 合并：

**检测方法**：
- 文件名包含 `.f399`、`.f137` 等格式 ID 通常表示仅视频流
- 使用 `ffprobe -v quiet -show_streams <视频文件>` 检查是否有 audio 类型的 stream

**合并命令**：

```powershell
ffmpeg -i "<仅视频文件.mp4>" -i "<音频文件.m4a>" -c:v copy -c:a aac -strict experimental "<输出文件.mp4>"
```

**示例**：
```powershell
ffmpeg -i "video.f399.mp4" -i "audio.f140.m4a" -c:v copy -c:a aac -strict experimental "merged_video.mp4"
```

### Step 7: 字幕翻译（可选）

如果用户请求翻译中文字幕，使用 pyVideoTrans 进行处理：

**前置条件**：
- 需要已安装 pyVideoTrans（源码部署方式）
- 需要配置 DeepSeek API Key（在 pyVideoTrans GUI 中设置一次即可）

**执行命令**：

```powershell
# 切换到 pyVideoTrans 目录
cd <pyvideotrans_path>

# 英译中，硬双语字幕（推荐学习）
uv run cli.py --task vtv --name "<视频完整路径>" --source_language_code en --target_language_code zh-cn --subtitle_type 3

# 英译中，仅中文硬字幕
uv run cli.py --task vtv --name "<视频完整路径>" --source_language_code en --target_language_code zh-cn --subtitle_type 1

# 使用 GPU 加速（如有 NVIDIA 显卡）
uv run cli.py --task vtv --name "<视频完整路径>" --source_language_code en --target_language_code zh-cn --subtitle_type 3 --cuda
```

**参数说明**：

| 参数 | 说明 |
|------|------|
| `--task vtv` | 视频翻译（识别→翻译→合成） |
| `--source_language_code` | 源语言代码 |
| `--target_language_code` | 目标语言：`zh-cn`(简体中文) |
| `--subtitle_type` | 0=不嵌入, 1=硬字幕, 2=软字幕, 3=硬双语, 4=软双语 |
| `--model_name` | Whisper 模型：`large-v3`(推荐)、`medium`、`small` |
| `--cuda` | 启用 GPU 加速 |

**输出文件**：
- 翻译后的视频会保存在原视频同目录下
- 同时生成 `.srt` 字幕文件

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| URL 无效 | 提示用户检查链接格式 |
| 视频不可用 | 提示视频可能已被删除或地区限制 |
| 网络超时 | 建议用户稍后重试 |
| 需要登录 | 提示该视频需要账号登录 |
| 格式不支持 | 降级到可用的最佳格式 |

## 常用命令参考

```powershell
# 查看可用格式
yt-dlp -F "<URL>"

# 下载指定格式
yt-dlp -f <format_id> "<URL>"

# 下载播放列表
yt-dlp --yes-playlist "<PLAYLIST_URL>"

# 限速下载（避免被封）
yt-dlp --limit-rate 5M "<URL>"

# 使用代理
yt-dlp --proxy "http://127.0.0.1:7890" "<URL>"
```

## 支持的平台

yt-dlp 支持 1000+ 网站，常用的包括：
- YouTube
- Bilibili
- Twitter/X
- TikTok
- Vimeo
- 抖音
- 西瓜视频
- 等等...

完整列表：https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## pyVideoTrans 安装配置（字幕翻译功能）

字幕翻译功能需要 pyVideoTrans 工具，安装步骤如下：

### 1. 前置条件

- Python 3.10 - 3.12
- FFmpeg（已配置到 PATH）
- Git

### 2. 安装 uv 包管理器

```powershell
# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. 克隆并安装 pyVideoTrans

```powershell
# 克隆仓库（路径不要有空格和中文）
git clone https://github.com/jianchang512/pyvideotrans.git D:\pyVideoTrans
cd D:\pyVideoTrans

# 安装依赖
uv sync
```

### 4. 配置 DeepSeek API

首次使用需要在 GUI 中配置翻译服务：

```powershell
# 启动 GUI
cd D:\pyVideoTrans
uv run sp.py
```

在设置中配置：
- **翻译渠道**：选择 DeepSeek
- **API Key**：填入你的 DeepSeek API Key
- **API URL**：`https://api.deepseek.com`

### 5. 验证安装

```powershell
cd D:\pyVideoTrans
uv run cli.py --help
```

如看到帮助信息，说明安装成功。

---

**参考链接**：
- pyVideoTrans 官网：https://pyvideotrans.com
- GitHub 仓库：https://github.com/jianchang512/pyvideotrans
- CLI 文档：https://pyvideotrans.com/cli
