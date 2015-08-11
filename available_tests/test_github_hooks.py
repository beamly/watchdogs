#!/usr/bin/env python
"""
Iterates over every respository in a set of github organisations and
verifies that there are no unknown hooks associated with any repository (Either
email or webhooks)

Required config.py variables:

GITHUB_ORGANISATIONS        List[String]    A list of github organisations whose
                                            repositories you would like to audit
                                            hooks for

GITHUB_API_TOKEN            String          A github API token that has access
                                            to all the organisations in
                                            GITHUB_ORGANISATIONS


GITHUB_ALLOWED_HOOKS   List[String]         A list of dictionary objects that can
                                            either be whole or partial matches to
                                            the json returned by the github list
                                            hooks API:

                                            https://developer.github.com/v3/repos/hooks/#list-hooks

                                            Allows you to be as explicit as you like
                                            when matching hooks.

Examples:
GITHUB_ORGANISATIONS = ['myorg1', 'myorg2']
GITHUB_API_TOKEN = '123456789ABCDEFG'
GITHUB_ALLOWED_HOOKS = [{'config' : {'domain': 'notify.travis-ci.org', 'user': 'myuser'}},
                        {'config' : {'url': 'https://beamly.slack.com/services/hooks/github?token=123456789ABCDEFG'}},
                        {'config' : {'url': 'http://hubot.beamly.com/hubot/gh-pull-requests'}}
                       ] + \
                       [{'name': 'email',
                         'config': {'address': email}
                        }
                        for email in LDAP_EMAILS
                       ]
]
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

def get_hooks_for_repo(organisation, reponame):
    """
    Returns all hooks for a given repository in a given organisation. For details
    on respose format see:

    https://developer.github.com/v3/repos/hooks/#list-hooks

    :param organisation:  (str)   The github organisation that owns the repository
                                  that you are requesting the hooks for
    :param reponame:      (str)   The name of the repository that you'd like the hooks for
    :returns:                     A list of dictionaries (one per hook) as defined by
                                  https://developer.github.com/v3/repos/hooks/#list-hooks
    """

    uri = 'https://api.github.com/repos/{0}/{1}/hooks'.format(organisation, reponame)
    response = requests.get(uri, auth=(CONFIG.GITHUB_API_TOKEN, 'x-oauth-basic'))
    return response.json()

def test_unknown_hooks():
    """
    Tests that all repos for all the organisations specified in CONFIG.GITHUB_ORGANISATIONS
    have no unknown web or email hooks
    """
    for organisation in CONFIG.GITHUB_ORGANISATIONS:
        for repo in get_all_github_repos(organisation):
            yield github_repo_is_clean, organisation, repo['name']

def github_repo_is_clean(organisation, reponame):
    """
    Returns True if a repository either has 0 hooks associated, or all hooks for
    are known (Either email hooks associated with an email address provided in
    CONFIG.GITHUB_VALID_EMAILS or is a webhook with a URL as specified in
    CONFIG.GITHUB_HOOKS_ALLOWED_URLS.

    :param organisation:  (str)   The github organisation that owns the
                                  repository you wish to audit the hooks of
    :param reponame:      (str)   The name of the repository that you'd like to
                                  it the hooks for
    :returns:             (bool)  True if the repository has 0 hooks or all
                                  hooks are known, False if there are unknown
                                  hooks for this repository
    """

    hooks = get_hooks_for_repo(organisation, reponame)
    unknown_hooks = [hook for hook in hooks if not allowed_hook(hook)]
    assert len(unknown_hooks) == 0

def dictionary_match(dict1, dict2):
    """
    Recursively tests whether dict1 is a "loose" subset of dict2, where loose means 
    string values in dict1 are "in" the opposite value in dict2, meaning these two dictionaries
    are considered "matched":

    dict1: 

        {'config' : {'url': 'https://tbonetv.jira.com/rest/bitbucket/1.0/repository'}}
    
    dict2: 

    { 'active': True,
      'config': {   
          'url': 
          'https://tbonetv.jira.com/rest/bitbucket/1.0/repository/1234/sync'
        },
      'created_at': u'2015-08-10T15:10:24Z',
      'events': ['push'],
      'id': 123456,
      'last_response': { 
        'code': 200, 
        'message': u'OK', 
        'status': 
        'active'
      },
      'name': u'web',
      'ping_url': 'https://api.github.com/repos/zeebox/MyRepo/hooks/123456/pings',
      'test_url': 'https://api.github.com/repos/zeebox/MyRepo/hooks/123456/test',
      'updated_at': '2015-08-10T15:10:24Z',
      'url': 'https://api.github.com/repos/zeebox/MyRepo/hooks/123456'}


    Shamelessly copied from:
    http://stackoverflow.com/questions/9323749/python-check-if-one-dictionary-is-a-subset-of-another-larger-dictionary
    """
    try:
        for pkey, pvalue in dict1.iteritems():
            if type(pvalue) is dict:
                result = dictionary_match(pvalue, dict2[pkey])
            elif type(pvalue) is str:
                assert pvalue in dict2[pkey]
                result = True
            else:
                assert dict2[pkey] == pvalue
                result = True
    except (AssertionError, KeyError):
        result = False
    return result

def allowed_hook(hook):
    """
    Asserts that a given hook matches all of the data in a entry in
    CONFIG.GITHUB_ALLOWED_HOOKS

    :param hook:    (dict)  A dictionary object as returned by the github webhooks
                            API (https://developer.github.com/v3/repos/hooks/#list-hooks)
    :returns:       (bool)  True is this is an allowed hook, False if not
    """

    # Check if it's an allowed exception
    matches = [dictionary_match(hook_exception, hook) for hook_exception in CONFIG.GITHUB_ALLOWED_HOOKS]
    return True in matches
