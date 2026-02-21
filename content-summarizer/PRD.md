# 内容订阅与AI摘要工具 - PRD开发文档

## 1. 项目概述

**项目名称**: Content Summarizer
**项目类型**: 命令行工具
**核心功能**: 自动抓取YouTube、小宇宙、Bilibili的内容，获取转录并生成AI中文深度摘要
**目标用户**: 需要消费大量视频/音频内容并生成笔记的用户

---

## 2. 功能需求

### 2.1 内容来源管理

| 来源 | 配置方式 | 说明 |
|------|---------|------|
| YouTube | 频道URL | 支持多个频道 |
| 小宇宙 | 播客RSS链接 | 支持多个播客 |
| Bilibili | UP主主页URL | 支持多个UP主 |

### 2.2 配置文件结构

```
project/
├── config/
│   ├── sources.yaml        # 订阅源配置
│   ├── state.yaml          # 处理状态记录
│   └── rewrite-prompt.md   # AI改写提示词
├── output/                  # 输出目录
└── src/
    ├── main.py             # 主入口
    ├── fetcher/            # 内容抓取
    ├── summarizer/         # AI改写
    └── archiver/          # 归档
```

### 2.3 工作流模式

#### 模式1：批量模式 (batch)
```
1. 扫描所有订阅源
2. 对比state.yaml获取新内容
3. 列出新内容供用户选择
4. 用户输入序号确认
5. 逐个处理选中的内容
```

#### 模式2：URL模式 (url)
```
1. 解析用户输入的URL
2. 自动检测URL类型
3. 直接处理，无需确认
```

### 2.4 内容处理流程

```
输入 → 视频URL抓取 → 转录获取 → AI改写 → 归档 → (飞书同步)
```

**Step 1: 视频抓取**
- 使用yt-dlp获取视频信息
- 提取真实发布时间（而非处理时间）
- 下载封面图

**Step 2: 转录获取**
- 使用yt-dlp --write-subs 获取字幕
- 优先使用自动生成的字幕

**Step 3: AI改写**
- 输入：原始转录文本
- 输出：结构化中文摘要
- 可配置摘要长度

**Step 4: 归档**
每个内容生成独立文件夹：
```
output/
└── {title}_{video_id}/
    ├── metadata.json       # 元数据
    ├── transcript.md       # 原始转录
    ├── summary.md          # AI摘要
    └── cover.jpg           # 封面图
```

---

## 3. 配置文件详解

### 3.1 sources.yaml

```yaml
version: "1.0"

# 订阅源列表
sources:
  # YouTube频道
  - name: "核心YouTube频道"
    type: youtube
    url: "https://www.youtube.com/@channel1"
    enabled: true

  # 小宇宙播客
  - name: "科技播客"
    type: xiaoyuzhou
    url: "https://www.xiaoyuzhoufm.com/podcast/xxx"
    enabled: true

  # Bilibili UP主
  - name: "学习UP主"
    type: bilibili
    url: "https://space.bilibili.com/123456"
    enabled: true

# AI配置
ai:
  # 兼容OpenAI/Gemini接口
  provider: "openai"  # openai | gemini
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key: "${OPENAI_API_KEY}"  # 从环境变量读取

# 摘要配置
summary:
  # 摘要长度选项
  length: "medium"  # short | medium | long | custom
  custom_words: 2000  # 自定义字数

# 输出配置
output:
  root: "./output"
  format: "markdown"
```

### 3.2 state.yaml

```yaml
version: "1.0"
last_scan: "2024-01-01T00:00:00Z"

# 已处理内容记录
processed:
  # YouTube
  youtube:
    - video_id: "abc123"
      title: "视频标题"
      processed_at: "2024-01-01T00:00:00Z"

  # 小宇宙
  xiaoyuzhou:
    - episode_id: "xyz789"
      title: "播客标题"
      processed_at: "2024-01-01T00:00:00Z"

  # Bilibili
  bilibili:
    - video_id: "bilibili123"
      title: "视频标题"
      processed_at: "2024-01-01T00:00:00Z"
```

### 3.3 rewrite-prompt.md

```markdown
# AI改写提示词

## 任务
将以下视频/音频转录文本改写成结构化的中文深度摘要。

## 输出格式要求

### 1. 标题
生成一个吸引眼球的中文标题（20字以内）

### 2. 核心观点 (3-5条)
列出内容的主要观点，每条不超过30字

### 3. 关键洞察 (2-4条)
深入分析内容中的洞察和启示

### 4. 金句提取 (3-5条)
提取内容中的经典语句

### 5. 嘉宾信息（如有）
- 姓名：
- 身份：
- 主要观点：

### 6. 摘要正文
{length}字左右的中文深度摘要

---

## 转录内容
{transcript}
```

---

## 4. 技术方案

### 4.1 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 视频抓取 | Python + yt-dlp | 复用现有能力 |
| 内容转录 | yt-dlp --write-subs | 获取字幕文件 |
| AI改写 | Python调用LLM API | 支持OpenAI/Gemini兼容接口 |
| 飞书集成 | Python + 飞书SDK | 后续开发 |

### 4.2 目录结构

```
content-summarizer/
├── config/
│   ├── sources.yaml
│   ├── state.yaml
│   └── rewrite-prompt.md
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI入口
│   ├── config.py            # 配置加载
│   ├── fetcher/
│   │   ├── __init__.py
│   │   ├── base.py          # 基类
│   │   ├── youtube.py
│   │   ├── xiaoyuzhou.py
│   │   └── bilibili.py
│   ├── summarizer/
│   │   ├── __init__.py
│   │   └── openai_client.py # LLM调用
│   └── archiver/
│       ├── __init__.py
│       └── writer.py
├── requirements.txt
└── README.md
```

### 4.3 URL自动检测

```python
def detect_url_type(url: str) -> str:
    """自动检测URL类型"""
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "xiaoyuzhou" in url:
        return "xiaoyuzhou"
    elif "bilibili.com" in url:
        return "bilibili"
    else:
        raise ValueError(f"不支持的URL类型: {url}")
```

### 4.4 状态管理

- 使用state.yaml记录已处理内容
- 处理前检查video_id是否已存在
- 处理完成后更新state.yaml

---

## 5. CLI接口

```bash
# 批量模式：扫描订阅源，选择处理
python -m src.main batch

# URL模式：直接处理指定URL
python -m src.main url "https://youtube.com/watch?v=xxx"

# URL模式：批量URL
python -m src.main url "url1" "url2" "url3"

# 查看帮助
python -m src.main --help
```

---

## 6. 输出示例

### metadata.json
```json
{
  "title": "AI改变了我们的学习方法",
  "title_zh": "AI如何颠覆传统学习",
  "source": "youtube",
  "source_url": "https://youtube.com/watch?v=xxx",
  "video_id": "xxx",
  "published_at": "2024-01-01T00:00:00Z",
  "author": "频道名",
  "guests": [
    {
      "name": "张三",
      "role": "AI研究员",
      "views": "关于AI学习的观点"
    }
  ],
  "quotes": [
    "AI不是替代学习，而是增强学习",
    "Prompt是人与AI沟通的新语言"
  ],
  "created_at": "2024-01-02T00:00:00Z"
}
```

### summary.md
```markdown
# AI如何颠覆传统学习

## 核心观点
1. AI是学习的增强工具而非替代品
2. 提示词工程成为核心技能
3. 人机协作是未来趋势

## 关键洞察
- 学习方式从"记忆知识"转向"调用知识"
- AI降低了学习门槛，但提高了思考深度

## 金句
- "AI不是替代学习，而是增强学习"
- "Prompt是人与AI沟通的新语言"

## 嘉宾
- 张三 | AI研究员

## 摘要正文
（约2000字的中文深度摘要...）
```

---

## 7. 飞书集成（预留）

后续开发内容：
- 飞书多维表格API对接
- 封面图上传到飞书
- 字段映射配置

---

## 8. 验收标准

- [ ] sources.yaml配置正确加载
- [ ] 批量模式能列出新内容供选择
- [ ] URL模式能自动检测URL类型
- [ ] 视频发布时间正确提取
- [ ] 封面图正确下载
- [ ] 转录文本正确获取
- [ ] AI改写输出符合格式要求
- [ ] 归档文件夹结构正确
- [ ] 状态管理避免重复处理
- [ ] 错误处理完善
