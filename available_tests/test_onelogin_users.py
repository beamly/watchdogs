#!/usr/bin/env python
"""
When Onelogin is connected to a directory users are created in Onelogin but are
not removed when the user is removed from LDAP. While not necessarily a security
concern (As users still need to authenticate against the directory) this script
verifies that all Onelogin users are known.

Required config.py variables:

ONELOGIN_API_KEY       String       The API key used to conncet to Onelogin

"""

import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def test_unknown_onelogin_users():
    """
    Assert that all email addresses of all users in Onelogin are known
    """
    onelogin_xml = requests.get("https://app.onelogin.com/api/v2/users.xml", auth=HTTPBasicAuth(CONFIG.ONELOGIN_API_KEY, ',x'))
    dom = BeautifulSoup(onelogin_xml.text)
    onelogin_emails = [email.contents[0] for email in dom.findAll('email')]
    for email in onelogin_emails:
        yield email_is_in_valid, email.lower()

def email_is_in_valid(onelogin_email_address):
    """
    Assert that the email address of a single Onelogin user is valid/active
    """
    valid_emails = [email.lower() for email in CONFIG.ONELOGIN_VALID_EMAILS]
    assert onelogin_email_address in valid_emails
