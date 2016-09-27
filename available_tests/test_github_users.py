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



import os
import imp
import pytest
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])


def _all_organisation_members(organisation, two_factor_auth_disabled_only=False):
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

def _all_github_users():
    """
    Iterates over a list of github organisations as specified in
    CONFIG.GITHUB_ORGANISATIONS and ensures that every member is known and has
    two factor authentication enabled.
    """

    all_github_users = []
    for organisation in CONFIG.GITHUB_ORGANISATIONS:
        github_users = _all_organisation_members(organisation=organisation, two_factor_auth_disabled_only=False)
        for github_user in github_users:
            all_github_users.append((github_user['login'],True))

        github_users_2fa_disabled = _all_organisation_members(organisation=organisation, two_factor_auth_disabled_only=True)

        for github_user in github_users_2fa_disabled:
            all_github_users.append((github_user['login'],False))

    return all_github_users

@pytest.mark.parametrize("githubid,two_factor_enabled", _all_github_users())
def test_github_user_is_valid(githubid,two_factor_enabled):
    """
    Assert that the githubid is valid
    :param githubid:   str  The githubid that you want to assert is a known id
    """
    assert githubid in CONFIG.GITHUB_VALID_USERS
    assert two_factor_enabled