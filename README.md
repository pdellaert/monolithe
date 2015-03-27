VSDK Vanilla
============

SDK Generator for Nuage Network API

Supported version:

    * Python 2.6
    * Python 2.7

Dependencies
------------

Python dependencies (see `requirements.txt` file)


Setup your Python Virtual Environment
-------------------------------------

Create your virtualenv
::

    $ virtualenv vsdk-vanilla-env

Activate your environment
::

    $ cd vsdk-vanilla-env
    $ source bin/activate
    (vsdk-vanilla-env) $


How it works
============

    (vsdk-vanilla-env) $ cd vsdk-vanilla
    (vsdk-vanilla-env) $ cd generator
    (vsdk-vanilla-env) $ vsdkgenerator -h  # Display help command

Generate a new API
------------------
This will take default sources and will create a new SDK in `codegen/{{version}}`

    (vsdk-vanilla-env) $ vsdkgenerator -u https://vsd:8443 -v 3.1
    (vsdk-vanilla-env) $ vsdkgenerator -f ~/Path/To/V3_1

Work from an existing API version
---------------------------------
This will clone the branch of the given git repository and update the SDK sources according to the VSD API.
_Note: If the branch does not exists, it will automatically create one_

    (vsdk-vanilla-env) $ vsdkgenerator -u https://vsd:8443 -v 3.1 -g https://github.com/nuagenetworks/vsdk.git


Work from an existing API version and Push
------------------------------------------
This will clone the branch of the given git repository and will push generates sources to the repository
_Note: If the branch does not exists, it will automatically create one_

    (vsdk-vanilla-env) $ vsdkgenerator -u https://vsd:8443 -v 3.1 -g https://github.com/nuagenetworks/vsdk.git --push

What to do when I have my Python SDK sources:
=============================================

You will have several options here:

* Install your SDK in development mode
It will be update everytime your SDK sources change:

    (vsdk-vanilla-env) $ cd codegen/3.0/
    (vsdk-vanilla-env) $ python setup.py develop

* Create a package and install it wherever you want
It will create a `dist` folder containing a `tar.gz` file that can be installed using `pip install vsdk.tar.gz` command:

    (vsdk-vanilla-env) $ cd codegen/3.0/
    (vsdk-vanilla-env) $ python setup.py sdist

    (your-own-env) $ pip install dist/vsdk-3.0-1.tar.gz


* Install the vsdk from your repository
It will install the vsdk from the github repository

    (your-own-env) $ pip install git+https://github.com/nuagenetworks/vsdk.git

Any Trouble ?
=============
It can happen ! Do not hesitate to send a quick email to `christophe.serafin@alcatel-lucent.com`
