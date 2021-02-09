## Purpose
This is a script that connects to Google's Gmail Service through its API. Collects a select set of emails. Then based on the contents of these emails. Sends LINE message Notifications. This could be modified to send messages to other services, Discord, Telegram and more.

## Package Installation

If you are not interested in using the line_notify module. Remove it before using pip.

```
pip3 install -r requirements.txt
```

## Create some required files.

### constants.py
Give these constants slightly more memorable / understandable names.
This file simplifies the management when processing emails from several different sources.
```python
FROM_1 = "local@domain"
FROM_2 = "local@domain2"

SUB_1 = "Subject Line"
SUB_2 = "Subject Line"

SUBJECTS = [SUB_1, SUB_2]
```

### secrets.py
This file is where you might keep some of your secrets. Though I would probably recommend that you move these to being environment variables instead.  
**Note**: You should have this file listed in your .gitignore file. It should not be uploaded to GitHub.

```python
SEARCH_STRING = "GMail search String"

# Notifier laben ID
LABEL_ID = "Gmail Label ID String"

LINE_TOKEN = "My Secret Token for LINE"

NAME = "A Name"
```
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
