# -*- coding: utf-8 -*-
{{ header }}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='{{ cli_name }}',
    version='{{ version }}',
    description='{{ description }}',
    url='{{ url }}',
    author='{{ author }}',
    author_email='{{ email }}',
    license='{{ license }}',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],
    keywords='{{ description }}',
    packages=[
        '{{ name }}',
        '{{ name }}.common',
        '{{ name }}.simentities',
    ],
    install_requires=[
        'vspk=={{ version }}',
        'flask-restful'
    ],
    python_requires='>=2.6, <3',
    entry_points={
        'console_scripts': [
            '{{ cli_name }} = {{ name }}.shell:main'
        ]
    }
)
