#!/usr/bin/env python

import imp
import os
import pytest
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def get_name_for_token(user_id, access_token, app_name):
    url = "https://graph.facebook.com/v2.4/{0}?access_token={1}".format(user_id, access_token)
    rsp = requests.get(url)
    rsp.raise_for_status()
    json = rsp.json()
    return json['name']

def _get_all_facebook_app_users():
    facebook_users = []
    for app in CONFIG.FACEBOOK_APPS:
        app_name = app["name"]
        app_id = app["id"]
        app_secret = app["secret"]

        # https://developers.facebook.com/docs/facebook-login/access-tokens#apptokens
        url1 = 'https://graph.facebook.com/oauth/access_token' \
               '?client_id={0}' \
               '&client_secret={1}' \
               '&grant_type=client_credentials'.format(app_id, app_secret)
        rsp1 = requests.get(url1)
        rsp1.raise_for_status()
        access_token = rsp1.text.split("=")[1]

        # https://developers.facebook.com/docs/graph-api/reference/v2.4/app/roles
        url2 = 'https://graph.facebook.com/v2.4/{0}/roles' \
               '?access_token={1}' \
               '&limit=1000'.format(app_id, access_token)
        rsp2 = requests.get(url2)
        rsp2.raise_for_status()
        for json in rsp2.json()['data']:
            facebook_users.append((get_name_for_token(json["user"],access_token,app_name),json["user"], access_token, app_name))

    return facebook_users

@pytest.mark.parametrize("facebook_name, facebook_user_id, access_token, app_name", _get_all_facebook_app_users())
def test_facebook_user_is_in_ldap(facebook_name, facebook_user_id, access_token, app_name):
    # N.B. User IDs associated to Apps are app-scoped, see
    # https://developers.facebook.com/docs/apps/upgrading#upgrading_v2_0_user_ids
    assert (facebook_user_id in CONFIG.FACEBOOK_IDS) or facebook_name.upper() in CONFIG.FACEBOOK_NAMES

