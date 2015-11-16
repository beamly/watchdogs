#!/usr/bin/env python
"""
Checks all members of a dropbox for business team are known

Required config.py variables:

DROPBOX_APP_ACCESS_TOKEN        String      The API key used to access your dropbox for
											business account (Requires permission type 'Team auditing')

DROPBOX_ALLOWED_EMAILS      List[String]    A list of all allowed email addresses for your Dropbox for business account

"""
import json
import requests

import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def test_unknown_dropbox_users():
    """
    Asserts that all emaill addresses associated with your Dropbox for business account are in the
    list DROPBOX_ALLOWED_EMAILS (Case insensitive)
    """

    headers = {'Authorization': 'Bearer {0}'.format(CONFIG.DROPBOX_APP_ACCESS_TOKEN), 'Content-Type': 'application/json'}
    response = requests.post('https://api.dropbox.com/1/team/members/list', headers=headers, data=json.dumps({'limit': 1000}))

    all_dropbox_emails = [member['profile']['email'] for member in response.json()['members']]
    print all_dropbox_emails
    print type(all_dropbox_emails)
    for dropbox_email in all_dropbox_emails:
        yield email_is_in_ldap, dropbox_email

def email_is_in_ldap(email_to_test):
    """
    Asserts that the email provided is present in the list of
    DROPBOX_ALLOWED_EMAILS. Case insensitive.
    """
    valid_emails = [email.lower() for email in CONFIG.DROPBOX_ALLOWED_EMAILS]
    assert email_to_test.lower() in valid_emails
