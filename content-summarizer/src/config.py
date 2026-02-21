"""配置加载模块"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"


@dataclass
class AIConfig:
    """AI配置"""
    provider: str
    base_url: str
    model: str
    api_key: str


@dataclass
class SummaryConfig:
    """摘要配置"""
    length: str
    custom_words: int


@dataclass
class OutputConfig:
    """输出配置"""
    root: str
    format: str


@dataclass
class Source:
    """订阅源"""
    name: str
    type: str
    url: str
    enabled: bool


@dataclass
class Config:
    """全局配置"""
    sources: list
    ai: AIConfig
    summary: SummaryConfig
    output: OutputConfig


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """加载YAML文件"""
    if not file_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def expand_env_vars(value: Any) -> Any:
    """展开环境变量"""
    if isinstance(value, str):
        # 展开 ${VAR} 或 $VAR 格式的环境变量
        if value.startswith('${') and value.endswith('}'):
            var_name = value[2:-1]
            return os.environ.get(var_name, '')
        elif value.startswith('$'):
            var_name = value[1:]
            return os.environ.get(var_name, '')
        return value
    elif isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [expand_env_vars(v) for v in value]
    return value


def load_config(config_path: Optional[Path] = None) -> Config:
    """加载配置文件"""
    if config_path is None:
        config_path = CONFIG_DIR / "sources.yaml"

    data = load_yaml(config_path)
    data = expand_env_vars(data)

    # 构建AI配置
    ai_data = data.get('ai', {})
    ai_config = AIConfig(
        provider=ai_data.get('provider', 'openai'),
        base_url=ai_data.get('base_url', 'https://api.openai.com/v1'),
        model=ai_data.get('model', 'gpt-4o-mini'),
        api_key=ai_data.get('api_key', '')
    )

    # 构建摘要配置
    summary_data = data.get('summary', {})
    summary_config = SummaryConfig(
        length=summary_data.get('length', 'medium'),
        custom_words=summary_data.get('custom_words', 2000)
    )

    # 构建输出配置
    output_data = data.get('output', {})
    output_config = OutputConfig(
        root=output_data.get('root', './output'),
        format=output_data.get('format', 'markdown')
    )

    # 构建订阅源列表
    sources = []
    for s in data.get('sources', []):
        sources.append(Source(
            name=s.get('name', ''),
            type=s.get('type', ''),
            url=s.get('url', ''),
            enabled=s.get('enabled', True)
        ))

    return Config(
        sources=sources,
        ai=ai_config,
        summary=summary_config,
        output=output_config
    )


def load_state() -> Dict[str, Any]:
    """加载状态文件"""
    state_path = CONFIG_DIR / "state.yaml"
    if not state_path.exists():
        return {'version': '1.0', 'last_scan': None, 'processed': {}}
    return load_yaml(state_path)


def save_state(state: Dict[str, Any]) -> None:
    """保存状态文件"""
    state_path = CONFIG_DIR / "state.yaml"
    with open(state_path, 'w', encoding='utf-8') as f:
        yaml.dump(state, f, allow_unicode=True, default_flow_style=False)


def load_prompt_template() -> str:
    """加载AI改写提示词模板"""
    prompt_path = CONFIG_DIR / "rewrite-prompt.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"提示词模板不存在: {prompt_path}")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_output_dir() -> Path:
    """获取输出目录"""
    config = load_config()
    output_root = PROJECT_ROOT / config.output.root
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root
