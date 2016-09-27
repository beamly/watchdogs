#!/usr/bin/env python
"""
Tests the users in a Mailchimp account

Required config.py variables:

MAILCHIMP_API_KEY         String       Your mailchimp API key

MAILCHIMP_DATACENTER      String       Your mailchimp datacenter (The last 3 characters of your API key, e.g.
                                       if your API key is 123456789-us4, your datacenter is us4.

MAILCHIMP_VALID_EMAILS    List         A list of email addresses for valid Mailchimp users

"""

import os
import imp
import pytest
import requests
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def _all_mailchimp_team_members():
    """
    Returns a list of members for a given mailchimp account, each represented as a dictionary.
    (See https://apidocs.mailchimp.com/api/2.0/users/logins.php for fields)
    """
    uri = "https://{0}.api.mailchimp.com/2.0//users/logins.json?apikey={1}-us4".format(CONFIG.MAILCHIMP_DATACENTER, CONFIG.MAILCHIMP_API_KEYS)
    response = requests.get(uri)
    all_mailchimp_users = response.json()
    return [user['email'] for user in all_mailchimp_users]

@pytest.mark.parametrize("email", _all_mailchimp_team_members())
def test_mailchimp_user(email):
    """
    Assert that all email addresses of all users in Mailchimp are known
    """
    assert email in CONFIG.MAILCHIMP_VALID_EMAILS