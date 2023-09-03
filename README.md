## Purpose

This is a script that connects to Google's Gmail Service through its API. Collects a select set of emails. Then based on the contents of these emails it sends LINE message Notifications. 

## Package Installation

Download the package from github and simply run:

```bash
pip install <Package Name>
```

## Configuration:

#### Required files:

1. config.toml

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
  regex = 'r"""(?P<date>\d{2}月\d{2}日)\s(?P<time>\d{2}時\d{2}分)(?:\r)?\nREPLACEME(?:\r)?\n「(?P<busname>[一-龯]\d{1,2})\s(?P<destination>[一-龯]+)行き・(?P<boardedat>[一-龯]+)」"""'
  # Service level archive setting. Overrides Gmail level setting if 
  # present. If archive is not present. Gmail setting is used. If 
  # it is present. It overrides Gmail settings.
  archive = true
  [services.train]
  sender = "東急セキュリティ <tskids@goopas.jp>"
  subjects = ["エキッズ" ]
  enter = "入場"
  exit = "出場"
  regex = 'r"""(?P<date>\d{2}月\d{2}日)　(?P<time>\d{2}時\d{2}分)\nREAPLACEME\n「(?P<provider>[一-龯]+)・(?P<station>[一-龯]+)」を(?P<enterexit>[一-龯]+)"""'

```



### Secrets and Tokens

These need to be kept secure as such the following things should be kept in mind.

1. They should never be stored in git. So they should be added to the `.gitignore` file. This includes the files `credentials.json` and `token.pickle`

2. Gmail `label` and Line `Token` are expected to be set as shell environment variables to work with the script. This should prevent them from being leaked from the code.

## Running the script

If you found this code first on github, I would direct you to [this article series.](https://dev.to/basman/connecting-to-gmail-api-with-python-546b) This will walk you through setting things up with Google.

After going to the Google Quick start. You should have downloaded your `credentials.json` file. Run the gmail-sample.py 

### First Run

This will confirm that you are connecting to gmail successfully. If you do not see a list of labels. Work through the google trouble shooting.

If successful delete the following code:

```python
# Stage 1 Check Connection
list_labels_on_setup(service)
sys.exit(0)
# Delete from service = get_service() to this line
```

### Second Run

In the code you will need to set the varible `name` to some label name you wish to use.  
Then run the script. This will report the label_id that google assigned to this new label. For simplicity, don't manually create the label.  
Add the label_id to the secrets.py file.

Delete the next section of code:

```python
# Stage 2 Create New Label
  if secrets.LABEL_ID == "":
      print("We are creating a new label.")
      # Replace "" with the label name you wish to use.
      name = ""
      if len(name) == 0:
          print("You have not yet set name See 'name = ""' in the code above")
          print("Do that now and run the script again")
          sys.exit(0)
      new_label = define_label(name)
      new_label = add_label_to_gmail(service, new_label, logger)
      print(f"Your new label ID is: {get_new_label_id(new_label)}")
      print("Set this in secrets.py")
      sys.exit(0)
  # Delete from service = get_service() to this line
```

At this point you should have a working sample code.

## Customising the script.

You will need to update the code in the following section:

```python
if notifier == "NOTE1":
    logger.debug("Note1")
    # Your custom code goes here. Bot / Line
    processed = True
elif notifier == "NOTE2":
    logger.debug("Note2")
    # Your custom code goes here. Bot / Line
    processed = True
```

If you are confused. Take a look at gmail.py which is my current working implementation.

## Automating Script Execution

You can either use good old Cron or systemd.
I have included a copy of the two files for systemd which should be located in the `/etc/systemd/system/` directory on your system.  
You will need to modify the path details and the timers to your own needs.



## Notes on Regular Expressions.

The sample provided is based on my own needs here in Japan. If you are planning to use this in another country with another language. You will need to research how to create the needed `regex` strings. The function that performs the regex 

[regex101](https://regex101.com) will be your best friend for this.

### Sample Regex Links

[Bus](https://regex101.com/r/iErPZQ/4)

[Train](https://regex101.com/r/zQvrg3/5)
