# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Alcatel-Lucent Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its contributors
#       may be used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import unicode_literals
from builtins import str
import os
import shutil
from collections import OrderedDict

from monolithe.lib import SDKUtils, TaskManager
from monolithe.generators.lib import TemplateFileWriter


class APIVersionWriter(TemplateFileWriter):
    """ Provide usefull method to write Python files.

    """
    def __init__(self, monolithe_config, api_info):
        """ Initializes a _PythonSDKAPIVersionFileWriter

        """
        super(APIVersionWriter, self).__init__(package="monolithe.generators.lang.vsdsim")

        self.api_version = api_info["version"]
        self.api_root = api_info["root"]
        self.api_prefix = api_info["prefix"]

        self.monolithe_config = monolithe_config
        self._output = self.monolithe_config.get_option("output", "transformer")
        self._transformation_name = self.monolithe_config.get_option("name", "transformer")
        self._class_prefix = self.monolithe_config.get_option("class_prefix", "transformer")
        self._product_accronym = self.monolithe_config.get_option("product_accronym")
        self._product_name = self.monolithe_config.get_option("product_name")

        self.output_directory = "%s/vsdsim/%s" % (self._output, self._transformation_name)
        self.override_folder = os.path.normpath("%s/../../__overrides" % self.output_directory)
        self.fetchers_path = "/fetchers/"

        with open("%s/vsdsim/__code_header" % self._output, "r") as f:
            self.header_content = f.read()

    def perform(self, specifications):
        """
        """
        self.model_filenames = dict()
        self.model_resourcenames = dict()
        self.child_parents = dict()

        self._write_root()
        self._write_resource()

        self._build_child_parents_relations(specifications)
        task_manager = TaskManager()
        for rest_name, specification in specifications.items():
            task_manager.start_task(method=self._write_model, specification=specification, specification_set=specifications)
        task_manager.wait_until_exit()
        self._write_init_models(filenames=self.model_filenames)

        self._write_shell(resourcenames=self.model_resourcenames)
        self._write_common_utils()

    def _write_root(self):
        """ Write the root entry of the sim
        """
        self.write(destination="%s/simentities" % self.output_directory, filename="nusimroot.py", template_name="nusimroot.py.tpl",
                   header=self.header_content)

    def _write_resource(self):
        """ Write the root object of all sim entries
        """
        self.write(destination="%s/simentities" % self.output_directory, filename="nusimresource.py", template_name="nusimresource.py.tpl",
                   header=self.header_content)

    def _write_shell(self, resourcenames):
        """ Write the root object of all sim entries
        """
        self.write(destination="%s" % self.output_directory, filename="shell.py", template_name="shell.py.tpl",
                   apiversion=SDKUtils.get_string_version(self.api_version),
                   resourcenames=self._prepare_resourcenames(resourcenames=resourcenames),
                   header=self.header_content)

    def _write_common_utils(self):
        """
        """
        self.write(destination="%s/common" % self.output_directory, filename="utils.py", template_name="utils.py.tpl",
                   name=self._transformation_name,
                   apiversion=SDKUtils.get_string_version(self.api_version),
                   child_parents=OrderedDict(sorted(self.child_parents.items())),
                   header=self.header_content)

    def _write_init_models(self, filenames):
        """ Write simentities init file

            Args:
                filenames (dict): dict of filename and classes

        """
        self.write(destination="%s/simentities" % self.output_directory, filename="__init__.py", template_name="__init__simentities.py.tpl",
                   filenames=self._prepare_filenames(filenames),
                   class_prefix=self._class_prefix,
                   header=self.header_content)

    def _write_model(self, specification, specification_set):
        """ Write autogenerate specification file

        """
        filename = "%s%s.py" % (self._class_prefix.lower(), specification.entity_name.lower())

        self.env.filters['handle_default_value'] = self._handle_default_value

        if specification.rest_name == self.api_root:
            self.write(destination="%s/simentities" % self.output_directory, filename=filename, template_name="nusimme.py.tpl",
                       header=self.header_content)
        else:
            self.write(destination="%s/simentities" % self.output_directory, filename=filename, template_name="model.py.tpl",
                       specification=specification,
                       specification_set=specification_set,
                       version=SDKUtils.get_string_version(self.api_version),
                       class_prefix=self._class_prefix,
                       child_parents=OrderedDict(sorted(self.child_parents[specification.rest_name].items())),
                       header=self.header_content)

        self.model_filenames[filename] = specification.entity_name
        self.model_resourcenames[specification.resource_name] = specification.entity_name

    def _build_child_parents_relations(self, specifications):
        """
        """
        for rest_name, specification in specifications.items():
            if not self.child_parents.has_key(rest_name):
                self.child_parents[rest_name] = {}
            for child in specification.child_apis:
                if not self.child_parents.has_key(child.rest_name):
                    self.child_parents[child.rest_name] = {}
                self.child_parents[child.rest_name][rest_name] = {
                    'allows_get': child.allows_get,
                    'allows_create': child.allows_create,
                    'relationship': child.relationship
                }

    def _prepare_filenames(self, filenames, suffix=''):
        """
        """
        formatted_filenames = {}

        for filename, classname in filenames.items():
            formatted_filenames[filename[:-3]] = str("%s%s%s" % (self._class_prefix, classname, suffix))

        return OrderedDict(sorted(formatted_filenames.items()))

    def _prepare_resourcenames(self, resourcenames, suffix=''):
        """
        """
        formatted_resourcenames = {}

        for resourcename, classname in resourcenames.items():
            formatted_resourcenames[resourcename] = str("%s%s%s" % (self._class_prefix, classname, suffix))

        return OrderedDict(sorted(formatted_resourcenames.items()))

    def _handle_default_value(self, attribute):
        """
        """
        if attribute.type in ("string", "enum"):
            return "'{0}'".format(attribute.default_value)

        if attribute.type == "boolean":
            if type(attribute.default_value) == 'bool':
                return attribute.default_value
            else:
                return attribute.default_value in ('true', 'True')

        if attribute.type == "integer":
            if type(attribute.default_value) == 'int':
                return attribute.default_value
            else:
                return int(attribute.default_value)

        if attribute.type in ("float", " time"):
            if type(attribute.default_value) == 'float':
                return attribute.default_value
            else:
                return float(attribute.default_value)

        if attribute.type in ("object"):
            try:
                value = int(attribute.default_value)
            except ValueError:
                if attribute.default_value in ('true', 'True', True, 'false', 'False', False):
                    value = attribute.default_value in ('true', 'True', True)
                else:
                    value = "'{0}'".format(attribute.default_value)
            return value

        return None