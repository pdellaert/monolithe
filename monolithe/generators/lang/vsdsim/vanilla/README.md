# Nuage Networks VSD API Simulator

The Nuage Networks VSD API Simulator (nuage-vsd-sim) is a tool that mimics the Nuage Networks VSD API in a very basic form.

It is meant to be used for testing the initial integration if you are creating a tool that will make REST API calls to the Nuage Networks VSD. 

## Functionality

The nuage-vsd-sim is a VSD API simulator and does not contain any of the VSD backend logic. It is meant to test getting, creating, updating and deleting entities in the VSD API to see if your basic HTTP REST API calls work properly and handle the return values properly.

It was developed as a tool to test basic integration of the Nuage VSPK Ansible module and is well suited for any similar purpose. For instance, if you are creating a new library to communicate with the VSD API, this simulator can be used in your test environment.

### Supported methods

The nuage-vsd-sim supports all HTTP REST API methods (GET, POST, PUT and DELETE) for all existing entities in the Nuage VSD API.

### Supported VSD Entities

As the nuage-vsd-sim is generated from the Nuage VSD API Specificatoins, it supports all the VSD API entities. 

### Caveats

* No persistent database: On restart of the nuage-vsd-sim, it will reset its database
* Only direct parent-child relationships. Example: If you create a Subnet in a Zone of a Domain, in the actual API, you are able to find that subnet by getting all subnet children directly from the Domain. In nuage-vsd-sim, that relationship is not available. Getting all subnets of a Domain can only be done by first getting all Zones, and for each Zone, getting all Subnets.
* No backend logic any automated activity of VSD is not simulated.. Examlple: In the real VSD API, when an Enterprise is created, automatically a few Groups (user groups for permissions) are created, in nuage-vsd-sim, this will not happen.
* No backend logic also implies that the Job concept does not work on the nuage-vsd-sim
* No support for HTTPS

## Installation

### With pip

The nuage-vsd-sim can be installed by using `pip`, using the following command:
```
pip install nuage-vsd-sim
```

### With Docker

The nuage-vsd-sim can also be run as a Docker container, for each Nuage release, a new image will be provided in the `pdellaert/nuage-vsd-sim` Docker Hub repository. 

## Usage

### Running locally

After installing using pip, you can run the `nuage-vsd-sim` command and the nuage-vsd-sim will run in the forground. 

#### Default configuration

When running the nuage-vsd-sim without any option and no configuration file, the nuage-vsd-sim will run with the log level set to `WARNING` and log everything to the console. It will also listen on `http://0.0.0.0:5000`.

#### Options

```
$ nuage-vsd-sim -h
usage: nuage-vsd-sim [-h] [-c CONFIG_FILE] [-p PORT]
                     [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

A sample Nuage VSD API simulator.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Configuration file to use, if not specified ~/.nuage-
                        vsd-sim/config.ini is used, it that does not exist,
                        /etc/nuage-vsd-sim/config.ini is used.
  -p PORT, --port PORT  Port to listen on
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Loglevel, supported values are DEBUG, INFO, WARNING,
                        ERROR, CRITICAL.
```

### Running as a Docker container

For running the nuage-vsd-sim as a container, the command to run the container is:
```
docker run --rm -d -p 5000:5000 pdellaert/nuage-vsd-sim
```

This will run the nuage-vsd-sim with the basic configuration as described above and forward the docker host port 5000 to port 5000 on the nuage-vsd-sim container. 

You can run the container with the different options to run nuage-vsd-sim with a different log level or a different port, for instance:
```
docker run --rm -d -p 8080:8080 pdellaert/nuage-vsd-sim -l DEBUG -p 8080
```

### Accessing the simulator

To make API calls, as the base URL, use `http://ip-to-sim:sim-port` and use the `v5_0` API endpoint. This means that the base URL for API calls is `http://ip-to-sim:sim-port/nuage/v5_0/`. 

### Data overview

If you browse to `http://ip-to-sim:sim-port`, you will get a JSON output of the nuage-vsd-sim internal data. This can provide insight in what is present in the VSD and what direct parent-child relationship are available.
