#!/usr/bin/env python

import imp
import json
import os
import requests

CONFIG = imp.load_source('config', os.environ['WATCHDOG_CONFIG_LOCATION'])

GOOGLE_PROJECTS = CONFIG.GOOGLE_PROJECTS
GOOGLE_EMAILS = CONFIG.GOOGLE_EMAILS


def test_google_project_users():
    prj_and_users = []
    for prj in GOOGLE_PROJECTS:
        rsp = requests.get("https://accounts.google.com/ServiceLoginAuth")
        rsp.raise_for_status()
        galx = rsp.cookies["GALX"]

        rsp = requests.post(
            "https://accounts.google.com/ServiceLoginAuth",
            data={
                "GALX": galx,
                "Email": prj["email"],
                "Passwd": prj["password"],
            },
            cookies={"GALX": galx},
            allow_redirects=False,
        )
        rsp.raise_for_status()
        sid = rsp.cookies["SID"]
        hsid = rsp.cookies["HSID"]
        ssid = rsp.cookies["SSID"]

        url = "https://console.developers.google.com/m/teamlist?pid=" + \
              prj["number"]
        rsp = requests.get(
            url,
            cookies={"SID": sid, "HSID": hsid, "SSID": ssid},
        )
        rsp.raise_for_status()
        json1 = json.loads(rsp.text[5:])  # skip ")]}\n"
        users = json1["teamList"]

        suffix = ".gserviceaccount.com"

        for user in users:
            prj_and_users.append({"prj": prj, "user": user, })

    for prj_and_user in prj_and_users:
        yield google_user_is_in_ldap, prj_and_user


def google_user_is_in_ldap(prj_and_user):
    prj = prj_and_user["prj"]
    email = prj_and_user["user"]["email"]
    assert email.endswith(".gserviceaccount.com") or email in GOOGLE_EMAILS, \
        "Unknown email on [{0}] ({1}): [{2}]".format(
            prj["name"], prj["number"], email)
