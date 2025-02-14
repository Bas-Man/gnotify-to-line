# g2line (Gmail to LINE Notifier)

## Purpose

g2line is a Python-based utility that connects to Gmail through the Google API to monitor specific emails and automatically forward them as notifications to LINE messenger. It's particularly useful for:

- Monitoring important emails based on Gmail labels
- Automatically sending notifications to LINE when matching emails are received
- Processing email content using configurable regex patterns
- Supporting multiple notification services (LINE and Pushover)

## Requirements

1. Python 3.7 or higher
2. A Google Cloud Project with Gmail API enabled
3. A LINE Notify account and token
4. Gmail account with configured labels

You need to set up a LINE Notify token and configure your LINE group to receive notifications. For LINE setup instructions, see: [Setting up LINE Notifications](https://gmailzapierlinenotify.readthedocs.io/en/latest/setting-up-line.html)

## Installation

You can install g2line directly from GitHub:

```bash
pip install git+https://github.com/Bas-Man/gnotify-to-line.git
```

Dependencies will be automatically installed, including:
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- line-notify
- python-dotenv
- toml

## Configuration:

#### Required files:

1. config.toml - This is the main configuration file.

2. credentials.json

3. token.pickle

`credentials.json` is obtained from Google and `token.pickle` is generated when you run the script and authenticate against Google. `config.toml` is the file you will need to manage by hand.

The configuration files are expected to live in your home directory under *` ~/.config/gmail2line/*

#### Sample Configuration

```toml
[log]
# Level of logging that the script should run at.
lvl = 'INFO' # Lvls: INFO, DEBUG, WARN

[gmail]
# Google Search String. The labels as seen below are applied by Gmail
# through its filtering system. You will need to set this up.
search = '((label:kidsduo OR label:pasmo OR label:nichinoken OR label:linenotification) AND -label:notified) AND newer_than:1d'
# If archive is true. Then processed emails will be removed from
# the Gmail 'INBOX'. Note that this archive level is overwritten
# by service specific settings if present.
archive = false

# This is the list of supported services.
[services]
  [services.bus]
  # From Address
  sender = "noreply@tskids.jp"
  # Email subject. This is a list as there is the need to support more
  # than one in some cases.
  subjects = [ "エキッズ" ]
  # Regular expression for extracting data from the email for use in the
  # notification message
  regex = '(?P<date>\d{2}月\d{2}日)\s(?P<time>\d{2}時\d{2}分)(?:\r)?\nREPLACEME(?:\r)?\n「(?P<busname>[一-龯]\d{1,2})\s(?P<destination>[一-龯]+)行き・(?P<boardedat>[一-龯]+)」'
  # Service level archive setting. Overrides Gmail level setting if 
  # present. If archive is not present. Gmail setting is used. If 
  # it is present. It overrides Gmail settings.
  archive = true
  [services.train]
  sender = "東急セキュリティ <tskids@goopas.jp>"
  subjects = ["エキッズ" ]
  enter = "入場"
  exit = "出場"
  regex = '(?P<date>\d{2}月\d{2}日)　(?P<time>\d{2}時\d{2}分)\nREAPLACEME\n「(?P<provider>[一-龯]+)・(?P<station>.*)」を(?P<enterexit>[一-龯]+)'

# The people section is provided so you can have a consistent name
# in the message. Several services provide variations on a name depending on 
# how you have registered the person. Some might be full-width Hiragana.
# Some might be half-width. In Japan, some might be 'lastname' then
# 'firstname' 
# While others might just report a first name. So this section creates 
# a mapping of the name in the email to the name you would 
# like to see in the notification. If this section is not provided then
# the name in the email will be used.
[people]
  [people.name]
  names = ["name1", "name2" ....]
```

### Secrets and Tokens

These need to be kept secure as such the following things should be kept in mind.

1. They should never be stored in Git. So they should be added to the `.gitignore` file. This includes the files `credentials.json` and `token.pickle`

2. Gmail `label` and Line `Token` are expected to be set as shell environment variables to work with the script. This should prevent them from being leaked from the code.

## Running g2line

### Initial Setup

1. First, set up your Google Cloud Project and enable the Gmail API:
   - Follow [this guide](https://dev.to/basman/connecting-to-gmail-api-with-python-546b) for detailed instructions
   - Download your `credentials.json` file from Google Cloud Console
   - Place `credentials.json` in `~/.config/gmail2line/`

2. Set up required environment variables:
   ```bash
   export GMAIL_LABEL=your_gmail_label
   export LINE_ACCESS_TOKEN=your_line_token
   ```

3. First run of g2line:
   ```bash
   g2line
   ```
   This will:
   - Authenticate with Google (creates `token.pickle`)
   - Verify your configuration
   - Start monitoring emails

### Automation

g2line can be automated using either cron or systemd:

#### Using systemd (Recommended)

1. Create the following files in `~/.config/systemd/user/`:
   - `gnotifier.service`
   - `gnotifier.timer`

2. Enable and start the service:
   ```bash
   systemctl --user enable gnotifier.service
   systemctl --user start gnotifier.service
   ```

3. Check service status:
   ```bash
   systemctl --user status gnotifier.service
   ```

#### Using cron

Add an entry to your crontab, making sure to include the required environment variables:

```bash
crontab -e
# Add line like:
*/5 * * * * export GMAIL_LABEL=label LINE_ACCESS_TOKEN=token; /path/to/g2line
```

## Regular Expression Configuration

g2line uses regular expressions to extract relevant information from email content. The default regex patterns are configured for Japanese email formats, but you can customize them for your needs:

- Use [regex101](https://regex101.com) to test your patterns
- Ensure your regex includes named capture groups for data extraction
- Reference sample patterns:
  - [Bus notification pattern](https://regex101.com/r/iErPZQ/4)
  - [Train notification pattern](https://regex101.com/r/zQvrg3/5)

Customize the regex patterns in your `config.toml` file to match your email formats.
