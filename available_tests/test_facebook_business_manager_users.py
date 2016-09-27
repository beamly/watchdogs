#!/usr/bin/env python

import imp
import os
import pytest
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])


def _get_all_facebook_business_manager_users():
    # Validates members of a Facebook business
    #
    # https://business.facebook.com/settings/people
    #
    # * in order to interact with the Facebook API you need an access token
    # * which you can get as a Facebook User
    # * but that requires an interactive login process
    # * and it only lasts a few hours
    # * so we exchange that short-lived for a long-lived one
    #   (lasts 60 days, and sadly requires refreshes every 60 days...)
    # * but to do that a Facebook App is required (for its id and secret)
    # * so..
    #
    # Steps:
    # 1. Identify what (or create a) Facebook user to use
    #
    # 2. Identify what (or create a) Facebook app to use
    #
    # 3. Make sure that the user is added to the app and to the business acct
    #
    # 4. Use Facebook's guide to create a short-lived access token (Make sure you add 'ads_management' to 'scope' for login)
    #    https://developers.facebook.com/docs/marketing-api/authentication
    #
    # 5. Use that short-lived access token to get a long-lived one:
    #     curl -G \
    #       -d 'grant_type=fb_exchange_token' \
    #       -d 'client_id=APP_ID' \
    #       -d 'client_secret=APP_SECRET' \
    #       -d 'fb_exchange_token=SHORT_LIVED_ACCESS_TOKEN' \
    #       https://graph.facebook.com/oauth/access_token
    # 6. Store that access token as FACEBOOK_ACCESS_TOKEN in config.py

    # https://developers.facebook.com/docs/marketing-api/businessmanager/v2.4#users
    all_business_manager_users = []
    url = 'https://graph.facebook.com/v2.4/{0}/userpermissions' \
          '?access_token={1}' \
          '&limit=1000'.format(
              CONFIG.FACEBOOK_BUSINESS_ID, CONFIG.FACEBOOK_ACCESS_TOKEN)
    rsp = requests.get(url)
    rsp.raise_for_status()
    for json in rsp.json()['data']:
        print json
        if ('is_system_user' not in json) or (not json['is_system_user']):
            all_business_manager_users.append((json['business_persona']['name'],json['email']))
    return all_business_manager_users


@pytest.mark.parametrize("facebook_name,facebook_email,", _get_all_facebook_business_manager_users())
def test_facebook_user_is_in_ldap(facebook_name,facebook_email):

    #is_known_facebook_id = facebook_user_id in CONFIG.FACEBOOK_IDS
    is_known_email_address = facebook_email in CONFIG.FACEBOOK_KNOWN_EMAILS

    assert is_known_email_address or facebook_name.upper() in CONFIG.FACEBOOK_NAMES
