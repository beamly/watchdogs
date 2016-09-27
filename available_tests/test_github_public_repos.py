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

import os
import imp
import pytest
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def _get_all_github_repos():

    all_github_repos = []
    for organisation in CONFIG.GITHUB_PRIVATE_ORGANISATIONS:
      uri = 'https://api.github.com/orgs/{0}/repos'.format(organisation)

      page = 1
      more_data = True
      while more_data:
          response = requests.get(uri + "?page={0}".format(page), auth=(CONFIG.GITHUB_API_TOKEN, 'x-oauth-basic')).json()
          #print response
          if len(response) > 0:
            for repo in response:
              all_github_repos.append((repo['name'],repo))
            page += 1
          else:
            more_data = False

    return all_github_repos

@pytest.mark.parametrize("repo_name,repo", _get_all_github_repos())
def test_repo(repo_name, repo):
      assert repo['private']
