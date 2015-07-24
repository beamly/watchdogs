#!/usr/bin/env python
"""
Verifies that all github accounts in a list of github organisations are known and
that all accounts have two factor authentication enabled.

Required config.py variables:

GITHUB_ORGANISATIONS        List[String]    A list of github organisations whose
                                            repositories you would like to audit
                                            hooks for

GITHUB_API_TOKEN            String          A github API token that has access
                                            to all the organisations in
                                            GITHUB_ORGANISATIONS

GITHUB_VALID_USERS          dict            A dictionary with keys representing
                                            githubids mapping to values of the
                                            real name of that person.
"""

import requests

import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def github_user_is_valid(githubid):
    """
    Assert that the githubid is valid
    :param githubid:   str  The githubid that you want to assert is a known id
    """
    assert githubid in CONFIG.GITHUB_VALID_USERS.keys()

def github_user_has_2fa_enabled(githubid):
    """
    Assert that a githubid is false. This is a dummy method to allow us to present
    each account that has 2FAS disabled as a seperate failure.
    :param githubid:  str   The githubid of an account that has 2FA disabled
    """
    assert githubid == None

def get_all_organisation_members(organisation, two_factor_auth_disabled_only=False):
    """
    Return all users for a given github organisation.
    See: https://developer.github.com/v3/orgs/members/ for details.
    :param organisation:                  str     The github organisation that
                                                  you want to retrieve all
                                                  members for
    :param two_factor_auth_disabled_only: bool    Return only members with 2FA
                                                  disabled.
    :returns:                             list    A list of dictionary objects,
                                                  one per user.
                                                  See https://developer.github.com/v3/orgs/members/
                                                  for details.

    """
    uri = 'https://api.github.com/orgs/{0}/members?&per_page=1000'.format(organisation)
    if two_factor_auth_disabled_only:
        uri += "&filter=2fa_disabled"

    response = requests.get(uri, auth=(CONFIG.GITHUB_API_TOKEN, 'x-oauth-basic'))
    all_github_users = response.json()
    return all_github_users

def test_all_github_users():
    """
    Iterates over a list of github organisations as specified in
    CONFIG.GITHUB_ORGANISATIONS and ensures that every member is known and has
    two factor authentication enabled.
    """
    # Check that all users are known
    for organisation in CONFIG.GITHUB_ORGANISATIONS:
        github_users = get_all_organisation_members(organisation=organisation, two_factor_auth_disabled_only=False)
        for github_user in github_users:
            yield github_user_is_valid, github_user['login']

        github_users_2fa_disabled = get_all_organisation_members(organisation=organisation, two_factor_auth_disabled_only=True)
        github_ids_2fa_disabled = [user['login'] for user in github_users_2fa_disabled]

        # Assert false for every user in this list. We could just assert that
        # the list is empty but we want each entry to register as a seperate
        # failure. We have to do it this way as the github API doesn't return
        # a field indicating whether a member has 2FA enabled, we can only query
        # for all users with 2FA disabled.
        for githubid in github_ids_2fa_disabled:
            yield github_user_has_2fa_enabled, githubid


