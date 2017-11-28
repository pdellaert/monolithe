# -*- coding: utf-8 -*-
{{ header }}
"""
Nuage VSD Sim Config
"""
import json

from bambou import NURESTObject


class NUSimEntityEncoder(json.JSONEncoder):
    def default(self, o):
        if issubclass(type(o), NURESTObject):
            return o.to_dict()


class NUSimConfig(object):
    RESTFUL_JSON = {'cls': NUSimEntityEncoder}
