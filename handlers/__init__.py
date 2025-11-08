# handlers/__init__.py
from .command_handlers import router as command_router
from .callback_handlers import router as callback_router
from .message_handlers import router as message_router
from .reply_handler import router as reply_router

__all__ = ['command_router', 'callback_router', 'message_router', 'reply_router']