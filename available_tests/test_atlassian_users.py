#!/usr/bin/env python
"""
Tests all cloud hosted Atlassian applications (Jira, Confluence) to ensure that
only valid users have a licence assigned, and that all active users have an
email in ATLASSIAN_VALID_EMAILS

ATLASSIAN_HOSTNAME        String    The hostname used to connect to the Atlassian API

ATLASSIAN_USERNAME        String    The user used to authenticate against API calls

ATLASSIAN_PASSWORD        String    The password used to authenticate against API calls

ATLASSIAN_APPLICATIONS    Dict      A dictionary of all the Atlassian products you
                                    wish to check the licences for

ATLASSIAN_VALID_EMAILS    List      A list of email addresses for active users

ATLASSIAN_EXCEPTIONS      dict      A dictionary of email address: Exceptions
                                    That can be used to define system accounts
                                    or temporary exceptions. Format:

                                    { 'email':
                                      {
                                        'description': 'DESCRIPTION',
                                        'allowed_until': 'dd/mm/yyyy'
                                      }
                                    }
Examples:

ATLASSIAN_USERNAME ='readonlybot'
ATLASSIAN_PASSWORD = 'testpassword'

ATLASSIAN_APPLICATIONS = {'JIRA': '52b5fcb8-5e0a-3f54-9c7d-827342368abbcda',
                          'CONFLUENCE': '257d6142-ccd6-31d6-9f68-7346237864abcaa'}

ATLASSIAN_VALID_EMAILS = [user['mail'][0].lower() for user in LDAP_USERS if 'mail' in user]
ATLASSIAN_EXCEPTIONS = {
    'partner@external.com': {
      'description': 'External Partner - Read only access to EXTERNAL workspace',
      'allowed_until': '1/1/2099'
    }
  }

"""

import os
import imp
import time
import pytest
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def _all_active_atlassian_users():
    """
    Asserts that all active users have an email address in ATLASSIAN_VALID_EMAILS
    ATLASSIAN_EXCEPTIONS (and that the current date is before allowed_until)
    """

    url = "https://%(hostname)s/admin/rest/um/1/user/search?max-results=1000" % {'hostname': CONFIG.ATLASSIAN_HOSTNAME}
    response = requests.get(url, auth=(CONFIG.ATLASSIAN_USERNAME, CONFIG.ATLASSIAN_PASSWORD))
    all_users = response.json()
    return [user['email'].lower() for user in all_users if user['active']]

@pytest.mark.parametrize("email", _all_active_atlassian_users())
def test_user(email):
    """
    Asserts that every user with a licence is either in ATLASSIAN_VALID_EMAILS or
    ATLASSIAN_EXCEPTIONS (and that the current date is before allowed_until)
    """
    if email in CONFIG.ATLASSIAN_EXCEPTIONS:
        valid_until = time.strptime(CONFIG.ATLASSIAN_EXCEPTIONS[email]['allowed_until'], "%d/%m/%Y")
        assert time.gmtime() <= valid_until
    else:
        assert email in CONFIG.ATLASSIAN_VALID_EMAILS



