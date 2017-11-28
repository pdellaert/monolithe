# -*- coding: utf-8 -*-
{{ header }}
"""
{{ class_prefix }}{{ specification.entity_name }}
"""
from vspk import {{ version }} as vsdk

from nuagevsdsim.simentities.nusimresource import NUSimResource

class {{ class_prefix }}{{ specification.entity_name }}(NUSimResource):
    """ Represents a {{ specification.entity_name }}

        Notes:
            {{ specification.description }}
    """
{% set vars = {'prev': False} %}
    __vspk_class__ = vsdk.NU{{ specification.entity_name }}
    __unique_fields__ = [{% if vars.update({'prev': False}) %}{% endif %}{% for attribute in specification.attributes %}{% if attribute.unique %}{% if vars.prev %}, {% endif %}{% if vars.update({'prev': True}) %}{% endif %}'{{ attribute.name }}'{% endif %}{% endfor %}]
    __mandatory_fields__ = [{% if vars.update({'prev': False}) %}{% endif %}{% for attribute in specification.attributes %}{% if attribute.required %}{% if vars.prev %}, {% endif %}{% if vars.update({'prev': True}) %}{% endif %}'{{ attribute.name }}'{% endif %}{% endfor %}]
    __default_fields__ = {
        {% if vars.update({'prev': False}) %}{% endif %}{% for attribute in specification.attributes %}{% if attribute.default_value is not none %}{% if vars.prev %},
        {% endif %}{% if vars.update({'prev': True}) %}{% endif %}'{{ attribute.name }}': {{ attribute|handle_default_value }}{% endif %}{% endfor %}
    }
    __get_parents__ = [{% if vars.update({'prev': False}) %}{% endif %}{% for parent, info in child_parents.items() %}{% if info.allows_get %}{% if vars.prev %}, {% endif %}{% if vars.update({'prev': True}) %}{% endif %}'{{ parent }}'{% endif %}{% endfor %}]
    __create_parents__ = [{% if vars.update({'prev': False}) %}{% endif %}{% for parent, info in child_parents.items() %}{% if info.allows_create %}{% if vars.prev %}, {% endif %}{% if vars.update({'prev': True}) %}{% endif %}'{{ parent }}'{% endif %}{% endfor %}]

    def __init__(self):
        super({{ class_prefix }}{{ specification.entity_name }}, self).__init__()
