---
description: 使用 yt-dlp 下载视频，支持画质选择、字幕下载、仅音频模式
---

# 视频下载器 (Video Downloader)

使用 yt-dlp 工具下载网络视频，支持 YouTube、Bilibili、Twitter 等主流平台。

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | ✅ | - | 视频链接 |
| `quality` | ❌ | `best` | 画质选项：`best`、`1080`、`720`、`480` |
| `subtitle` | ❌ | `false` | 是否下载字幕 |
| `audio_only` | ❌ | `false` | 仅下载音频 |

## 执行步骤

### Step 1: 解析用户请求

从用户输入中提取：
- **视频链接**：识别 URL 模式
- **画质要求**：识别 "1080p"、"720p"、"最高画质" 等
- **字幕需求**：识别 "字幕"、"subtitle"
- **音频模式**：识别 "音频"、"mp3"、"audio"

### Step 2: 构建 yt-dlp 命令

| 用户需求 | yt-dlp 参数 |
|---------|-------------|
| 最佳画质 | `-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"` |
| 1080p | `-f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"` |
| 720p | `-f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"` |
| 下载字幕 | `--write-subs --sub-langs all` |
| 仅音频 | `-x --audio-format mp3 --audio-quality 0` |

### Step 3: 执行下载

```powershell
# 示例：下载最佳画质视频
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "%(title)s.%(ext)s" "<URL>"

# 示例：下载 720p 带字幕
yt-dlp -f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]" --write-subs --sub-langs all -o "%(title)s.%(ext)s" "<URL>"

# 示例：仅下载音频
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s" "<URL>"
```

**重要**：设置 `WaitMsBeforeAsync` 为 `500`，使用 `command_status` 监控进度。

### Step 4: 返回结果

下载完成后报告：
- ✅ 下载状态
- 📁 文件位置
- 📊 文件大小

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| URL 无效 | 提示检查链接格式 |
| 视频不可用 | 提示可能已删除或地区限制 |
| 网络超时 | 建议稍后重试 |
| 需要登录 | 提示需要账号登录 |
