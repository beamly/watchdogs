#!/usr/bin/env python
"""
Verifies that all AWS IAM users:

- Are known
- Users with a password set
    - Have two factor authentication enabled
    - Have logged in to the console in the last AWS_IAM_USER_LAST_LOGGED_IN_DAYS days
- Every account has only a single AWS access key
- That all access keys have been used within the last AWS_IAM_KEY_LAST_USED_DAYS

This test makes no effort to validate the permissions for each user, as it's
mainly intended to ensure AWS IAM accounts are removed when employees leave
the company (At Beamly we name IAM users with a users primary email address)

This script uses boto to authenticate with AWS. For details on how to configure
boto authentication see:

http://boto.readthedocs.org/en/latest/boto_config_tut.html

This script requires permissions to Get*, List* all IAM properties: Add the
following IAM polocy document to the relevant IAM Role/User:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1432131248000",
            "Effect": "Allow",
            "Action": [
                "iam:Get*",
                "iam:List*",
                "iam:GenerateCredentialReport"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}

Required config.py variables:

AWS_IAM_VALID_USERNAMES     List[String]    A list of valid AWS account names.

AWS_IAM_KEY_LAST_USED_DAYS  int             The number of days in which a key
                                            must have been used last in order to
                                            be considered 'active'.

AWS_IAM_USER_LAST_LOGGED_IN_DAYS            The number of days since a users
                                            last login (If they have a password
                                            set) to be considered active.

AWS_IAM_VALID_VAULT_USERS                   OPTIONAL. Set to a list of strings to
                                            configure support for Hashicorp vault,
                                            which has is used to dynamically generate
                                            AWS IAM users for a limited period of
                                            time and automatically deletes them.

AWS_IAM_VAULT_USER_AUTH_MECHANISM           Only required if AWS_IAM_VALID_VAULT_USERS is set. Vault creates
                                            users using the pattern: vault-{AUTH_TYPE}-{USERNAME}-{POLICY}-{EXPIRATION}
                                            Defaults to 'ldap'

AWS_IAM_VAULT_USER_LEASE_TIME               Only required if AWS_IAM_VALID_VAULT_USERS is set. The number of
                                            seconds that you've configured vault to issue AWS token leases for.

"""
import time
import base64
from datetime import datetime
from dateutil.parser import parse
from boto.exception import BotoServerError
from boto.iam.connection import IAMConnection

CFN = IAMConnection()

import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])


def get_credential_report_dict():
    """
    Returns the IAM credential report as a python dictionary using the IAM
    username as a key.
    """
    CFN.generate_credential_report()
    time.sleep(5)
    report = CFN.get_credential_report()
    report = report['get_credential_report_response']['get_credential_report_result']['content']
    report = base64.b64decode(report)
    report = report.split('\n')

    credential_report = {}

    field_names = report[0].split(',')

    for entry in report[1:]:
        fields = entry.split(',')
        credential_report[fields[0]] = dict(zip(field_names, fields))

    return credential_report

CREDENTIAL_REPORT = get_credential_report_dict()

def get_days_since_key_last_login(username):
    """
    Returns the number of days since the username provided logged in
    :param username: string The name of the user you want to check
    :returns: int   The number of days since the user provided logged in
    """
    try:
        last_used_date = CREDENTIAL_REPORT[username]['password_last_used']
        datetime_now = datetime.now()
        datetime_last_used = parse(last_used_date)
        datetime_last_used = datetime_last_used.replace(tzinfo=None)
        diff = datetime_now - datetime_last_used
        return diff.days
    except ValueError:
        return None

def get_days_since_key_last_use(aws_access_key):
    """
    Returns the number of days since the AWS Access Key provided was last used
    :param aws_access_key: string The access key that you want to check
    :returns: int   The number of days since the uaccess key provided was used,
                    or None if it was never used
    """
    response = CFN.get_response(action='GetAccessKeyLastUsed', params={'AccessKeyId':aws_access_key})

    try:
        last_used_date = response['get_access_key_last_used_response']['get_access_key_last_used_result']['access_key_last_used']['last_used_date']
        datetime_now = datetime.now()
        datetime_last_used = parse(last_used_date)
        datetime_last_used = datetime_last_used.replace(tzinfo=None)
        diff = datetime_now - datetime_last_used
        return diff.days
    except KeyError:
        return None

def is_vault_enabled():
    try:
        a = CONFIG.AWS_IAM_VALID_VAULT_USERS
        b = CONFIG.AWS_IAM_VAULT_USER_AUTH_MECHANISM
        c = CONFIG.AWS_IAM_VAULT_USER_LEASE_TIME
        return True
    except AttributeError:
        return False

def test_all_iam_users():
    """
    Ensure that all IAM users:

    - Are known
    - Users with a password set
        - Have two factor authentication enabled
        - Have logged in to the console in the last AWS_IAM_USER_LAST_LOGGED_IN_DAYS days
    - Every account has only a single AWS access key
    - That all access keys have been used within the last AWS_IAM_KEY_LAST_USED_DAYS
    """
    iam_users = CFN.get_all_users()

    for user in iam_users['list_users_response']['list_users_result']['users']:
        if is_vault_enabled():
            yield iam_user_is_valid, user, CONFIG.AWS_IAM_VALID_VAULT_USERS, CONFIG.AWS_IAM_VAULT_USER_AUTH_MECHANISM, CONFIG.AWS_IAM_VAULT_USER_LEASE_TIME
        else:
            yield iam_user_is_valid, user

def user_has_password(username):
    """
    Returns true if the user has a password set
    :param username: str The username you which to check the existance of a password for
    :return: bool True is the user specified has a password, False if not
    """
    try:
        CFN.get_login_profiles(username)
        return True
    except BotoServerError:
        return False

def user_has_mfa_enabled(username):
    """
    Tests whether a given user has two factor authentication enabled
    :param username: str The user that you want to test if 2FA is enabled for
    :returns: bool True if 2FA is enabled for this user, False if not
    """
    mfa_devices = CFN.get_all_mfa_devices(username)
    return len(mfa_devices['list_mfa_devices_response']['list_mfa_devices_result']['mfa_devices']) > 0

def get_access_keys_for_user(username, active_only=True):
    """
    Returns a list of AWS Access Keys for the given user
    :param username: str The username for which you would like to return access keys for
    :returns: list A list of AWS Access Keys associated with this user
    """
    response = CFN.get_all_access_keys(user_name=username)['list_access_keys_response']['list_access_keys_result']['access_key_metadata']
    return [key['access_key_id'] for key in response if (active_only and key['status'] == 'Active') or not active_only]

def iam_user_is_valid(user, vault_usernames=None, vault_auth_method='ldap', vault_lease_time=3600):
    """
    Ensure that the username of the provided user:

    - Is known
    - If they have a password set
        - Have two factor authentication enabled
        - Have logged in to the console in the last AWS_IAM_USER_LAST_LOGGED_IN_DAYS days
    - Has only a single AWS access key
    - That all access keys have been used within the last AWS_IAM_KEY_LAST_USED_DAYS
    :param user:    str     The AWS IAM user that you would like to validate
    """
    # Assert that the user is known
    username = user['user_name']
    tokens = username.split('-')

    if username.startswith('vault-') and vault_usernames is not None and len(tokens) == 6:
        # Looks like a vault user.
        grace_period = 120
        earliest_create_time = time.time() - vault_lease_time - grace_period
        assert tokens[0] == 'vault'
        assert tokens[1] == vault_auth_method
        assert tokens[3] in vault_usernames
        assert int(tokens[4]) > earliest_create_time
    else:
        assert username.lower() in CONFIG.AWS_IAM_VALID_USERNAMES

    # Assert the user has a maximum of one active key
    access_keys = get_access_keys_for_user(username)
    assert len(access_keys) <= 1

    # Assert that the key has been used recently
    for key in access_keys:
        days_since_last_used = get_days_since_key_last_use(key)
        if days_since_last_used is not None:
            assert days_since_last_used < CONFIG.AWS_IAM_KEY_LAST_USED_DAYS

    # Is the user has a password check that they've got 2FA enabled and that they've logged in recently
    if user_has_password(username):
        assert user_has_mfa_enabled(username)
        last_login_days = get_days_since_key_last_login(username)
        assert (last_login_days is not None) and (last_login_days <= CONFIG.AWS_IAM_USER_LAST_LOGGED_IN_DAYS)

