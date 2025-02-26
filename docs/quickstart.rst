Quick Start
===========

Here’s a basic example to fetch emails and send a notification:

.. code-block:: python

    from gmail2notification.gmail import GmailClient
    from gmail2notification.notifiers.line import LineNotifier

    client = GmailClient("credentials.json")
    emails = client.get_emails(label="INBOX")

    notifier = LineNotifier(access_token="your_token_here")
    notifier.send_message(f"You have {len(emails)} new emails!")

Configuration File
__________________

Including a TOML Configuration
==============================

You can configure the application using a `config.toml` file:

.. literalinclude:: ../tests/toml/config.toml
   :language: toml
   :linenos:

