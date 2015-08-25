#!/usr/bin/env python

import imp
import os
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])


def test_facebook_app_users():
    # https://developers.facebook.com/docs/facebook-login/access-tokens#apptokens
    url1 = 'https://graph.facebook.com/oauth/access_token' \
           '?client_id={0}' \
           '&client_secret={1}' \
           '&grant_type=client_credentials'.format(
        CONFIG.FACEBOOK_APP_ID, CONFIG.FACEBOOK_APP_SECRET)
    rsp1 = requests.get(url1)
    rsp1.raise_for_status()
    access_token = rsp1.text.split("=")[1]

    # https://developers.facebook.com/docs/graph-api/reference/v2.4/app/roles
    url2 = 'https://graph.facebook.com/v2.4/{0}/roles' \
           '?access_token={1}' \
           '&limit=1000'.format(CONFIG.FACEBOOK_APP_ID, access_token)
    rsp2 = requests.get(url2)
    rsp2.raise_for_status()
    for json in rsp2.json()['data']:
        yield facebook_user_is_in_ldap, json


def facebook_user_is_in_ldap(json):
    # N.B. User IDs associated to Apps are app-scoped, see
    # https://developers.facebook.com/docs/apps/upgrading#upgrading_v2_0_user_ids
    assert json['user'] in CONFIG.FACEBOOK_IDS, \
        'Unknown user: [{0}], role: [{1}]'.format(json['user'], json['role'])
