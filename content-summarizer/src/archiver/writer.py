"""归档模块"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import asdict

from ..fetcher.base import MediaItem
from ..summarizer.openai_client import SummaryResult


class Archiver:
    """内容归档器"""

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            from ..config import get_output_dir
            output_dir = get_output_dir()

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """清理文件名中的非法字符"""
        import re
        # 替换非法字符为下划线
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # 限制长度
        if len(name) > 100:
            name = name[:100]
        return name

    def _create_folder_name(self, media: MediaItem) -> str:
        """创建文件夹名称"""
        title = self._sanitize_filename(media.title)
        return f"{title}_{media.id}"

    def archive(
        self,
        media: MediaItem,
        transcript: str,
        summary: SummaryResult,
        cover_path: Optional[Path] = None
    ) -> Path:
        """
        归档内容
        返回归档目录路径
        """
        # 创建内容目录
        folder_name = self._create_folder_name(media)
        content_dir = self.output_dir / folder_name
        content_dir.mkdir(parents=True, exist_ok=True)

        # 1. 写入 metadata.json
        self._write_metadata(content_dir, media, summary)

        # 2. 写入 transcript.md
        self._write_transcript(content_dir, media, transcript)

        # 3. 写入 summary.md
        self._write_summary(content_dir, media, summary)

        # 4. 复制封面图
        if cover_path and cover_path.exists():
            dest_cover = content_dir / 'cover.jpg'
            shutil.copy2(cover_path, dest_cover)
            # 清理临时封面目录
            try:
                cover_path.parent.rmdir()
            except:
                pass

        return content_dir

    def _write_metadata(self, content_dir: Path, media: MediaItem, summary: SummaryResult) -> None:
        """写入元数据文件"""
        metadata = {
            'title': media.title,
            'title_zh': summary.title,
            'source': 'youtube',  # TODO: 根据实际来源设置
            'source_url': media.url,
            'video_id': media.id,
            'published_at': media.published_at,
            'author': media.author,
            'duration': media.duration,
            'thumbnail': media.thumbnail,
            'core_points': summary.core_points,
            'insights': summary.insights,
            'quotes': summary.quotes,
            'guests': summary.guests,
            'created_at': datetime.now().isoformat()
        }

        metadata_path = content_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _write_transcript(self, content_dir: Path, media: MediaItem, transcript: str) -> None:
        """写入转录文件"""
        content = f"""# {media.title}

**原始标题**: {media.title}
**来源**: {media.author}
**发布时间**: {media.published_at}
**链接**: {media.url}

---

## 转录内容

{transcript}
"""

        transcript_path = content_dir / 'transcript.md'
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _write_summary(self, content_dir: Path, media: MediaItem, summary: SummaryResult) -> None:
        """写入摘要文件"""
        # 构建嘉宾部分
        guests_section = ""
        if summary.guests:
            guests_section = "\n## 嘉宾\n"
            for guest in summary.guests:
                if isinstance(guest, dict):
                    guests_section += f"- {guest.get('name', '')} | {guest.get('role', '')}\n"
                    guests_section += f"  - {guest.get('views', '')}\n"
                else:
                    guests_section += f"- {guest}\n"

        # 构建金句部分
        quotes_section = ""
        if summary.quotes:
            quotes_section = "\n## 金句\n"
            for quote in summary.quotes:
                quotes_section += f"- **{quote}**\n"

        # 构建核心观点部分
        core_points_section = ""
        if summary.core_points:
            core_points_section = "\n## 核心观点\n"
            for i, point in enumerate(summary.core_points, 1):
                core_points_section += f"{i}. {point}\n"

        # 构建关键洞察部分
        insights_section = ""
        if summary.insights:
            insights_section = "\n## 关键洞察\n"
            for i, insight in enumerate(summary.insights, 1):
                insights_section += f"{i}. {insight}\n"

        content = f"""# {summary.title}

**原文标题**: {media.title}
**来源**: {media.author}
**发布时间**: {media.published_at}

---

{core_points_section}
{insights_section}
{quotes_section}
{guests_section}
---

## 摘要正文

{summary.summary}

---

*本文由 Content Summarizer 自动生成*
*处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        summary_path = content_dir / 'summary.md'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(content)


# 单例实例
_archiver = None


def get_archiver(output_dir: Optional[Path] = None) -> Archiver:
    """获取归档器实例"""
    global _archiver
    if _archiver is None:
        _archiver = Archiver(output_dir)
    return _archiver
