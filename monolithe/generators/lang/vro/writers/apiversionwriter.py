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

from future import standard_library
from urlparse import urlparse
standard_library.install_aliases()

import os
from configparser import RawConfigParser
from shutil import copyfile, rmtree, copytree
from os import remove

from monolithe.lib import SDKUtils, TaskManager
from monolithe.generators.lib import TemplateFileWriter
from monolithe.specifications import SpecificationAPI

class APIVersionWriter(TemplateFileWriter):
    """ Provide useful method to write Java files.

    """
    def __init__(self, monolithe_config, api_info):
        """ Initializes a _JavaSDKAPIVersionFileWriter

        """
        super(APIVersionWriter, self).__init__(package="monolithe.generators.lang.vro")

        self.api_version = api_info["version"]
        self._api_version_string = SDKUtils.get_string_version(self.api_version)
        self.api_root = api_info["root"]
        self.api_prefix = api_info["prefix"]

        self.monolithe_config = monolithe_config
        self._output = self.monolithe_config.get_option("output", "transformer")
        self._name = self.monolithe_config.get_option("name", "transformer")
        self._class_prefix = ""
        self._product_accronym = self.monolithe_config.get_option("product_accronym")
        self._product_name = self.monolithe_config.get_option("product_name")
        self._url = self.monolithe_config.get_option("url", "transformer")

        self._package_prefix = self._get_package_prefix(self._url)
        self._package_name = self._package_prefix + ".vro." + self._name
        self._package_subdir = self._package_name.replace('.', '/')

        self.output_directory = "%s/vro" % (self._output)
        self.override_folder = os.path.normpath("%s/__overrides" % self.output_directory)
        self.fetchers_path = "/fetchers/"

        self.attrs_defaults = RawConfigParser()
        path = "%s/vro/__attributes_defaults/attrs_defaults.ini" % self._output
        self.attrs_defaults.optionxform = str
        self.attrs_defaults.read(path)

        self.entity_name_attrs = RawConfigParser()
        path = "%s/vro/__attributes_defaults/entity_name_attrs.ini" % self._output
        self.entity_name_attrs.optionxform = str
        self.entity_name_attrs.read(path)

        self.attrs_types = RawConfigParser()
        path = "%s/vro/__attributes_defaults/attrs_types.ini" % self._output
        self.attrs_types.optionxform = str
        self.attrs_types.read(path)
	
        with open("%s/vro/__code_header" % self._output, "r") as f:
            self.header_content = f.read()

    def perform(self, specifications):
        """
        """
        self._resolve_parent_apis(specifications) # Temporary fix, see method's comment for more info
        self._set_enum_list_local_type(specifications) # Temporary until get_type_name is enhanced to include specificiation subtype and local_name

        self._write_file(self.output_directory, "pom.xml.tpl", "pom.xml")
        self._write_o11plugin(specifications)
        self._write_o11plugin_core(specifications)
        self._write_o11plugin_package()

    def _write_o11plugin(self, specifications):
        """
        """
        output_directory = "%s/o11nplugin-%s" % (self.output_directory, self._name.lower())
        self._write_file(output_directory, "o11nplugin/pom.xml.tpl", "pom.xml")
        license_output_directory = "%s/src/main/vmoapp/VSO-INF" % (output_directory)
        os.makedirs(license_output_directory)
        copyfile("%s/LICENSE" % (self.output_directory), "%s/vsoapp.txt" % (license_output_directory));

        icons_output_directory = "%s/src/main/dar/resources/images" % (output_directory)
        os.makedirs(icons_output_directory)
        icons_source_directory = "%s/__icons" % (self.output_directory)
        self._copyfile("icon-plugin.png", icons_source_directory, icons_output_directory)
        self._copyfile("icon-session.png", icons_source_directory, icons_output_directory)
        self._copyfile("icon-folder.png", icons_source_directory, icons_output_directory)
        for rest_name, specification in specifications.items():
            self._copyfile("icon-%s.png" % (specification.entity_name.lower()), icons_source_directory, icons_output_directory)
        rmtree("%s" % (icons_source_directory))

    def _write_o11plugin_core(self, specifications):
        """
        """
        output_directory = "%s/o11nplugin-%s-core" % (self.output_directory, self._name.lower())
        self._write_file(output_directory, "o11nplugin-core/pom.xml.tpl", "pom.xml")
        
        source_output_directory = "%s/src/main/java/%s" % (output_directory, self._package_subdir)
        self._write_modulebuilder(source_output_directory, package_name=self._package_name)
        self._write_pluginadaptor(source_output_directory, package_name=self._package_name)
        self._write_pluginfactory(specifications, source_output_directory, package_name=self._package_name)

        model_package_name = self._package_name + ".model"
        model_source_output_directory = "%s/model" % (source_output_directory)
        self._write_constants(specifications, model_source_output_directory, package_name=model_package_name)
        self._write_sessionmanager(model_source_output_directory, package_name=model_package_name)
        self._write_session(specifications, model_source_output_directory, package_name=model_package_name)
        self._write_modelhelper(specifications, model_source_output_directory, package_name=model_package_name)
        
        task_manager = TaskManager()
        for rest_name, specification in specifications.items():
            task_manager.start_task(method=self._write_model, specification=specification, specification_set=specifications, output_directory=model_source_output_directory, package_name=model_package_name)
            task_manager.start_task(method=self._write_fetcher, specification=specification, specification_set=specifications, output_directory=model_source_output_directory, package_name=model_package_name)
        task_manager.wait_until_exit()

    def _write_o11plugin_package(self):
        """
        """
        output_directory = "%s/o11nplugin-%s-package" % (self.output_directory, self._name.lower())
        self._write_file(output_directory, "o11nplugin-package/pom.xml.tpl", "pom.xml")
        self._write_file("%s/src/main/resources/META-INF" % (output_directory), "o11nplugin-package/dunes-meta-inf.xml.tpl", "dunes-meta-inf.xml")
        copyfile("%s/archetype.keystore" % (self.output_directory), "%s/archetype.keystore" % (output_directory));
        remove("%s/archetype.keystore" % (self.output_directory))

        resources_output_directory = "%s/src/main/resources/Workflow" % (output_directory)
        resources_source_directory = "%s/__resources/Workflow" % (self.output_directory)
        copytree(resources_source_directory, resources_output_directory)
        rmtree("%s" % (resources_source_directory))

    def _write_session(self, specifications, output_directory, package_name):
        """ Write SDK session file

            Args:
                version (str): the version of the server

        """
        template_file = "o11nplugin-core/session.java.tpl"
        base_name = "Session"
        filename = "%s%s.java" % (self._class_prefix, base_name)
        override_content = self._extract_override_content(base_name)

        self.write(destination=output_directory,
                   filename=filename,
                   template_name=template_file,
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   class_prefix=self._class_prefix,
                   root_api=self.api_root,
                   name=self._name,
                   api_prefix=self.api_prefix,
                   override_content=override_content,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   package_name=package_name,
                   specifications=list(specifications.values()),
                   root_entity=specifications[self.api_root])

    def _write_model(self, specification, specification_set, output_directory, package_name):
        """ Write autogenerate specification file

        """
        template_file = "o11nplugin-core/model.java.tpl"
        filename = "%s%s.java" % (self._class_prefix, specification.entity_name)

        override_content = self._extract_override_content(specification.entity_name)
        superclass_name = "BaseRootObject" if specification.rest_name == self.api_root else "BaseObject"

        defaults = {}
        section = specification.entity_name
        if self.attrs_defaults.has_section(section):
            for attribute in self.attrs_defaults.options(section):
                defaults[attribute] = self.attrs_defaults.get(section, attribute)

        entity_name_attr = "id"
        if self.entity_name_attrs.has_section(section):
            entity_name_attr = self.entity_name_attrs.get(section, "name")

        self.write(destination=output_directory,
                   filename=filename, 
                   template_name=template_file,
                   specification=specification,
                   specification_set=specification_set,
                   version=self.api_version,
                   name=self._name,
                   class_prefix=self._class_prefix,
                   product_accronym=self._product_accronym,
                   override_content=override_content,
                   superclass_name=superclass_name,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   package_name=package_name,
                   attribute_defaults=defaults,
                   entity_name_attr=entity_name_attr,
                   root_api=self.api_root)

        return (filename, specification.entity_name)

    def _write_fetcher(self, specification, specification_set, output_directory, package_name):
        """ Write fetcher

        """
        template_file = "o11nplugin-core/fetcher.java.tpl"
        destination = "%s%s" % (output_directory, self.fetchers_path)
        base_name = "%sFetcher" % specification.entity_name_plural
        filename = "%s%s.java" % (self._class_prefix, base_name)
        override_content = self._extract_override_content(base_name)

        self.write(destination=destination,
                   filename=filename,
                   template_name=template_file,
                   specification=specification,
                   specification_set=specification_set,
                   class_prefix=self._class_prefix,
                   product_accronym=self._product_accronym,
                   override_content=override_content,
                   header=self.header_content,
                   name=self._name,
                   version_string=self._api_version_string,
                   package_name=package_name)

        return (filename, specification.entity_name_plural)

    def _write_modulebuilder(self, output_directory, package_name):
        """
        """
        template_file = "o11nplugin-core/modulebuilder.java.tpl"
        base_name = "ModuleBuilder"
        filename = "%s%s.java" % (self._class_prefix, base_name)
        override_content = self._extract_override_content(base_name)

        self.write(destination=output_directory,
                   filename=filename,
                   template_name=template_file,
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   class_prefix=self._class_prefix,
                   root_api=self.api_root,
                   name=self._name,
                   api_prefix=self.api_prefix,
                   override_content=override_content,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   package_name=package_name)

    def _write_pluginadaptor(self, output_directory, package_name):
        """
        """
        template_file = "o11nplugin-core/pluginadaptor.java.tpl"
        base_name = "PluginAdaptor"
        filename = "%s%s.java" % (self._class_prefix, base_name)
        override_content = self._extract_override_content(base_name)

        self.write(destination=output_directory,
                   filename=filename,
                   template_name=template_file,
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   class_prefix=self._class_prefix,
                   root_api=self.api_root,
                   name=self._name,
                   api_prefix=self.api_prefix,
                   override_content=override_content,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   package_name=package_name)

    def _write_pluginfactory(self, specifications, output_directory, package_name):
        """
        """
        template_file = "o11nplugin-core/pluginfactory.java.tpl"
        base_name = "PluginFactory"
        filename = "%s%s.java" % (self._class_prefix, base_name)
        override_content = self._extract_override_content(base_name)

        self.write(destination=output_directory,
                   filename=filename,
                   template_name=template_file,
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   class_prefix=self._class_prefix,
                   root_api=self.api_root,
                   name=self._name,
                   api_prefix=self.api_prefix,
                   override_content=override_content,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   package_name=package_name,
                   specification_set=specifications,
                   specifications=list(specifications.values()))

    def _write_constants(self, specifications, output_directory, package_name):
        """
        """
        template_file = "o11nplugin-core/constants.java.tpl"
        base_name = "Constants"
        filename = "%s%s.java" % (self._class_prefix, base_name)
        override_content = self._extract_override_content(base_name)

        self.write(destination=output_directory,
                   filename=filename,
                   template_name=template_file,
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   class_prefix=self._class_prefix,
                   root_api=self.api_root,
                   name=self._name,
                   api_prefix=self.api_prefix,
                   override_content=override_content,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   product_name=self._product_name,
                   package_name=package_name,
                   specification_set=specifications,
                   specifications=list(specifications.values()))

    def _write_sessionmanager(self, output_directory, package_name):
        """
        """
        template_file = "o11nplugin-core/sessionmanager.java.tpl"
        base_name = "SessionManager"
        filename = "%s%s.java" % (self._class_prefix, base_name)
        override_content = self._extract_override_content(base_name)

        self.write(destination=output_directory,
                   filename=filename,
                   template_name=template_file,
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   class_prefix=self._class_prefix,
                   root_api=self.api_root,
                   name=self._name,
                   api_prefix=self.api_prefix,
                   override_content=override_content,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   package_name=package_name)

    def _write_modelhelper(self, specifications, output_directory, package_name):
        """
        """
        template_file = "o11nplugin-core/modelhelper.java.tpl"
        base_name = "ModelHelper"
        filename = "%s%s.java" % (self._class_prefix, base_name)
        override_content = self._extract_override_content(base_name)

        self.write(destination=output_directory,
                   filename=filename,
                   template_name=template_file,
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   class_prefix=self._class_prefix,
                   root_api=self.api_root,
                   name=self._name,
                   api_prefix=self.api_prefix,
                   override_content=override_content,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   product_name=self._product_name,
                   package_name=package_name,
                   specification_set=specifications,
                   specifications=list(specifications.values()))

    def _write_file(self, output_directory, template_file, filename):
        """ 
        """
        self.write(destination=output_directory,
                   filename=filename,
                   template_name=template_file,
                   version=self.api_version,
                   product_accronym=self._product_accronym,
                   class_prefix=self._class_prefix,
                   root_api=self.api_root,
                   api_prefix=self.api_prefix,
                   product_name=self._product_name,
                   name=self._name,
                   header=self.header_content,
                   version_string=self._api_version_string,
                   package_prefix=self._package_prefix,
                   package_name=self._package_name)

    def _extract_override_content(self, name):
        """
        """
        # find override file
        specific_override_path = "%s/%s_%s%s.override.java" % (self.override_folder, self.api_version, self._class_prefix, name.title())
        generic_override_path = "%s/%s%s.override.java" % (self.override_folder, self._class_prefix, name.title())
        final_path = specific_override_path if os.path.exists(specific_override_path) else generic_override_path

        # Read override from file
        override_content = None
        if os.path.isfile(final_path):
            override_content = open(final_path).read()

        return override_content

    def _get_package_prefix(self, url):
        ""
        ""
        hostname_parts = self._get_hostname_parts(url)

        package_name = ""
        for index, hostname_part in enumerate(reversed(hostname_parts)):
            package_name = package_name + hostname_part
            if index < len(hostname_parts) - 1:
                package_name = package_name + '.'

        return package_name

    def _get_hostname_parts(self, url):
        ""
        ""
        if url.find("http://") != 0:
            url = "http://" + url

        hostname = urlparse(url).hostname
        hostname_parts = hostname.split('.')

        valid_hostname_parts = []
        for hostname_part in hostname_parts:
            if hostname_part != "www":
                valid_hostname_parts.append(hostname_part)

        return valid_hostname_parts

    # Custom version of this method until the main one gets fixed
    def _resolve_parent_apis(self, specifications):
        """
        """
        for specification_rest_name, specification in specifications.items():
            specification.parent_apis[:] = []
            for rest_name, remote_spec in specifications.items():
                for related_child_api in remote_spec.child_apis:
                    if related_child_api.rest_name == specification.rest_name:
                        parent_api = SpecificationAPI(specification=remote_spec)
                        parent_api.rest_name = remote_spec.rest_name
                        if specification.allows_get:
                            parent_api.allows_get = True
                        if specification.allows_create:
                            parent_api.allows_create = True
                        if specification.allows_update:
                            parent_api.allows_update = True
                        if specification.allows_delete:
                            parent_api.allows_Delete = True

                        specification.parent_apis.append(parent_api)

    def _set_enum_list_local_type(self, specifications):
        ""
        ""
        for rest_name, specification in specifications.items():
            for attribute in specification.attributes:
                if attribute.type == "enum":
                    enum_type = attribute.local_name[0:1].upper() + attribute.local_name[1:]
                    attribute.local_type = enum_type
                elif attribute.type == "object":
                    attr_type = "Object"
                    if self.attrs_types.has_option(specification.entity_name, attribute.local_name):
                        type = self.attrs_types.get(specification.entity_name, attribute.local_name)
                        if type:
                            attr_type = type
                        else:
                            print specification.entity_name + "." + attribute.local_name
                        attribute.local_type = attr_type
                elif attribute.type == "list":
                    if attribute.subtype == "enum":
                        enum_subtype = attribute.local_name[0:1].upper() + attribute.local_name[1:]
                        attribute.local_type = "java.util.List<" + enum_subtype + ">"
                    elif attribute.subtype == "object":
                        attr_type = "java.util.List<com.fasterxml.jackson.databind.JsonNode>"
                        if self.attrs_types.has_option(specification.entity_name, attribute.local_name):
                            type = self.attrs_types.get(specification.entity_name, attribute.local_name)
                            if type:
                                attr_type = type
                        attribute.local_type = attr_type
                    elif attribute.subtype == "entity":
                        attribute.local_type = "java.util.List<com.fasterxml.jackson.databind.JsonNode>"
                    else:
                        attribute.local_type = "java.util.List<String>"

    def _copyfile(self, filename, input_directory, output_directory):
         ""
         ""

         input_file = "%s/%s" % (input_directory, filename)
         if os.path.isfile(input_file):
             output_file = "%s/%s" % (output_directory, filename)
             copyfile(input_file, output_file)
