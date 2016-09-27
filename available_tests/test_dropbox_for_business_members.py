#!/usr/bin/env python
"""
Checks all members of a dropbox for business team are known

Required config.py variables:

DROPBOX_APP_ACCESS_TOKEN        String      The API key used to access your dropbox for
											business account (Requires permission type 'Team auditing')

DROPBOX_ALLOWED_EMAILS      List[String]    A list of all allowed email addresses for your Dropbox for business account

"""
import os
import imp
import json
import pytest
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def _all_dropbox_emails():
    headers = {'Authorization': 'Bearer {0}'.format(CONFIG.DROPBOX_APP_ACCESS_TOKEN), 'Content-Type': 'application/json'}
    response = requests.post('https://api.dropbox.com/1/team/members/list', headers=headers, data=json.dumps({'limit': 1000}))
    return [member['profile']['email'] for member in response.json()['members']]

@pytest.mark.parametrize("email", _all_dropbox_emails())
def test_dropbox_user(email):
    """
    Asserts that all emaill addresses associated with your Dropbox for business account are in the
    list DROPBOX_ALLOWED_EMAILS (Case insensitive)
    """
    assert email.lower() in CONFIG.DROPBOX_ALLOWED_EMAILS
