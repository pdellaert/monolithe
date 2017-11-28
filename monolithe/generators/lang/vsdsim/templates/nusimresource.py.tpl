# -*- coding: utf-8 -*-
{{ header }}

import json
import logging
import random
import re
import time
import uuid

from flask_restful import Resource, abort, request

from nuagevsdsim.common.utils import NUAGE_API_DATA, get_idiomatic_name, get_singular_name


class NUSimResource(Resource):
    __vspk_class__ = None
    __unique_fields__ = []
    __mandatory_fields__ = []
    __default_fields__ = {}
    __get_parents__ = []
    __create_parents__ = []

    def __init__(self):
        pass

    def get(self, parent_type=None, parent_id=None, entity_id=None):
        logging.debug('GET - {0:s} - parent_type: {1:s} - parent_id: {2:s} - entity_id: {3:s}'.format(
            self.__vspk_class__.rest_name,
            parent_type,
            parent_id,
            entity_id))

        if parent_type:
            parent_type = get_singular_name(parent_type)

        headers = self._parse_nuage_headers(headers=request.headers)
        logging.debug('GET - {0:s} - headers: {1:s}'.format(self.__vspk_class__.rest_name, headers))
        http_filter = headers['X-Nuage-Filter']

        result = []
        if entity_id:
            self._abort_missing_entity('id', entity_id)
            result.append(NUAGE_API_DATA[self.__vspk_class__.rest_name][entity_id].to_dict())

        elif parent_type and parent_id:
            self._abort_get_wrong_parent(parent_type=parent_type, parent_id=parent_id)
            if parent_id in NUAGE_API_DATA['{0:s}_{1:s}'.format(parent_type, self.__vspk_class__.rest_name)].keys():
                for key, entity in NUAGE_API_DATA['{0:s}_{1:s}'.format(parent_type, self.__vspk_class__.rest_name)][parent_id].iteritems():
                    if self._verify_filter(http_filter=http_filter, entity=entity):
                        result.append(entity.to_dict())
                        if headers['X-Nuage-Page'] == '0' and headers['X-Nuage-PageSize'] == '1':
                            break

        else:
            for key, entity in NUAGE_API_DATA[self.__vspk_class__.rest_name].iteritems():
                if key != NUAGE_API_DATA['ROOT_UUIDS']['csp_enterprise'] and self._verify_filter(http_filter=http_filter, entity=entity):
                    result.append(entity.to_dict())
                    if headers['X-Nuage-Page'] == '0' and headers['X-Nuage-PageSize'] == '1':
                        break

        headers['X-Nuage-Count'] = len(result)
        return result, 200, self._build_response_headers(request_headers=headers)

    def delete(self, entity_id=None):
        logging.debug('DELETE - {0:s} - entity_id: {1:s}'.format(self.__vspk_class__.rest_name, entity_id))

        if entity_id == NUAGE_API_DATA['ROOT_UUIDS']['csproot_user']:
            return_data = {
                'errors': [{
                    'property': '',
                    'descriptions': [
                        {
                            'description': 'System user cannot be deleted.',
                            'title': 'System user cannot be deleted'
                        }
                    ]
                }],
                "internalErrorCode": 2013
            }
            abort(409, **return_data)

        if entity_id == NUAGE_API_DATA['ROOT_UUIDS']['csp_enterprise']:
            return_data = {
                'errors': [{
                    'property': '',
                    'descriptions': [
                        {
                            'description': 'System enterprise cannot be deleted.',
                            'title': 'System enterprise cannot be deleted'
                        }
                    ]
                }],
                "internalErrorCode": 2010
            }
            abort(409, **return_data)

        self._abort_missing_entity('id', entity_id)

        if entity_id:
            self._recursive_delete(entity_id=entity_id, entity_type=self.__vspk_class__.rest_name)
        return '', 204

    def put(self, parent_type=None, parent_id=None, entity_id=None):
        logging.debug('PUT - {0:s} - parent_type: {1:s} - parent_id: {2:s} - entity_id: {3:s}'.format(
            self.__vspk_class__.rest_name,
            parent_type,
            parent_id,
            entity_id))
        logging.debug('PUT - data: {0}'.format(request.data))

        if parent_type:
            parent_type = get_singular_name(parent_type)

        if entity_id:
            self._abort_missing_entity('id', entity_id)
            data = json.loads(request.data)

            for field in self.__mandatory_fields__:
                self._abort_mandatory_field(data=data, field=field)
            for field in self.__unique_fields__:
                self._abort_duplicate_field(data=data, field=field)

            data = self._parse_data(data)
            old_entity = NUAGE_API_DATA[self.__vspk_class__.rest_name][entity_id]
            new_entity = self.__vspk_class__(**data)
            new_entity.id = old_entity.id
            if hasattr(new_entity, 'creation_date'):
                new_entity.creation_date = old_entity.creation_date
            if hasattr(new_entity, 'last_updated_by'):
                new_entity.last_updated_by = NUAGE_API_DATA['ROOT_UUIDS']['csproot_user']
            if hasattr(new_entity, 'last_updated_date'):
                new_entity.last_updated_date = int(time.time() * 1000)
            if hasattr(new_entity, 'customer_id'):
                new_entity.customer_id = old_entity.customer_id
            if hasattr(new_entity, 'dictionary_version'):
                new_entity.dictionary_version = 2
            if hasattr(new_entity, 'parent_id'):
                new_entity.parent_id = old_entity.parent_id
                new_entity.parent_type = old_entity.parent_type
            del old_entity

            NUAGE_API_DATA[self.__vspk_class__.rest_name][new_entity.id] = new_entity
            if new_entity.parent_id and new_entity.parent_type:
                NUAGE_API_DATA['{0:s}_{1:s}'.format(new_entity.parent_type, self.__vspk_class__.rest_name)][new_entity.parent_id][new_entity.id] = new_entity
            return [NUAGE_API_DATA[self.__vspk_class__.rest_name][new_entity.id].to_dict()], 201

        elif parent_type and parent_id:
            self._abort_get_wrong_parent(parent_type=parent_type, parent_id=parent_id)

            members = {}
            data = json.loads(request.data)
            if len(data) > 0:
                for member_id in data:
                    self._abort_missing_entity('id', member_id)
                    members[member_id] = NUAGE_API_DATA[self.__vspk_class__.rest_name][member_id]
            NUAGE_API_DATA['{0:s}_{1:s}'.format(parent_type, self.__vspk_class__.rest_name)][parent_id] = members
            return None, 204

    def post(self, parent_type=None, parent_id=None):
        logging.debug('POST - {0:s} - parent_type: {1:s} - parent_id: {2:s}'.format(
            self.__vspk_class__.rest_name,
            parent_type,
            parent_id))
        logging.debug('POST - data: {0}'.format(request.data))

        if parent_type:
            parent_type = get_singular_name(parent_type)

        data = json.loads(request.data)

        for field in self.__mandatory_fields__:
            self._abort_mandatory_field(data=data, field=field)
        for field in self.__unique_fields__:
            self._abort_duplicate_field(data=data, field=field)
        for field, value in self.__default_fields__.iteritems():
            if field not in data.keys() or not data[field]:
                data[field] = value

        data = self._parse_data(data)

        entity = self.__vspk_class__(**data)
        entity.id = str(uuid.uuid1())
        if hasattr(entity, 'owner'):
            entity.owner = NUAGE_API_DATA['ROOT_UUIDS']['csproot_user']
        if hasattr(entity, 'creation_date'):
            entity.creation_date = int(time.time() * 1000)
        if hasattr(entity, 'last_updated_by'):
            entity.last_updated_by = NUAGE_API_DATA['ROOT_UUIDS']['csproot_user']
        if hasattr(entity, 'last_updated_date'):
            entity.last_updated_date = int(time.time() * 1000)
        if hasattr(entity, 'customer_id'):
            entity.customer_id = 10000 + random.randint(0, 89999)
        if hasattr(entity, 'dictionary_version'):
            entity.dictionary_version = 2

        if parent_type and parent_id:
            self._abort_post_wrong_parent(parent_type=parent_type, parent_id=parent_id)
            if hasattr(entity, 'parent_type'):
                entity.parent_type = parent_type
                entity.parent_id = parent_id
        elif 'me' not in self.__create_parents__:
            return_data = {
                'errors': [{
                    'property': '',
                    'descriptions': [
                        {
                            'description': 'Entity {0:s} can not be created on the root level'.format(self.__vspk_class__.rest_name),
                            'title': 'Invalid parent'
                        }
                    ]
                }]
            }
            abort(409, **return_data)

        NUAGE_API_DATA[self.__vspk_class__.rest_name][entity.id] = entity
        if parent_type and parent_id:
            if parent_id in NUAGE_API_DATA['{0:s}_{1:s}'.format(parent_type, self.__vspk_class__.rest_name)].keys():
                NUAGE_API_DATA['{0:s}_{1:s}'.format(parent_type, self.__vspk_class__.rest_name)][parent_id][entity.id] = entity
            else:
                NUAGE_API_DATA['{0:s}_{1:s}'.format(parent_type, self.__vspk_class__.rest_name)][parent_id] = {entity.id: entity}
        return [NUAGE_API_DATA[self.__vspk_class__.rest_name][entity.id].to_dict()], 201

    def _abort_duplicate_field(self, data=None, field=None):
        if field in data.keys() and data[field]:
            results = self._find_entities_by_field(NUAGE_API_DATA[self.__vspk_class__.rest_name], field, data[field])
            if len(results) > 1 or (len(results) == 1 and 'ID' in data.keys() and (data['ID'] is None or results[0].id != data['ID'])):
                return_data = {
                    'errors': [{
                        'property': field,
                        'descriptions': [
                            {
                                'description': 'Another {0:s} with the same {1:s} = {2:s} exists.'.format(self.__vspk_class__.rest_name, field, data[field]),
                                'title': 'Cannot create duplicate entity.'
                            }
                        ]
                    }],
                    "internalErrorCode": 9501
                }
                abort(409, **return_data)

    def _abort_get_wrong_parent(self, parent_type, parent_id):
        if parent_type not in self.__get_parents__:
            return_data = {
                'errors': [{
                    'property': '',
                    'descriptions': [
                        {
                            'description': 'Invalid get parent type {0:s} for a {1:s}'.format(parent_type, self.__vspk_class__.rest_name),
                            'title': 'Invalid parent'
                        }
                    ]
                }]
            }
            abort(409, **return_data)
        elif parent_id not in NUAGE_API_DATA[parent_type].keys():
            return_data = {
                'errors': [{
                    'property': '',
                    'descriptions': [
                        {
                            'description': 'Parent {0:s} with ID {1:s} does not exist'.format(parent_type, parent_id),
                            'title': 'Invalid parent'
                        }
                    ]
                }]
            }
            abort(409, **return_data)

    def _abort_missing_entity(self, field, value):
        if len(self._find_entities_by_field(data=NUAGE_API_DATA[self.__vspk_class__.rest_name], field=field, value=value)) == 0:
            abort(404, message='Unable to find entity with field {0} and value {1}'.format(field, value))

    def _abort_post_wrong_parent(self, parent_type, parent_id):
        if parent_type not in self.__create_parents__:
            return_data = {
                'errors': [{
                    'property': '',
                    'descriptions': [
                        {
                            'description': 'Invalid post parent type {0:s} for a {1:s}'.format(parent_type, self.__vspk_class__.rest_name),
                            'title': 'Invalid parent'
                        }
                    ]
                }]
            }
            abort(409, **return_data)
        elif parent_id not in NUAGE_API_DATA[parent_type].keys():
            return_data = {
                'errors': [{
                    'property': '',
                    'descriptions': [
                        {
                            'description': 'Parent {0:s} with ID {1:s} does not exist'.format(parent_type, parent_id),
                            'title': 'Invalid parent'
                        }
                    ]
                }]
            }
            abort(409, **return_data)

    def _recursive_delete(self, entity_id, entity_type):
        # Loop through database
        for key in NUAGE_API_DATA.keys():
            if key.startswith('{0:s}_'.format(entity_type)):
                if entity_id in NUAGE_API_DATA[key].keys():
                    if NUAGE_API_DATA[key]['_TYPE'] != 'member':
                        for sub_key in NUAGE_API_DATA[key][entity_id].keys():
                            if sub_key != '_TYPE':
                                self._recursive_delete(entity_id=sub_key, entity_type=NUAGE_API_DATA[key][entity_id][sub_key].rest_name)
                    del NUAGE_API_DATA[key][entity_id]
            elif key.endswith('_{0:s}'.format(entity_type)):
                for parent_id in NUAGE_API_DATA[key].keys():
                    if parent_id != '_TYPE' and entity_id in NUAGE_API_DATA[key][parent_id].keys():
                        del NUAGE_API_DATA[key][parent_id][entity_id]
        # Delete entity itself
        del NUAGE_API_DATA[entity_type][entity_id]

    @staticmethod
    def _abort_mandatory_field(data=None, field=None):
        if field not in data.keys() or not data[field]:
            return_data = {
                'errors': [{
                    'property': field,
                    'descriptions': [
                        {
                            'description': 'This value cannot be null',
                            'title': 'Invalid input. Value cannot be null'
                        }
                    ]
                }],
                "internalErrorCode": 5001
            }
            abort(409, **return_data)

    @staticmethod
    def _build_response_headers(request_headers=None):
        if request_headers is None:
            request_headers = dict()
        result = {}
        for header, value in request_headers.iteritems():
            if value is not None:
                result[header] = value
        return result

    @staticmethod
    def _find_entities_by_field(data, field, value):
        result = []
        if data and field and value and len(data) > 0 and hasattr(data.itervalues().next(), get_idiomatic_name(field)):
            result = list(v for k, v in data.iteritems() if getattr(v, get_idiomatic_name(field)) == value)
        return result

    @staticmethod
    def _parse_data(data=None):
        if data is None:
            data = dict()
        new_data = {}
        for key, value in data.iteritems():
            new_data[get_idiomatic_name(key)] = value
        return new_data

    @staticmethod
    def _parse_nuage_headers(headers=None):
        if headers is None:
            headers = dict()
        result = {
            'X-Nuage-Organization': 'csp',
            'X-Nuage-Page': None,
            'X-Nuage-PageSize': None,
            'X-Nuage-OrderBy': None,
            'X-Nuage-FilterType': None,
            'X-Nuage-Filter': None,
            'X-Nuage-Count': None,
            'X-Nuage-Custom': None,
            'X-Nuage-ClientType': None,
            'Access-Control-Expose-Headers': 'X-Nuage-Organization, X-Nuage-ProxyUser, X-Nuage-OrderBy, X-Nuage-FilterType, X-Nuage-Filter, X-Nuage-Page, X-Nuage-PageSize, X-Nuage-Count, X-Nuage-Custom, X-Nuage-ClientType'
        }

        lower_headers = {k.lower(): v for k, v in headers.iteritems()}
        for header in result.keys():
            if header.lower() in lower_headers.keys():
                result[header] = lower_headers[header.lower()]
        return result

    @staticmethod
    def _verify_filter(http_filter, entity):
        if http_filter:
            reg = re.search('[\'"]?([\w]*)[\'"]?\s*==\s*[\'"]?([\w\s-]*)[\'"]?', http_filter)
            if len(reg.groups()) == 2:
                field, value = reg.groups()
                if hasattr(entity, get_idiomatic_name(field)) and getattr(entity, get_idiomatic_name(field)) == value:
                    return True
            return False
        return True
