#!/usr/bin/env python
"""
Checks that all Slack users for a given account are either registered with a
known (Organisation) email address and have two factor authentication enabled,
or are listed as an exceptions (Useful for external/single channel/restricted
users outside your organisation). Exceptions/External users are not required
to have 2FA enabled.

Required config.py variables:

SLACK_AUTH_TOKEN        String          Your organisations Slack API token

SLACK_VALID_EMAILS      List[String]    A list of valid email addresses for your organisation

SLACK_EXCEPTIONS        dict            A dictionary of email address: Exceptions
                                        That can be used to define external
                                        (Restricted/Single channel) users. Format:

                                          { 'EMAIL@DOMAIN.COM':
                                            {
                                              'description': 'DESCRIPTION',
                                              'allowed_until': 'dd/mm/yyyy'
                                            }
                                          }

"""

import time
import requests

import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def get_all_active_slack_users(auth_token):
    """
    Returns a list of active slack users, each represented as a dictionary.
    (See https://api.slack.com/methods/users.list for fields)
    """

    uri = 'https://slack.com/api/users.list?token=' + auth_token
    response = requests.get(uri)
    all_slack_users = response.json()
    all_active_slack_users = [member for member in all_slack_users['members'] if not member['deleted']]
    return all_active_slack_users

def test_unknown_slack_users():
    """
    Iterates through all active Slack users and asserts that they are either
    registered with a valid email (SLACK_VALID_EMAILS) or is in SLACK_EXCEPTIONS
    and the current date is before the 'allowed_until' field
    """

    all_active_slack_users = get_all_active_slack_users(auth_token=CONFIG.SLACK_AUTH_TOKEN)

    for user in all_active_slack_users:
        if user['id'] != 'USLACKBOT' and not user['is_bot']:
            yield email_is_valid, user['profile']['email'].lower()
            if user['profile']['email'] not in CONFIG.SLACK_EXCEPTIONS:
                yield two_factor_enabled, user['real_name'], user['has_2fa']

def email_is_valid(slack_account_email):
    """
    Asserts that an email address is either in SLACK_VALID_EMAILS or is a key in
    SLACK_EXCEPTIONS and that the 'allowed_until' field is after todays date
    """
    if slack_account_email in CONFIG.SLACK_EXCEPTIONS:
        # We have eception for this address, check it's still valid
        valid_until = time.strptime(CONFIG.SLACK_EXCEPTIONS[slack_account_email]['allowed_until'], "%d/%m/%Y")
        assert time.gmtime() <= valid_until
    else:
        assert slack_account_email in CONFIG.SLACK_VALID_EMAILS

def two_factor_enabled(realname, two_factor_auth_enabled):
    """
    Asserts that two factor authentication is enabled for this user
    """
    print realname
    assert two_factor_auth_enabled
