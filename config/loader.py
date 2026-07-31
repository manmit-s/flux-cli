from pathlib import Path
import os
from typing import Any
from platformdirs import user_config_dir, user_data_dir
import tomli

from config.config import Config

from utils.errors import ConfigError

import logging

logger = logging.getLogger(__name__)
CONFIG_FILE_NAME = 'config.toml'
AGENT_MD_FILE = 'AGENT.md'
 
def get_config_dir() -> Path:
    return Path(user_config_dir("flux-cli", appauthor=False))

def get_data_dir() -> Path:
    return Path(user_data_dir('flux-cli'))

def get_system_config_path() -> Path:
    return get_config_dir() / CONFIG_FILE_NAME

def _parse_toml(path: Path):
    try:
        with open(path, 'rb') as f:
            return tomli.load(f)

    except tomli.TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML in {path}: {e}", config_file=str(path)) from e
    except (OSError, IOError) as e:
        raise ConfigError(f"Failed to read config file {path}: {e}", config_file=str(path)) from e
            
def _get_project_config(cwd: Path) -> Path | None:
    current = cwd.resolve()
    agent_dir = current / '.flux-cli'

    if agent_dir.is_dir():
        config_file = agent_dir / CONFIG_FILE_NAME
        if config_file.is_file():
            return config_file
    
    return None

def _get_agent_md_files(cwd: Path) -> Path | None:
    current = cwd.resolve()
    agent_dir = current / '.flux-cli'

    if agent_dir.is_dir():
        agent_md_file = current / AGENT_MD_FILE
        if agent_md_file.is_file():
            content = agent_md_file.read_text(encoding='utf-8')
            return content
    
    return None

def _merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value

    return result
        

def load_config(cwd: Path | None) -> Config:
    cwd = cwd or Path.cwd()
    
    system_path = get_system_config_path()

    config_dict: dict[str, Any] = {}

    if system_path.is_file():
        try:
            config_dict = _parse_toml(system_path)
        except ConfigError:
            logger.warning(f"Skipping invalid sustem config: {system_path}")

    
    project_path = _get_project_config(cwd)
    if project_path:
        try:
            project_config_dict = _parse_toml(project_path)
            config_dict = _merge_dicts(config_dict, project_config_dict)
        except ConfigError:
            logger.warning(f"Skipping invalid sustem config: {system_path}")

    if 'cwd' not in config_dict:
        config_dict['cwd'] = cwd

    if 'developer_instructions' not in config_dict:
        agent_md_content = _get_agent_md_files(cwd)
        if agent_md_content:
            config_dict['developer_instructions'] = agent_md_content

    if "api_key" in config_dict and isinstance(config_dict["api_key"], str):
        if not os.environ.get("API_KEY"):
            os.environ["API_KEY"] = config_dict["api_key"]

    if "base_url" in config_dict and isinstance(config_dict["base_url"], str):
        if not os.environ.get("BASE_URL"):
            os.environ["BASE_URL"] = config_dict["base_url"]

    try:
        config = Config(**config_dict)
    except Exception as e:
        raise ConfigError(f"Invalid configuration: {e}") from e
    return config