"""
LINE Notify implementation
"""
from typing import Optional
from line_notify import LineNotify
from .base import NotifierProtocol, NotifierFactory


class LineNotifier(NotifierProtocol):
    """LINE Notify implementation"""
    
    def __init__(self, token: str):
        self._notifier = LineNotify(token)
    
    def send(self, message: str, title: Optional[str] = None) -> None:
        """Send notification via LINE"""
        self._notifier.send(message)
    
    @classmethod
    def from_config(cls, config: dict) -> 'LineNotifier':
        """Create instance from config"""
        if 'token' not in config:
            raise ValueError("LINE token is required")
        return cls(config['token'])


# Register the LINE notifier
NotifierFactory.register('line', LineNotifier)
