"""AI改写模块"""
import os
import json
import re
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

try:
    import openai
    from openai import AsyncOpenAI
except ImportError:
    print("Warning: openai not installed. Run: pip install openai")
    AsyncOpenAI = None

from ..config import load_config, load_prompt_template


# 摘要长度映射
LENGTH_MAP = {
    'short': 500,
    'medium': 1500,
    'long': 2500,
}


@dataclass
class SummaryResult:
    """摘要结果"""
    title: str              # 中文标题
    core_points: list       # 核心观点
    insights: list          # 关键洞察
    quotes: list            # 金句
    guests: list            # 嘉宾信息
    summary: str            # 摘要正文


class Summarizer:
    """AI摘要生成器"""

    def __init__(self, config=None):
        if config is None:
            config = load_config()

        self.config = config
        self.ai_config = config.ai
        self.summary_config = config.summary

        # 初始化OpenAI客户端
        if AsyncOpenAI:
            self.client = AsyncOpenAI(
                api_key=self.ai_config.api_key,
                base_url=self.ai_config.base_url
            )
        else:
            self.client = None

        # 加载提示词模板
        self.prompt_template = load_prompt_template()

    def _get_length_words(self) -> int:
        """获取目标摘要字数"""
        length = self.summary_config.length
        if length == 'custom':
            return self.summary_config.custom_words
        return LENGTH_MAP.get(length, 1500)

    def _build_prompt(self, transcript: str) -> str:
        """构建提示词"""
        # 替换模板中的占位符
        prompt = self.prompt_template
        prompt = prompt.replace('{length}', str(self._get_length_words()))
        prompt = prompt.replace('{transcript}', transcript)
        return prompt

    async def summarize(self, transcript: str) -> SummaryResult:
        """生成摘要"""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        prompt = self._build_prompt(transcript)

        try:
            response = await self.client.chat.completions.create(
                model=self.ai_config.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容分析师，擅长将长篇内容改写成结构化的中文摘要。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            content = response.choices[0].message.content
            return self._parse_response(content)

        except Exception as e:
            raise RuntimeError(f"AI调用失败: {e}")

    def _parse_response(self, content: str) -> SummaryResult:
        """解析AI响应"""
        # 尝试提取各个部分
        result = {
            'title': '',
            'core_points': [],
            'insights': [],
            'quotes': [],
            'guests': [],
            'summary': ''
        }

        # 尝试解析JSON
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                result.update(data)
            except json.JSONDecodeError:
                pass

        # 如果没有JSON，尝试文本解析
        if not result['title']:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith('# '):
                    result['title'] = line[2:].strip()
                elif '核心观点' in line:
                    # 收集接下来的列表项
                    j = i + 1
                    while j < len(lines):
                        item = lines[j].strip()
                        if item and (item.startswith('-') or item.startswith('1.') or item.startswith('•')):
                            result['core_points'].append(item.lstrip('-•123456789. '))
                        elif item and not item.startswith('#'):
                            break
                        j += 1
                elif '金句' in line:
                    j = i + 1
                    while j < len(lines):
                        item = lines[j].strip()
                        if item and (item.startswith('"') or item.startswith('「') or item.startswith('-')):
                            quote = item.strip().strip('"「」-')
                            if quote:
                                result['quotes'].append(quote)
                        elif item and not item.startswith('#'):
                            break
                        j += 1

        # 如果还是空的，直接使用原始内容作为摘要
        if not result['summary']:
            result['summary'] = content

        return SummaryResult(
            title=result.get('title', '未命名'),
            core_points=result.get('core_points', []),
            insights=result.get('insights', []),
            quotes=result.get('quotes', []),
            guests=result.get('guests', []),
            summary=result.get('summary', content)
        )


# 单例实例
_summarizer = None


def get_summarizer(config=None) -> Summarizer:
    """获取摘要生成器实例"""
    global _summarizer
    if _summarizer is None:
        _summarizer = Summarizer(config)
    return _summarizer
