# -*- coding: utf-8 -*-
{{ header }}

from flask_restful import Resource

from nuagevsdsim.common.utils import NUAGE_API_DATA


class NUSimRoot(Resource):

    def get(self):
        return NUAGE_API_DATA
