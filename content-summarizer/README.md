# Content Summarizer

自动抓取 YouTube、小宇宙、Bilibili 的内容，获取转录并生成 AI 中文深度摘要。

## 功能特性

- 支持多平台：YouTube、小宇宙播客、Bilibili
- 自动获取视频转录
- AI 改写生成结构化中文摘要
- 状态管理，避免重复处理
- 本地归档

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

复制配置文件并编辑：

```bash
cp config/sources.yaml config/sources.yaml.bak
# 编辑 config/sources.yaml，填入你的配置
```

配置示例：

```yaml
sources:
  - name: "我的YouTube频道"
    type: youtube
    url: "https://www.youtube.com/@channel_name"
    enabled: true

ai:
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key: "${OPENAI_API_KEY}"  # 或直接填入 API Key

summary:
  length: "medium"  # short | medium | long | custom

output:
  root: "./output"
```

### 3. 设置 API Key

```bash
# Windows
set OPENAI_API_KEY=your_api_key

# Linux/Mac
export OPENAI_API_KEY=your_api_key
```

### 4. 运行

```bash
# 批量模式：扫描订阅源，选择处理
python -m src.main batch

# URL模式：直接处理指定URL
python -m src.main url "https://youtube.com/watch?v=xxx"
python -m src.main url "url1" "url2" "url3"
```

## 输出结构

每个内容会生成独立文件夹：

```
output/
└── 视频标题_xxxxx/
    ├── metadata.json    # 元数据
    ├── transcript.md    # 原始转录
    ├── summary.md        # AI摘要
    └── cover.jpg         # 封面图
```

## 项目结构

```
content-summarizer/
├── config/
│   ├── sources.yaml       # 订阅源配置
│   ├── state.yaml         # 处理状态
│   └── rewrite-prompt.md  # AI提示词
├── src/
│   ├── main.py            # CLI入口
│   ├── config.py          # 配置加载
│   ├── fetcher/           # 内容抓取
│   │   ├── base.py
│   │   ├── youtube.py
│   │   ├── bilibili.py
│   │   └── xiaoyuzhou.py
│   ├── summarizer/        # AI改写
│   │   └── openai_client.py
│   └── archiver/          # 归档
│       └── writer.py
├── output/                 # 输出目录
├── requirements.txt
└── README.md
```

## 飞书集成

飞书多维表格同步功能开发中...
