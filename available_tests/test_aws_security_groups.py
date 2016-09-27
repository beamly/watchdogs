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
import os
import imp
import pytest
import boto.ec2

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])



def _all_security_groups_all_regions():

    all_security_groups = []

    for region in CONFIG.AWS_SECURITY_GROUP_REGIONS:
        conn = boto.ec2.connect_to_region(region)
        all_security_groups += ([(sg.name, region, sg) for sg in conn.get_all_security_groups()])

    return all_security_groups

@pytest.mark.parametrize("security_group_name,region,group", _all_security_groups_all_regions())
def test_all_security_groups(security_group_name, region, group):
    """
    Iterate through every security group in a configured set of AWS regions and
    verifies that:

    - Every IP address exception (Everything except global exceptions - 0.0.0.0/0) are known
    - Every global exception (0.0.0.0/0) are known
    """

    for rule in group.rules:
        for grant in rule.grants:
            if group.name not in CONFIG.AWS_SECURITY_GROUP_IGNORE_SGS:
                strrule = str(rule.ip_protocol).upper() + "-" + str(rule.from_port)  + "-" +  str(rule.to_port)  + "-" + str(grant)
                if str(grant) == '0.0.0.0/0':
                    assert strrule in CONFIG.AWS_SECURITY_GROUP_GLOBAL_EXCEPTIONS[group.name]
                elif re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}', str(grant)) and \
                     not str(grant).startswith(CONFIG.AWS_SECURITY_GROUP_IGNORE_IP_STARTING_WITH) and \
                     not group.name not in CONFIG.AWS_SECURITY_GROUP_IGNORE_SGS:
                    assert grant in CONFIG.AWS_SECURITY_GROUP_IP_EXCEPTIONS.keys()
                else:
                    assert True
