# -*- coding: utf-8 -*-
# TODO

from setuptools import setup
import os

packages = ['tdldk']
resources = []
sdk_api_version_path = "./tdldk"

for version_folder in os.listdir(sdk_api_version_path):
    if os.path.isfile("%s/%s" % (sdk_api_version_path, version_folder)):
        continue

    packages.append("tdldk.%s" % version_folder)
    packages.append("tdldk.%s.fetchers" % version_folder)
    packages.append("tdldk.%s.autogenerates" % version_folder)

    resources.append(('tdldk/%s/resources' % version_folder, ['tdldk/%s/resources/attrs_defaults.ini' % version_folder]))

sdk_name_upper = "tdldk_VERSION".upper()

setup(
    name='tdldk',
    version=os.environ[sdk_name_upper] if sdk_name_upper in os.environ else "1.0",
    url='www.mycompany.net/mysdk',
    author='someone',
    author_email='someone@yourcompany.com',
    packages=packages,
    description='SDK for the My Product',
    long_description=open('README.md').read(),
    install_requires=[line for line in open('requirements.txt')],
    license='BSD',
    include_package_data=True,
    data_files=resources
)