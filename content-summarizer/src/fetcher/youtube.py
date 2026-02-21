"""YouTube抓取器"""
import re
import json
from typing import List
from .base import BaseFetcher, MediaItem


class YouTubeFetcher(BaseFetcher):
    """YouTube内容抓取器"""

    def get_source_name(self) -> str:
        return "youtube"

    def extract_id_from_url(self, url: str) -> str:
        """从YouTube URL提取视频ID"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        raise ValueError(f"无法从URL中提取YouTube视频ID: {url}")

    async def fetch_source_list(self, source_url: str) -> List[MediaItem]:
        """
        从YouTube频道获取视频列表
        source_url: 频道URL，如 https://www.youtube.com/@channel_name
        """
        # 获取频道的所有视频
        cmd = [
            '--dump-json',
            '--flat-playlist',
            source_url
        ]

        result = self._run_yt_dlp(cmd)
        items = []

        for line in result['output'].strip().split('\n'):
            if not line.strip():
                continue
            try:
                info = json.loads(line)
                items.append(MediaItem(
                    id=info.get('id', ''),
                    title=info.get('title', ''),
                    url=f"https://www.youtube.com/watch?v={info.get('id', '')}",
                    published_at=info.get('upload_date', ''),
                    author=info.get('channel', ''),
                    duration=info.get('duration'),
                    thumbnail=info.get('thumbnail')
                ))
            except json.JSONDecodeError:
                continue

        return items


# 单例实例
_fetcher = None


def get_youtube_fetcher() -> YouTubeFetcher:
    """获取YouTube抓取器实例"""
    global _fetcher
    if _fetcher is None:
        _fetcher = YouTubeFetcher()
    return _fetcher
