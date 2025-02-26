"""
Pushover notification implementation
"""
import http.client
import urllib.parse
from typing import Optional
from .base import NotifierProtocol, NotifierFactory


class PushoverNotifier(NotifierProtocol):
    """Pushover notification implementation"""
    
    def __init__(self, user_key: str, app_token: str, device: Optional[str] = None):
        self._user_key = user_key
        self._app_token = app_token
        self._device = device
    
    def send(self, message: str, title: Optional[str] = None) -> None:
        """Send notification via Pushover"""
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        
        payload = {
            "token": self._app_token,
            "user": self._user_key,
            "title": title,
            "message": message,
        }
        
        if self._device:
            payload["device"] = self._device
            
        conn.request(
            "POST",
            "/1/messages.json",
            urllib.parse.urlencode(payload),
            {"Content-type": "application/x-www-form-urlencoded"}
        )
        
        response = conn.getresponse()
        if response.status != 200:
            raise RuntimeError(f"Failed to send Pushover message: {response.read().decode()}")
    
    @classmethod
    def from_config(cls, config: dict) -> 'PushoverNotifier':
        """Create instance from config"""
        if 'user_key' not in config:
            raise ValueError("Pushover user key is required")
        if 'app_token' not in config:
            raise ValueError("Pushover app token is required")
        
        return cls(
            user_key=config['user_key'],
            app_token=config['app_token'],
            device=config.get('device')  # Optional device name
        )


# Register the Pushover notifier
NotifierFactory.register('pushover', PushoverNotifier)
