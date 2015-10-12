#!/usr/bin/env python
"""
Iterates over every respository in a set of github organisations and
verifies that there are no public repositories

Required config.py variables:

GITHUB_PRIVATE_ORGANISATIONS   List[String]   A list of github organisations whose
                                              repositories you would like to audit
                                              hooks for

GITHUB_API_TOKEN                String        A github API token that has access
                                              to all the organisations in
                                              GITHUB_PRIVATE_ORGANISATIONS

Examples:
GITHUB_PRIVATE_ORGANISATIONS = ['myorg1', 'myorg2']
GITHUB_API_TOKEN = '123456789ABCDEFG'

"""
import requests

import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])


def get_all_github_repos(organisation):
    """
    Given an organisation returns list of dictionaries, one per repo. For detail
    on response format see:

    https://developer.github.com/v3/repos/#list-your-repositories

    :param organisation: (str) The github organisation for which to return a list
                               of all repositories for
    :returns:                  A list of dictionaries as defined by
                               https://developer.github.com/v3/repos/#list-your-repositories
    """
    all_github_repos = []
    uri = 'https://api.github.com/orgs/{0}/repos'.format(organisation)
    response = requests.get(uri, auth=(CONFIG.GITHUB_API_TOKEN, 'x-oauth-basic'))
    all_github_repos += (response.json())

    page = 2
    while len(response.json()) > 0:
        response = requests.get(uri + "?page={0}".format(page), auth=(CONFIG.GITHUB_API_TOKEN, 'x-oauth-basic'))
        all_github_repos += response.json()
        page += 1

    return all_github_repos


def test_all_repos():
    for organisation in CONFIG.GITHUB_PRIVATE_ORGANISATIONS:
        repos = get_all_github_repos(organisation)
        for repo in repos:
            yield repo_is_private, repo

def repo_is_private(repo):
    assert repo['private'] == True