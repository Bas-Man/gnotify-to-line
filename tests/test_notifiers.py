"""Tests for the notification system"""
import os
import pytest
from typing import Optional
from typing_extensions import Protocol
from dotenv import load_dotenv, find_dotenv

from gmail2line.notifiers.base import NotifierFactory, NotifierProtocol
from gmail2line.notifiers.line_notifier import LineNotifier
from gmail2line.notifiers.pushover_notifier import PushoverNotifier

# Load environment variables from .env file
load_dotenv()


# Fixtures
@pytest.fixture
def test_token():
    return "test-token-123"


@pytest.fixture
def test_message():
    return "Test notification message"


@pytest.fixture
def line_notifier(test_token):
    return LineNotifier(test_token)


@pytest.fixture
def config_with_token(test_token):
    return {"token": test_token}


# LineNotifier Tests
def test_line_notifier_creation(line_notifier):
    """Test LineNotifier instance creation"""
    assert isinstance(line_notifier, LineNotifier)
    assert isinstance(line_notifier, NotifierProtocol)


def test_from_config_with_valid_config(test_token, config_with_token):
    """Test creating LineNotifier from valid config"""
    notifier = LineNotifier.from_config(config_with_token)
    assert isinstance(notifier, LineNotifier)
    # We can't access the token directly, but we can verify the notifier works
    assert notifier._notifier is not None


def test_from_config_with_missing_token():
    """Test creating LineNotifier with missing token raises error"""
    with pytest.raises(ValueError, match="LINE token is required"):
        LineNotifier.from_config({})


def test_send_notification(mocker, test_token, test_message):
    """Test sending notification"""
    # Create a mock LineNotify instance
    mock_line_notify = mocker.patch('gmail2line.notifiers.line_notifier.LineNotify')
    mock_instance = mock_line_notify.return_value

    # Create notifier and send message
    notifier = LineNotifier(test_token)
    notifier.send(test_message)

    # Verify the message was sent with correct parameters
    mock_instance.send.assert_called_once_with(test_message)


# NotifierFactory Tests
def test_register_and_create_line_notifier(config_with_token):
    """Test registering and creating a LINE notifier"""
    # LineNotifier should be auto-registered in line_notifier.py
    notifier = NotifierFactory.create("line", config_with_token)
    assert isinstance(notifier, LineNotifier)
    assert isinstance(notifier, NotifierProtocol)


def test_create_unknown_notifier():
    """Test creating an unknown notifier type raises error"""
    with pytest.raises(ValueError, match="Unknown notifier type: unknown"):
        NotifierFactory.create("unknown", {})


def test_register_new_notifier_type():
    """Test registering a new notifier type"""
    # Create a mock notifier class
    class MockNotifier(NotifierProtocol):
        def send(self, message: str, title: Optional[str] = None) -> None:
            pass

        @classmethod
        def from_config(cls, config: dict) -> 'MockNotifier':
            return cls()

    # Register the mock notifier
    NotifierFactory.register("mock", MockNotifier)

    # Create an instance
    notifier = NotifierFactory.create("mock", {})
    assert isinstance(notifier, MockNotifier)
    assert isinstance(notifier, NotifierProtocol)


@pytest.mark.skipif(
    not os.getenv("LINE_TOKEN_PERSONAL_DISABLED"),
    reason="LINE_TOKEN_PERSONAL not found in .env file"
)
def test_live_line_notification():
    """Integration test with real LINE Notify service"""
    token = str(os.getenv("LINE_TOKEN_PERSONAL"))
    notifier = LineNotifier(token)
    test_message = "🧪 Test message from gmail2line integration test"
    
    # This will actually send a notification if LINE_NOTIFY_TOKEN is set in .env
    notifier.send(test_message)


@pytest.mark.skipif(
    not (os.getenv("PUSHOVER_USER_KEY_DISABLED") and os.getenv("PUSHOVER_APP_TOKEN")),
    reason="PUSHOVER_USER_KEY or PUSHOVER_APP_TOKEN not found in .env file"
)
def test_live_pushover_notification():
    """Integration test with real Pushover service"""
    user_key = str(os.getenv("PUSHOVER_USER_KEY"))
    app_token = str(os.getenv("PUSHOVER_APP_TOKEN"))
    notifier = PushoverNotifier(user_key, app_token)
    test_message = "🧪 Test message from gmail2line integration test"
    
    # This will actually send a notification if Pushover credentials are set in .env
    notifier.send(test_message, title="Test title2")
