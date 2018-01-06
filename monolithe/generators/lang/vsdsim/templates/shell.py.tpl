# -*- coding: utf-8 -*-
{{ header }}
"""
nuage-vsd-sim
=============
A sample Nuage VSD API simulator
"""

import argparse
import ConfigParser
import os

from flask import Flask
from flask_restful import Api

from nuagevsdsim import simentities as sim
from nuagevsdsim.common import NUSimConfig, utils


class NuageVSDSim(object):
    def __init__(self):
        """
        Handle commands for interaction between Nuage Networks VSP and Amazon AWS
        """

        parser = argparse.ArgumentParser(
            description="A sample Nuage VSD API simulator."
        )
        parser.add_argument('-c', '--config-file', required=False,
                            help='Configuration file to use, if not specified ~/.nuage-vsd-sim/config.ini is used, it that does not exist, /etc/nuage-vsd-sim/config.ini is used.',
                            dest='config_file', type=str)
        args, command_args = parser.parse_known_args()

        # Handling configuration file
        if args.config_file:
            cfg = utils.parse_config(args.config_file)
        elif os.path.isfile('{0:s}/.nuage-vsd-sim/config.ini'.format(os.path.expanduser('~'))):
            cfg = utils.parse_config('{0:s}/.nuage-vsd-sim/config.ini'.format(os.path.expanduser('~')))
        elif os.path.isfile('/etc/nuage-vsd-sim/config.ini'):
            cfg = utils.parse_config('/etc/nuage-vsd-sim/config.ini')
        else:
            cfg = ConfigParser.ConfigParser()
            cfg.add_section('LOG')
            cfg.set('LOG', 'directory', '')
            cfg.set('LOG', 'file', '')
            cfg.set('LOG', 'level', 'DEBUG')

        # Handling logging
        log_dir = cfg.get('LOG', 'directory')
        log_file = cfg.get('LOG', 'file')
        log_level = cfg.get('LOG', 'level')

        if not log_level:
            log_level = 'WARNING'

        log_path = None
        if log_dir and log_file and os.path.isdir(log_dir) and os.access(log_dir, os.W_OK):
            log_path = os.path.join(log_dir, log_file)

        logger = utils.configure_logging(log_level, log_path)
        logger.debug('Logging initiated')

        utils.init_base_entities()

        self.app = Flask(__name__)

        self.app.config.from_object(NUSimConfig)

        self.api = Api(self.app)

        self.api.add_resource(
            sim.NUSimRoot,
            '/',
            '/nuage',
            '/nuage/api',
            '/nuage/api/{{ apiversion }}'
        )

        {% for resourcename, classname in resourcenames.items() -%}
        self.api.add_resource(
            sim.{{ classname }},
            '/nuage/api/{{ apiversion }}/{{ resourcename }}'
            {%- if resourcename != 'me' %},
            '/nuage/api/{{ apiversion }}/{{ resourcename }}/<entity_id>',
            '/nuage/api/{{ apiversion }}/<parent_type>/<parent_id>/{{ resourcename }}'{%- endif %}
        )
        {% endfor %}

        self.app.run(host='0.0.0.0', port=5000, debug=(log_level == 'DEBUG'))


def main():
    NuageVSDSim()
