#!/usr/bin/env python
"""
Iterate through every security group in a configured set of AWS regions and
verifies that:

- Every IP address exception (Everything except global exceptions - 0.0.0.0/0) are known
- Every global exception (0.0.0.0/0) are known

Required config.py variables:

AWS_SECURITY_GROUP_REGIONS            List[String]     A list of the AWS regions that
                                                       you want to audit

AWS_SECURITY_GROUP_IGNORE_SGS         List[String]     A list of security group names
                                                       that you want to ignore.
                                                       Useful for auto generated groups
                                                       that frequently change.

AWS_SECURITY_GROUP_IP_EXCEPTIONS           Dict        A dictionary with IP addresses/ranges
                                                       (X.X.X.X/NETMASK) as keys and descriptions
                                                       as values

AWS_SECURITY_GROUP_GLOBAL_EXCEPTIONS       Dict        A dictionary using the name of a security
                                                       group as the key mapping to a list of
                                                       exceptions, represented as strings of the
                                                       format "PROTOCOL-STARTPORT-ENDPORT-NETWORK/NETMASK"

AWS_SECURITY_GROUP_IGNORE_IP_STARTING_WITH    String   If an IP address in an exception starts with this
                                                       ignore it. Useful for excluding private VPC addresses
                                                       internal to your network
                                                       (This script is designed to audit external access)
"""
import re
import boto.ec2

import os
import imp
CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

def is_valid_global_exception(group, rule, region):
    """
    Asserts that the rule is valid for the group provided
    :param group:  str  The name of the security group that you wish to assert
                        that the globsal rule is valid for
    :param rule:   str  A string presenting the security group you wish to test,
                        in the format "PROTOCOL-STARTPORT-ENDPORT-NETWORK/NETMASK"
    :param region: str  The region that this rule is present for. Unused, but
                        present to ensure it's printed by pylint in the event of
                        an assertion failure to ease follow up.
    """
    assert region
    assert rule in CONFIG.AWS_SECURITY_GROUP_GLOBAL_EXCEPTIONS[group]

def is_known_ip(ip_address, group, region):
    """
    Asserts that an IP address or network range is known.
    :param ip_address:  str  The IP address or network range that you'd like to
                             assert is known, in the format "X.X.X.X/NETMASK"
    :param group:       str  The group that this IP address was found in. Unused,
                             but included to ensure that pylint prints it in the
                             debug output in the event of an assertion failure
     :param region:     str  The region that this rule is present for. Unused, but
                             present to ensure it's printed by pylint in the event of
                             an assertion failure to ease follow up.
    """
    assert group
    assert region
    assert ip_address in CONFIG.AWS_SECURITY_GROUP_IP_EXCEPTIONS.keys()

def test_all_security_groups():
    """
    Iterate through every security group in a configured set of AWS regions and
    verifies that:

    - Every IP address exception (Everything except global exceptions - 0.0.0.0/0) are known
    - Every global exception (0.0.0.0/0) are known
    """
    for region in CONFIG.AWS_SECURITY_GROUP_REGIONS:
        conn = boto.ec2.connect_to_region(region)
        for group in conn.get_all_security_groups():
            for rule in group.rules:
                for grant in rule.grants:
                    if group.name not in CONFIG.AWS_SECURITY_GROUP_IGNORE_SGS:
                        strrule = str(rule.ip_protocol).upper() + "-" + str(rule.from_port)  + "-" +  str(rule.to_port)  + "-" + str(grant)
                        if str(grant) == '0.0.0.0/0':
                            yield is_valid_global_exception, group.name, strrule, region
                        elif re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}', str(grant)) and \
                             not str(grant).startswith(CONFIG.AWS_SECURITY_GROUP_IGNORE_IP_STARTING_WITH) and \
                             not group.name not in CONFIG.AWS_SECURITY_GROUP_IGNORE_SGS:
                            yield is_known_ip, str(grant), group.name, region
                        else:
                            assert True
