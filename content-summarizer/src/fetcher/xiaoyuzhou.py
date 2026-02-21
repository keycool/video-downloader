"""小宇宙抓取器"""
import re
import json
import urllib.request
import xml.etree.ElementTree as ET
from typing import List
from .base import BaseFetcher, MediaItem


class XiaoyuzhouFetcher(BaseFetcher):
    """小宇宙播客抓取器"""

    def get_source_name(self) -> str:
        return "xiaoyuzhou"

    def extract_id_from_url(self, url: str) -> str:
        """从小宇宙URL提取播客/单集ID"""
        # 小宇宙URL格式:
        # 播客主页: https://www.xiaoyuzhoufm.com/podcast/xxx
        # 单集: https://www.xiaoyuzhoufm.com/episode/xxx

        # 提取单集ID
        match = re.search(r'xiaoyuzhoufm\.com/episode/([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)

        # 提取播客ID
        match = re.search(r'xiaoyuzhoufm\.com/podcast/([a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)

        raise ValueError(f"无法从小宇宙URL中提取ID: {url}")

    async def fetch_source_list(self, source_url: str) -> List[MediaItem]:
        """
        从小宇宙播客获取单集列表
        source_url: 播客RSS链接
        """
        items = []

        # 小宇宙使用RSS订阅，可以直接获取
        # 但yt-dlp可能不支持，需要尝试
        try:
            cmd = [
                '--dump-json',
                '--flat-playlist',
                source_url
            ]
            result = self._run_yt_dlp(cmd)

            for line in result['output'].strip().split('\n'):
                if not line.strip():
                    continue
                try:
                    info = json.loads(line)
                    # 提取单集ID
                    url = info.get('url', '')
                    ep_match = re.search(r'episode/([a-zA-Z0-9]+)', url)
                    ep_id = ep_match.group(1) if ep_match else ''

                    if ep_id:
                        items.append(MediaItem(
                            id=ep_id,
                            title=info.get('title', ''),
                            url=url,
                            published_at=info.get('upload_date', ''),
                            author=info.get('channel', ''),
                            duration=info.get('duration'),
                            thumbnail=info.get('thumbnail')
                        ))
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"使用yt-dlp获取失败，尝试RSS解析: {e}")
            # 备选：直接解析RSS
            try:
                items = self._fetch_from_rss(source_url)
            except Exception as e2:
                print(f"RSS解析也失败: {e2}")

        return items

    def _fetch_from_rss(self, rss_url: str) -> List[MediaItem]:
        """从RSS获取播客单集"""
        items = []

        try:
            with urllib.request.urlopen(rss_url, timeout=30) as response:
                content = response.read().decode('utf-8')

            root = ET.fromstring(content)
            channel = root.find('channel')

            if channel is not None:
                for item in channel.findall('item'):
                    title = item.findtext('title', '')
                    link = item.findtext('link', '')
                    pub_date = item.findtext('pubDate', '')

                    # 提取单集ID
                    ep_match = re.search(r'episode/([a-zA-Z0-9]+)', link)
                    ep_id = ep_match.group(1) if ep_match else ''

                    if ep_id:
                        # 尝试获取更多元数据
                        enclosure = item.find('enclosure')
                        duration = None
                        if enclosure is not None:
                            duration_str = enclosure.get('length', '')
                            # length可能是文件大小，不是时长

                        items.append(MediaItem(
                            id=ep_id,
                            title=title,
                            url=link,
                            published_at=pub_date,
                            author=channel.findtext('title', ''),
                            duration=duration,
                            thumbnail=None
                        ))

        except Exception as e:
            print(f"RSS解析错误: {e}")

        return items


# 单例实例
_fetcher = None


def get_xiaoyuzhou_fetcher() -> XiaoyuzhouFetcher:
    """获取小宇宙抓取器实例"""
    global _fetcher
    if _fetcher is None:
        _fetcher = XiaoyuzhouFetcher()
    return _fetcher
