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
import pytest

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def _all_onelogin_users():
    onelogin_xml = requests.get("https://app.onelogin.com/api/v2/users.xml", auth=HTTPBasicAuth(CONFIG.ONELOGIN_API_KEY, ',x'))
    dom = BeautifulSoup(onelogin_xml.text)
    return [email.contents[0] for email in dom.findAll('email')]

@pytest.mark.parametrize("email_address", _all_onelogin_users())
def test_onelogin_users(email_address):
    """
    Assert that all email addresses of all users in Onelogin are known
    """
    assert email_address in CONFIG.ONELOGIN_VALID_EMAILS