"""抓取器基类"""
import re
import subprocess
import json
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MediaItem:
    """媒体内容项"""
    id: str           # 视频/音频ID
    title: str        # 标题
    url: str          # 播放链接
    published_at: str # 发布时间 (ISO格式)
    author: str       # 作者/频道名
    duration: Optional[int] = None  # 时长(秒)
    thumbnail: Optional[str] = None  # 封面图URL


@dataclass
class MediaResult:
    """抓取结果"""
    media: MediaItem
    transcript: str   # 转录文本
    cover_path: Optional[Path] = None  # 封面图本地路径


class BaseFetcher(ABC):
    """抓取器基类"""

    def __init__(self):
        self.temp_dir = None

    @abstractmethod
    def get_source_name(self) -> str:
        """获取来源名称"""
        pass

    @abstractmethod
    async def fetch_source_list(self, source_url: str) -> List[MediaItem]:
        """
        从订阅源获取内容列表
        例如：获取频道的所有视频
        """
        pass

    @abstractmethod
    def extract_id_from_url(self, url: str) -> str:
        """从URL中提取ID"""
        pass

    def _run_yt_dlp(self, args: List[str], timeout: int = 300) -> Dict[str, Any]:
        """运行yt-dlp命令"""
        import os
        # 获取项目根目录的cookie文件
        project_root = Path(__file__).parent.parent.parent

        # 尝试多个cookie文件
        cookie_files = [
            project_root / "cookies.youtube.txt",
            project_root / "cookies.bilibili.txt",
            project_root / "cookies.txt"
        ]

        cookie_arg = []
        for cf in cookie_files:
            if cf.exists():
                cookie_arg = ['--cookies', str(cf)]
                break

        # 尝试多种方式运行yt-dlp
        cmd_options = [
            ['yt-dlp', '--no-download', '--no-playlist'] + cookie_arg + args,
            ['yt-dlp', '--no-download', '--no-playlist', '--extractor-args', 'youtube:player_client=default'] + cookie_arg + args,
            ['yt-dlp', '--no-download', '--no-playlist', '--extractor-args', 'youtube:player_client=android'] + cookie_arg + args,
        ]

        last_error = None
        for cmd in cmd_options:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8'
                )
                if result.returncode == 0:
                    return {'success': True, 'output': result.stdout}
                last_error = result.stderr
            except subprocess.TimeoutExpired:
                last_error = "timeout"
            except FileNotFoundError:
                raise RuntimeError("yt-dlp not found. Please install: pip install yt-dlp")

        raise RuntimeError(f"yt-dlp error: {last_error}")

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """获取视频信息"""
        # 尝试不同方式获取视频信息
        cmd_options = [
            ['--dump-json', '--no-download', '--no-playlist', url],
            ['--print', '%(json)s', '--no-download', '--skip-download', url],
        ]

        for cmd in cmd_options:
            try:
                result = self._run_yt_dlp(cmd)
                output = result['output'].strip()
                if output:
                    return json.loads(output)
            except:
                continue

        raise RuntimeError("无法获取视频信息")

    def download_cover(self, url: str, output_dir: Path) -> Optional[Path]:
        """下载封面图"""
        try:
            # 获取视频信息以获取封面URL
            info = self.get_video_info(url)
            thumbnail = info.get('thumbnail')
            if not thumbnail:
                return None

            # yt-dlp可以下载缩略图
            cmd = [
                '--write-thumbnail',
                '--convert-thumbnails', 'jpg',
                '-o', str(output_dir / 'cover'),
                url
            ]
            self._run_yt_dlp(cmd)

            # 查找下载的封面文件
            for ext in ['jpg', 'jpeg', 'png', 'webp']:
                cover_path = output_dir / f'cover.{ext}'
                if cover_path.exists():
                    # 统一重命名为cover.jpg
                    new_path = output_dir / 'cover.jpg'
                    cover_path.rename(new_path)
                    return new_path

            return None
        except Exception as e:
            print(f"下载封面失败: {e}")
            return None

    def get_transcript(self, url: str) -> str:
        """获取视频转录"""
        self.temp_dir = tempfile.mkdtemp()
        cmd = [
            '--write-subs',
            '--sub-lang', 'zh-CN,en,zh-Hans,zh-Hant',
            '--skip-download',
            '--output', f'{self.temp_dir}/%(title)s',
            url
        ]

        try:
            self._run_yt_dlp(cmd)
            # 查找字幕文件
            temp_path = Path(self.temp_dir)
            for sub_file in temp_path.glob('*.vtt'):
                return self._read_subtitle(sub_file)
            for sub_file in temp_path.glob('*.srt'):
                return self._read_subtitle(sub_file)

            return ""
        except Exception as e:
            print(f"获取转录失败: {e}")
            return ""
        finally:
            # 清理临时目录
            if self.temp_dir and Path(self.temp_dir).exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _read_subtitle(self, sub_path: Path) -> str:
        """读取字幕文件"""
        try:
            with open(sub_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # 移除WebVTT/SSA标记，保留纯文本
            lines = []
            for line in content.split('\n'):
                line = line.strip()
                # 跳过时间轴和空行
                if not line or '-->' in line or line.startswith('WEBVTT'):
                    continue
                # 移除标签如 <c>
                line = re.sub(r'<[^>]+>', '', line)
                if line:
                    lines.append(line)
            return '\n'.join(lines)
        except Exception as e:
            print(f"读取字幕失败: {e}")
            return ""

    async def fetch_media(self, url: str) -> MediaResult:
        """抓取单个媒体内容"""
        # 获取视频信息
        info = self.get_video_info(url)

        # 构建MediaItem
        media = MediaItem(
            id=self.extract_id_from_url(url),
            title=info.get('title', ''),
            url=url,
            published_at=info.get('upload_date', ''),  # 真实发布时间
            author=info.get('channel', info.get('uploader', '')),
            duration=info.get('duration'),
            thumbnail=info.get('thumbnail')
        )

        # 创建临时目录下载封面
        temp_dir = tempfile.mkdtemp()
        cover_path = self.download_cover(url, Path(temp_dir))

        # 获取转录
        transcript = self.get_transcript(url)

        return MediaResult(
            media=media,
            transcript=transcript,
            cover_path=cover_path
        )


def detect_url_type(url: str) -> str:
    """检测URL类型"""
    url_lower = url.lower()
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'xiaoyuzhou' in url_lower:
        return 'xiaoyuzhou'
    elif 'bilibili.com' in url_lower:
        return 'bilibili'
    else:
        raise ValueError(f"不支持的URL类型: {url}")
