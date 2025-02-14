"""
Base protocol and factory for notification services
"""
from typing import Dict, Optional, Type
from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class NotifierProtocol(Protocol):
    """Protocol defining the interface for notification services"""
    
    def send(self, message: str, title: Optional[str] = None) -> None:
        """
        Send a notification message
        
        Args:
            message: The message to send
            title: Optional title for the notification
        """
        ...

    @classmethod
    def from_config(cls, config: dict) -> 'NotifierProtocol':
        """
        Create a notifier instance from configuration
        
        Args:
            config: Configuration dictionary containing necessary credentials/settings
        
        Returns:
            An instance of the notifier
        """
        ...


class NotifierFactory:
    """Factory for creating notifier instances"""
    
    _notifiers: Dict[str, Type[NotifierProtocol]] = {}
    
    @classmethod
    def register(cls, name: str, notifier_class: Type[NotifierProtocol]) -> None:
        """Register a new notifier type"""
        cls._notifiers[name] = notifier_class
    
    @classmethod
    def create(cls, name: str, config: dict) -> NotifierProtocol:
        """Create a notifier instance by name and config"""
        if name not in cls._notifiers:
            raise ValueError(f"Unknown notifier type: {name}")
        return cls._notifiers[name].from_config(config)
