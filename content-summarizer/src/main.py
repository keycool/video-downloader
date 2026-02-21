"""Content Summarizer - 主入口"""
import asyncio
import argparse
import sys
import os
from pathlib import Path

# 解决Windows编码问题
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from typing import List, Optional
from datetime import datetime

from .config import load_config, load_state, save_state
from .fetcher.base import detect_url_type, MediaItem
from .fetcher.youtube import get_youtube_fetcher
from .fetcher.bilibili import get_bilibili_fetcher
from .fetcher.xiaoyuzhou import get_xiaoyuzhou_fetcher
from .summarizer.openai_client import get_summarizer
from .archiver.writer import get_archiver


def get_fetcher(source_type: str):
    """根据类型获取对应的抓取器"""
    fetchers = {
        'youtube': get_youtube_fetcher,
        'bilibili': get_bilibili_fetcher,
        'xiaoyuzhou': get_xiaoyuzhou_fetcher,
    }

    fetcher_fn = fetchers.get(source_type)
    if not fetcher_fn:
        raise ValueError(f"不支持的来源类型: {source_type}")

    return fetcher_fn()


async def process_single_url(url: str, config, state: dict) -> bool:
    """处理单个URL"""
    print(f"\n{'='*50}")
    print(f"处理: {url}")
    print('='*50)

    # 检测URL类型
    url_type = detect_url_type(url)
    print(f"来源类型: {url_type}")

    # 获取抓取器
    fetcher = get_fetcher(url_type)

    # 提取视频ID
    video_id = fetcher.extract_id_from_url(url)
    print(f"视频ID: {video_id}")

    # 检查是否已处理
    processed_list = state.get('processed', {}).get(url_type, [])
    if any(item.get('video_id') == video_id or item.get('id') == video_id for item in processed_list):
        print(f"[!] 已跳过: 该内容之前已处理过")
        return False

    # 抓取内容
    print("\n[>] 抓取内容...")
    try:
        result = await fetcher.fetch_media(url)
    except Exception as e:
        print(f"[X] 抓取失败: {e}")
        return False

    media = result.media
    transcript = result.transcript
    cover_path = result.cover_path

    print(f"标题: {media.title}")
    print(f"发布时间: {media.published_at}")
    print(f"作者: {media.author}")

    if not transcript:
        print("[!] 警告: 未获取到转录文本")
        transcript = "（无转录）"

    # AI改写
    print("\n[*] AI改写中...")
    try:
        summarizer = get_summarizer(config)
        summary = await summarizer.summarize(transcript)
        print(f"[OK] 摘要生成完成: {summary.title}")
    except Exception as e:
        print(f"[X] AI改写失败: {e}")
        return False

    # 归档
    print("\n[*] 归档中...")
    try:
        archiver = get_archiver()
        output_path = archiver.archive(media, transcript, summary, cover_path)
        print(f"[OK] 已归档到: {output_path}")
    except Exception as e:
        print(f"[X] 归档失败: {e}")
        return False

    # 更新状态
    state.setdefault('processed', {}).setdefault(url_type, []).append({
        'video_id': video_id,
        'title': media.title,
        'processed_at': datetime.now().isoformat()
    })

    return True


async def batch_mode(config, state: dict):
    """批量模式：扫描订阅源，让用户选择"""
    print("\n[*] 扫描订阅源...")
    print('='*50)

    all_new_items = []
    enabled_sources = [s for s in config.sources if s.enabled]

    for source in enabled_sources:
        print(f"\n[*] 检查: {source.name} ({source.type})")

        try:
            fetcher = get_fetcher(source.type)
            items = await fetcher.fetch_source_list(source.url)

            # 过滤已处理的内容
            processed_list = state.get('processed', {}).get(source.type, [])
            processed_ids = {item.get('video_id', item.get('id', '')) for item in processed_list}

            new_items = [item for item in items if item.id not in processed_ids]

            print(f"   发现 {len(items)} 个内容，其中 {len(new_items)} 个新内容")

            for item in new_items:
                item._source_name = source.name
                item._source_type = source.type
                all_new_items.append(item)

        except Exception as e:
            print(f"   [X] 获取失败: {e}")

    if not all_new_items:
        print("\n[OK] 没有新内容需要处理")
        return

    # 列出新内容供用户选择
    print("\n" + "="*50)
    print("新内容列表:")
    print("="*50)

    for i, item in enumerate(all_new_items, 1):
        print(f"{i}. [{item._source_name}] {item.title}")
        print(f"   发布时间: {item.published_at}")
        print(f"   URL: {item.url}")
        print()

    # 用户选择
    print("-"*50)
    print("请选择要处理的内容（输入序号，用逗号分隔，如: 1,3,5")
    print("输入 'all' 处理所有内容，输入 'q' 退出")
    choice = input("> ").strip()

    if choice.lower() == 'q':
        print("已退出")
        return

    # 解析选择
    if choice.lower() == 'all':
        selected_items = all_new_items
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            selected_items = [all_new_items[i-1] for i in indices if 1 <= i <= len(all_new_items)]
        except (ValueError, IndexError):
            print("无效选择，已退出")
            return

    if not selected_items:
        print("没有选择内容")
        return

    print(f"\n已选择 {len(selected_items)} 个内容，开始处理...\n")

    # 处理选中的内容
    for item in selected_items:
        await process_single_url(item.url, config, state)
        # 每处理完一个保存状态
        save_state(state)

    print("\n[OK] 批量处理完成")


async def url_mode(urls: List[str], config, state: dict):
    """URL模式：直接处理指定URL"""
    for url in urls:
        success = await process_single_url(url, config, state)
        if success:
            # 保存状态
            save_state(state)


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description='Content Summarizer - 内容订阅与AI摘要工具'
    )

    parser.add_argument(
        'mode',
        choices=['batch', 'url'],
        help='运行模式: batch(批量模式) 或 url(URL模式)'
    )

    parser.add_argument(
        'urls',
        nargs='*',
        help='URL模式下的URL列表'
    )

    args = parser.parse_args()

    # 加载配置
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"❌ 配置文件错误: {e}")
        print("\n请复制 config/sources.yaml.example 为 config/sources.yaml 并配置")
        sys.exit(1)

    # 检查API Key
    if not config.ai.api_key:
        print("❌ 错误: 未配置API Key")
        print("请设置环境变量 OPENAI_API_KEY 或在 config/sources.yaml 中配置")
        sys.exit(1)

    # 加载状态
    state = load_state()

    # 运行
    if args.mode == 'batch':
        asyncio.run(batch_mode(config, state))
    elif args.mode == 'url':
        if not args.urls:
            print("❌ 错误: URL模式下需要提供URL")
            parser.print_help()
            sys.exit(1)
        asyncio.run(url_mode(args.urls, config, state))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
