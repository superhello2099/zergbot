"""Message bus module for decoupled channel-agent communication."""

from zergbot.bus.events import InboundMessage, OutboundMessage
from zergbot.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
