#!/usr/bin/env python
"""
Tests the users in a Mailchimp account

Required config.py variables:

MAILCHIMP_API_KEY         String       Your mailchimp API key

MAILCHIMP_DATACENTER      String       Your mailchimp datacenter (The last 3 characters of your API key, e.g.
                                       if your API key is 123456789-us4, your datacenter is us4.

MAILCHIMP_VALID_EMAILS    List         A list of email addresses for valid Mailchimp users

"""

import requests
import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def get_all_mailchimp_team_members(datacenter, api_key):
    """
    Returns a list of members for a given mailchimp account, each represented as a dictionary.
    (See https://apidocs.mailchimp.com/api/2.0/users/logins.php for fields)
    """

    uri = "https://{0}.api.mailchimp.com/2.0//users/logins.json?apikey={1}-us4".format(datacenter, api_key)
    response = requests.get(uri)
    all_mailchimp_users = response.json()
    return all_mailchimp_users

def test_unknown_mailchimp_users():
    """
    Assert that all email addresses of all users in Mailchimp are known
    """
    all_mailchimp_users = get_all_mailchimp_team_members(datacenter=CONFIG.MAILCHIMP_DATACENTER, api_key=CONFIG.MAILCHIMP_API_KEYS)
    for user in all_mailchimp_users:
        yield email_is_in_valid, user['email'].lower()

def email_is_in_valid(mailchimp_email_address):
    """
    Assert that the email address of a single Mailchimp user is valid/active
    """
    valid_emails = [email.lower() for email in CONFIG.MAILCHIMP_VALID_EMAILS]
    assert mailchimp_email_address in valid_emails
