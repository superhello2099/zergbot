"""Configuration module for zergbot."""

from zergbot.config.loader import load_config, get_config_path
from zergbot.config.schema import Config

__all__ = ["Config", "load_config", "get_config_path"]
