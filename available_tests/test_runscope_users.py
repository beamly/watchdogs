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

import os
import imp
import pytest
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def _all_active_runscope_users():
    """
    Returns a list of members for a given runscope team, each represented as a dictionary.
    (See https://www.runscope.com/docs/api/resources/teams for fields)
    """

    uri = "https://api.runscope.com/teams/{0}/people".format(CONFIG.RUNSCOPE_TEAM_ID)
    response = requests.get(uri, headers={'Authorization': 'bearer {0}'.format(CONFIG.RUNSCOPE_ACCESS_TOKEN)})
    return [user['email'] for user in response.json()['data']]

@pytest.mark.parametrize("email", _all_active_runscope_users())
def test_runscope_user(email):
    """
    Assert that all email addresses of all users in Runscope are known
    """
    assert email in CONFIG.RUNSCOPE_VALID_EMAILS
