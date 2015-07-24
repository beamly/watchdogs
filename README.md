![Watchdogs Logo](./docs/logo.png)  Watchdogs
=============================================

The Beamly Watchdogs are a collection of simple, lightweight python unit tests 
each designed to test different aspects the security of your cloud infrastructure 
and third party services.

Tests can be cherry picked and combined to create a continuously running 
security audit capable of generating security alerts.

An example of _some_ of the things watchdogs can check for:

- All your AWS IAM users are known
- All your AWS IAM users with a password set have logged in in the last X days and have 2FA enabled
- All your IAM users access keys have been used in the last X days
- All of the Github accounts in your organisation are known
- All Github accounts have two factor authentication (2FA) enabled
- All your Slack users are valid members of the organisation
- All your Slack users have 2FA enabled
- Ensure that all IP addresses in your AWS security groups are known

```
============================= test session starts ==============================
platform linux2 -- Python 2.7.3 -- py-1.4.27 -- pytest-2.7.1
rootdir: /var/lib/go-agent-3/pipelines/SecurityAudit/tests, inifile:
collected 1280 items

test_atlassian_users.py ........................................................
test_aws_iam_users.py ..........................................................
test_aws_security_groups.py ....................................................
test_github_hooks.py ...........................................................
test_github_users.py ...........................................................
test_o365_users.py .............................................................
test_onelogin_users.py .........................................................
test_pagerduty_users.py ........................................................
test_slack_users.py .....................................F......................

=================================== FAILURES ===================================
_____________________________ test_slack_users[60] _____________________________

realname = ’New Joiner', two_factor_enabled = False

    def two_factor_enabled(realname, two_factor_enabled):

>       assert two_factor_enabled
E       assert False

test_slack_users:42: AssertionError
=================== 1 failed, 1279 passed in 145.26 seconds ====================
```

Our goal is to build a comprehensive set of simple security validation scripts
for a vast range of services that operations teams can pick and choose from.

Getting Started
----------------

### 1. Fork this repo

### 2. Install dependencies

We recommend first creating a virtualenv:
```
pip install virtualenv
virtualenv watchdog
source watchdog/bin/activate
```

Before installing the requirements using pip:
```
pip install -r requirements.txt
```

### 3. Enable the scripts you want to run

There are two directories in the repo `available_tests` and `enabled_tests`.
`enabled_tests` contains every test available, and the idea is you symlink the
scripts you want to run in to `enabled_scripts` (Run these commands in the root
of the repo)

````
ln -s ../available_tests/test_pagerduty_users.py enabled_tests/test_pagerduty_users.py
````

### 4. Write a configuration file (config.py)

`config.py` is a python script containing your secret, organisation specific data \
required for your chosen tests to run, including:

- API Keys
- User names/passwords
- Exceptions

To find the variables that each script needs refer to the comments section
of each individual script.

The configuration file is usually stored in a seperate repository with tight
access control, and is loaded dynamically by the scripts from the location
set in the WATCHDOG_CONFIG_LOCATION environment variable.

#### 5. Execute the scripts

Set the environment WATCHDOG_CONFIG variable to point to your populated config file:
```
export WATCHDOG_CONFIG_LOCATION='/Users/neil/r/watchdogs/config.py'
```
Run using py.test
```
(watchdog)neil@Neils-MacBook-Pro-2:~/r/watchdogs$ py.test enabled_tests/*
============================= test session starts =============================
platform darwin -- Python 2.7.6 -- py-1.4.24 -- pytest-2.6.2
collected 24 items

enabled_tests/test_pagerduty_users_all_valid.py ........................

========================== 24 passed in 2.60 seconds ==========================
```

Contributing
------------

Note: We're in the process of putting together a Contributor Licence Agreement,
No pull requests will be merged until we've got that in place - Sorry!

Our goal is to build a comprehensive set of security scripts that can be cherry
picked by organisation to audit as many services as possible, therefore we
will aim to merge pull requests as quickly as possible (within 48 hours). To
help us do this, we ask that all test scripts satisfy the following requirements:

### 1. Documentation

To help others integrate your script quickly, please be sure to include details
of all the config.py variables it requires in a docstring at the top of the file,
with examples if you're using a dictionary.

### 2. Loading config

Configuration should be loaded using the following code:

```
import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])
```

And variables accessed using CONFIG.<VARNAME>

### 3. pylint

We ask that all contributions have a perfect pylint score of 10.00 when
line length and member checks are disabled (pylint is installed as part of
watchdogs requirements):

```
pylint available_tests/test_pagerduty_users_all_valid.py --disable=line-too-long --disable=maybe-no-member

<snip>

Global evaluation
-----------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)

```


