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
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

import requests

def test_unknown_pd_users():
    """
    Connects to pager duty using the supplied account name
    (PAGERDUTY_ACCOUNT_NAME) and API key (PAGERDUTY_API_KEY), queries all users,
    and checks that there aren't any users with an email address not in the
    PAGERDUTY_VALID_EMAILS list
    """

    headers = {'Authorization': 'Token token={0}'.format(CONFIG.PAGERDUTY_API_KEY)}
    response = requests.get('https://{0}.pagerduty.com/api/v1/users'.format(CONFIG.PAGERDUTY_ACCOUNT_NAME), headers=headers)

    all_registered_pd_emails = [user['email'] for user in response.json()['users']]

    for email in all_registered_pd_emails:
        yield email_is_in_ldap, email

def email_is_in_ldap(email):
    """
    Asserts that the email provided is present in the list of
    PAGERDUTY_VALID_EMAILS. Case insensitive.
    """
    valid_emails = [email.lower() for email in CONFIG.PAGERDUTY_VALID_EMAILS]
    assert email.lower() in valid_emails
