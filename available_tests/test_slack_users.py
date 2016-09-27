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

                                          { 'email.+@domain.com':
                                            {
                                              'description': 'DESCRIPTION',
                                              'allowed_until': 'dd/mm/yyyy'
                                            }
                                          }

                                        The key is a regaulr expression of a match

                                        The value is a dictionary that supports the following parameters:

                                        allowed_until: A date for which this exception is valid

                                        single_channel: Ensure that the 'is_ultra_restricted' attribute
                                        returned by the Slack API is True (i.e. that they're a single
                                        channel only guest)

                                        prefix: Assert that the users username of the begins with this prefix

"""

import re
import os
import imp
import time
import requests
import pytest

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def _all_active_slack_users(auth_token=CONFIG.SLACK_AUTH_TOKEN):
    """
    Returns a list of active slack users, each represented as a dictionary.
    (See https://api.slack.com/methods/users.list for fields)
    """
    uri = 'https://slack.com/api/users.list?token=' + auth_token
    response = requests.get(uri)
    all_slack_users = response.json()
    all_active_slack_users = [(member['profile']['email'].lower(), member) for member in all_slack_users['members'] if not member['deleted'] and member['id'] != 'USLACKBOT' and not member['is_bot']]
    return all_active_slack_users

@pytest.mark.parametrize("email,slack_user", _all_active_slack_users())
def test_slack_user(email,slack_user):
    """
    Asserts that an email address is either in SLACK_VALID_EMAILS or is a key in
    SLACK_EXCEPTIONS and that the 'allowed_until' field is after todays date
    """
    exception_match = None

    # Either it's an exception or
    for EXCEPTION in CONFIG.SLACK_EXCEPTIONS:
        if re.match(EXCEPTION, email):
            exception_match = CONFIG.SLACK_EXCEPTIONS[EXCEPTION]

    if exception_match is not None:
        if 'allowed_until' in exception_match:
            valid_until = time.strptime(exception_match['allowed_until'], "%d/%m/%Y")
            assert time.gmtime() <= valid_until

        if 'single_channel' in exception_match:
            assert slack_user['is_ultra_restricted']

        if 'prefix' in exception_match:
            assert slack_user['name'].startswith(exception_match['prefix'])

    else:
        assert email in CONFIG.SLACK_VALID_EMAILS
        assert slack_user['has_2fa']