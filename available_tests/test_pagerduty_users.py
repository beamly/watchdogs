#!/usr/bin/env python
"""
Tests that all Pagerduty users are valid

Required config.py variables:

PAGERDUTY_API_KEY           String    The pagerduty API key used to query your users

PAGERDUTY_ACCOUNT_NAME      String    The pagerduty account name used to call the API at
                                      https://{PAGERDUTY_ACCOUNT_NAME}.pagerduty.com/api

PAGERDUTY_VALID_EMAILS      List      A list of valid email addresses (Case insensitive)
"""

import os
import imp
import pytest
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def _all_pagerduty_users():
    headers = {'Authorization': 'Token token={0}'.format(CONFIG.PAGERDUTY_API_KEY)}
    response = requests.get('https://{0}.pagerduty.com/api/v1/users'.format(CONFIG.PAGERDUTY_ACCOUNT_NAME), headers=headers)

    return [user['email'] for user in response.json()['users']]

@pytest.mark.parametrize("email_address", _all_pagerduty_users())
def test_unknown_pagerduty_user(email_address):
    """
    Connects to pager duty using the supplied account name
    (PAGERDUTY_ACCOUNT_NAME) and API key (PAGERDUTY_API_KEY), queries all users,
    and checks that there aren't any users with an email address not in the
    PAGERDUTY_VALID_EMAILS list
    """
    assert email_address in CONFIG.PAGERDUTY_VALID_EMAILS
