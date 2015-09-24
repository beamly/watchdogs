#!/usr/bin/env python

import imp
import os
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])


def test_facebook_app_users():
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
            facebook_users.append({
                "user_id": json["user"],
                "access_token": access_token,
                "app_name": app_name,
            })

    for user in facebook_users:
        yield facebook_user_is_in_ldap, \
            user["user_id"], user["access_token"], user["app_name"]


def facebook_user_is_in_ldap(user_id, access_token, app_name):
    # N.B. User IDs associated to Apps are app-scoped, see
    # https://developers.facebook.com/docs/apps/upgrading#upgrading_v2_0_user_ids
    assert user_id in CONFIG.FACEBOOK_IDS, error_msg(
        user_id, access_token, app_name)


def error_msg(user_id, access_token, app_name):
    url = "https://graph.facebook.com/v2.4/{0}?access_token={1}".format(
        user_id, access_token)
    rsp = requests.get(url)
    rsp.raise_for_status()
    json = rsp.json()
    return 'Unknown user on [{0}]: [{1}]: [{2}]'.format(
        app_name, user_id, json['name'])
