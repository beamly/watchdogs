#!/usr/bin/env python
"""
Tests the users in a Runscope team

Required config.py variables:

RUNSCOPE_TEAM_ID           String       The UUID for the team you with to verify.

                                        To find:

                                        1. Login to runscope
                                        2. Click the "Profile" icon (top right corner)
                                        3. Select "People" under the team you're interested in from the menu on the left
                                        4. Extract the team UUID from the URL, e.g:

                                        https://www.runscope.com/teams/84fa4a26-c823-4f7c-ab12-1691762cb7fa/people
                                                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                                                  RUNSCOPE_TEAM_ID

RUNSCOPE_ACCESS_TOKEN       String      Your runscope access token. To generate:

                                        1. Login to runscope
                                        2. Click the "Profile" icon (top right corner)
                                        3. Select "Applications" from the menu on the right
                                        4. Click "Create application"

                                           Name: Security Watchdogs
                                           Website URL: https://github.com/beamly/watchdogs
                                           Callback URL: https://github.com/beamly/watchdogs

                                        5. The access token is shown at the bottom of the page,
                                           titled "Personel Access token".

RUNSCOPE_VALID_EMAILS       List         A list of email addresses for valid Runscope users

"""

import requests

import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def get_all_runscope_team_members(access_token, team_id):
    """
    Returns a list of members for a given runscope team, each represented as a dictionary.
    (See https://www.runscope.com/docs/api/resources/teams for fields)
    """

    uri = "https://api.runscope.com/teams/{0}/people".format(team_id)
    response = requests.get(uri, headers={'Authorization': 'bearer {0}'.format(access_token)})
    all_runscope_users = response.json()['data']
    return all_runscope_users

def test_unknown_runscope_users():
    """
    Assert that all email addresses of all users in Runscope are known
    """
    all_runscope_users = get_all_runscope_team_members(access_token=CONFIG.RUNSCOPE_ACCESS_TOKEN, team_id=CONFIG.RUNSCOPE_TEAM_ID)
    for user in all_runscope_users:
        yield email_is_in_valid, user['email'].lower()

def email_is_in_valid(runscope_email_address):
    """
    Assert that the email address of a single Runscope user is valid/active
    """
    valid_emails = [email.lower() for email in CONFIG.RUNSCOPE_VALID_EMAILS]
    assert runscope_email_address in valid_emails
