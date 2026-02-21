"""Bilibili抓取器"""
import re
import json
from typing import List
from .base import BaseFetcher, MediaItem


class BilibiliFetcher(BaseFetcher):
    """Bilibili内容抓取器"""

    def get_source_name(self) -> str:
        return "bilibili"

    def extract_id_from_url(self, url: str) -> str:
        """从Bilibili URL提取视频ID"""
        patterns = [
            r'bilibili\.com/video/([Bb][Vv][a-zA-Z0-9]+)',
            r'bilibili\.com/video/([Bb][Vv][a-zA-Z0-9]+)\?',
            r'b23\.tv/([a-zA-Z0-9]+)',  # 短链
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        raise ValueError(f"无法从URL中提取Bilibili视频ID: {url}")

    async def fetch_source_list(self, source_url: str) -> List[MediaItem]:
        """
        从Bilibili UP主获取视频列表
        source_url: UP主主页URL，如 https://space.bilibili.com/123456789
        """
        # 从主页URL提取UID
        uid_match = re.search(r'space\.bilibili\.com/(\d+)', source_url)
        if not uid_match:
            raise ValueError(f"无法从URL中提取Bilibili UID: {source_url}")

        uid = uid_match.group(1)

        # 使用yt-dlp获取UP主所有视频
        cmd = [
            '--dump-json',
            '--flat-playlist',
            f'https://space.bilibili.com/{uid}'
        ]

        result = self._run_yt_dlp(cmd)
        items = []

        for line in result['output'].strip().split('\n'):
            if not line.strip():
                continue
            try:
                info = json.loads(line)
                # Bilibili视频ID是BV开头的
                bvid = info.get('id', '')
                if bvid:
                    items.append(MediaItem(
                        id=bvid,
                        title=info.get('title', ''),
                        url=f"https://www.bilibili.com/video/{bvid}",
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


def get_bilibili_fetcher() -> BilibiliFetcher:
    """获取Bilibili抓取器实例"""
    global _fetcher
    if _fetcher is None:
        _fetcher = BilibiliFetcher()
    return _fetcher
