# -*- coding: utf-8 -*-
{{ header }}
"""
SimMe
"""
import logging
import time
import uuid

from flask_restful import Resource

from nuagevsdsim.common.utils import NUAGE_API_DATA


class NUSimMe(Resource):
    @staticmethod
    def get():
        logging.debug('GET - me')
        result = [
            {
                "userName": NUAGE_API_DATA['user'][NUAGE_API_DATA['ROOT_UUIDS']['csproot_user']].user_name,
                "mobileNumber": None,
                "flowCollectionEnabled": False,
                "APIKey": str(uuid.uuid1()),
                "firstName": NUAGE_API_DATA['user'][NUAGE_API_DATA['ROOT_UUIDS']['csproot_user']].first_name,
                "statisticsEnabled": False,
                "APIKeyExpiry": int((time.time() + 86400) * 1000),
                "lastName": NUAGE_API_DATA['user'][NUAGE_API_DATA['ROOT_UUIDS']['csproot_user']].last_name,
                "enterpriseID": NUAGE_API_DATA['ROOT_UUIDS']['csp_enterprise'],
                "ID": NUAGE_API_DATA['ROOT_UUIDS']['csproot_user'],
                "entityScope": None,
                "avatarType": None,
                "enterpriseName": NUAGE_API_DATA['enterprise'][NUAGE_API_DATA['ROOT_UUIDS']['csp_enterprise']].name,
                "role": "CSPROOT",
                "statsTSDBServerAddress": None,
                "avatarData": None,
                "licenseCapabilities": [],
                "externalId": None,
                "password": None,
                "email": NUAGE_API_DATA['user'][NUAGE_API_DATA['ROOT_UUIDS']['csproot_user']].email,
                "externalID": None
            }
        ]
        return result
