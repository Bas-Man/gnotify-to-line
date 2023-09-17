## Purpose

This is a script that connects to Google's Gmail Service through its API. Collects a select set of emails. Then based on the contents of these emails it sends LINE message Notifications. 

## Requirements

You have already setup your **LINE** Group so that notifications can be sent to several users at once. **Please be aware that you need to setup the group within your Mobile Phone LINE.***

See: [Setting up LINE. &mdash; Gmail + Zapier + LINE Notifications 0.1.0 documentation](https://gmailzapierlinenotify.readthedocs.io/en/latest/setting-up-line.html)

## Package Installation

Download the package from github and simply run:

```bash
pip install <Package Name>
```

## Configuration:

#### Required files:

1. config.toml - This is the main configuration file.

2. credentials.json

3. token.pickle

`credentials.json` is obtained from Google  and `token.pickle` is generated when you run the script and authenticate against Google. `config.toml` is the file you will need to manage by hand.

The configuration files are expected to live in your home directory under *` ~/.config/gmail2line/*

#### Sample Configuration

```toml
[log]
# Level of logging that the script should run at.
lvl = 'INFO' # Lvls: INFO, DEBUG, WARN

[gmail]
# Google search String. The label as seen below are applied by Gmail
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
  regex = '(?P<date>\d{2}月\d{2}日)　(?P<time>\d{2}時\d{2}分)\nREAPLACEME\n「(?P<provider>[一-龯]+)・(?P<station>[一-龯]+)」を(?P<enterexit>[一-龯]+)'

# The people section is provided so you can have a consistent name
# in message. Several services provide varations on a name depending on 
# how you have registered the person. Some might be full-width Hiragana.
# Some might be half-width. In Japan some might be 'lastname' then
# 'firstname' 
# While others might just report a first name. So this section creates 
# a mapping of the of thee name in the email to the name you would you 
# like to see in the notification. If this section is not provided then
# the name in the email will be used.
[people]
  [people.name]
  names = ["name1", "name2" ....]
```

### Secrets and Tokens

These need to be kept secure as such the following things should be kept in mind.

1. They should never be stored in git. So they should be added to the `.gitignore` file. This includes the files `credentials.json` and `token.pickle`

2. Gmail `label` and Line `Token` are expected to be set as shell environment variables to work with the script. This should prevent them from being leaked from the code.

## Running the script

If you found this code first on github, I would direct you to [this article series.](https://dev.to/basman/connecting-to-gmail-api-with-python-546b) This will walk you through setting things up with Google.

After going tthough the Google Quick start. You should have downloaded your `credentials.json` file. Run the gmail-sample.py 

### First Run

### Second Run

## ## Automating Script Execution

You can either use good old Cron or systemd.

### Note that you will need to set up the environment variables.

I have included a copy of the two files for systemd which should be located in your home directory under `.config/systemd/user/`. You you need both `gnotifier.service` and `gnotofier.timer` . Once these files are created and edited you can run the command `systemctl --user enable gnotifier.service` followed by `systemctl --user start gnotifier.service` You can check the status the service using `systemctl --user status gnotifier.service`

## Notes on Regular Expressions.



The sample provided is based on my own needs here in Japan. If you are planning to use this in another country with another language. You will need to research how to create the needed `regex` strings. The function that performs the regex 

[regex101](https://regex101.com) will be your best friend for this.

### Sample Regex Links

[Bus](https://regex101.com/r/iErPZQ/4)

[Train](https://regex101.com/r/zQvrg3/5)
