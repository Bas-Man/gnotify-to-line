.. _installation:

Installation
============

I recommand the use of a virtual environment to isolate the dependencies.

Install `gmail2notification` using pip. There are two main options

.. code-block:: sh

    pip install git+https://github.com/bas-man/gmail2notification

Alternatively you can install it using as an egg which will allow you to both run and edit the g2notification code.
This requires that you download the source code before installing.

.. code-block:: sh

    pip install -e .["dev"]

You will need a Gmail API key. Follow these steps to set up authentication:

1. Go to the Google Cloud Console.
2. Create a project and enable Gmail API.
3. Generate OAuth credentials and save the JSON file.
