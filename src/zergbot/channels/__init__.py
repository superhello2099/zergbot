"""Chat channels module with plugin architecture."""

from zergbot.channels.base import BaseChannel
from zergbot.channels.manager import ChannelManager

__all__ = ["BaseChannel", "ChannelManager"]
