
# Mara Mondrian

[![Build Status](https://travis-ci.org/mara/mara-mondrian.svg?branch=master)](https://travis-ci.org/mara/mara-mondrian)
[![PyPI - License](https://img.shields.io/pypi/l/mara-mondrian.svg)](https://github.com/mara/mara-mondrian/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/mara-mondrian.svg)](https://badge.fury.io/py/mara-mondrian)
[![Slack Status](https://img.shields.io/badge/slack-join_chat-white.svg?logo=slack&style=social)](https://communityinviter.com/apps/mara-users/public-invite)

A python interface for [Mondrian server](https://github.com/project-a/mondrian-server), a [Mondrian](https://en.wikipedia.org/wiki/Mondrian_OLAP_server) [XMLA](https://en.wikipedia.org/wiki/XML_for_Analysis) server combined with the [Saiku](https://www.meteorite.bi/products/saiku/) ad hoc analysis tool. Comes with

- A [Makefile](.scripts/mondrian-server.mk) for running Mondrian Server locally.

- [Mondrian schma](https://mondrian.pentaho.com/documentation/schema.php) generation from a [Mara Schema](https://github.com/mara/mara-schema) definition.

- Mondrian cache flushing.

- Saiku authentication via [Mara ACL](https://github.com/mara/mara-acl). 



&nbsp;

## Installation

To use the library directly, use pip:

```
pip install mara-mondrian
```

or
 
```
pip install git+https://github.com/mara/mara-mondrian.git
```

For an example of an integration into a flask application, have a look at the [mara example project 1](https://github.com/mara/mara-example-project-1).

&nbsp;

## Running Saiku

From within a Mara project, include [.scripts/mondrian-server.mk] in your project Makefile (as for example in [https://github.com/mara/mara-example-project-1/blob/master/Makefile](https://github.com/mara/mara-example-project-1/blob/master/Makefile)).

Then running `make run-mondrian-server` will start Saiku and the XMLA server on port 8080: 

![Saiku](docs/saiku.png)

For running mondrian server in production, please have a look at [https://github.com/project-a/mondrian-server/blob/master/README.md](https://github.com/project-a/mondrian-server/blob/master/README.md).

&nbsp;

## Mondrian schema generation

If you have a data warehouse schema defined in [Mara Schema](https://github.com/mara/mara-schema), then you can automatically create a mondrian schema file using the function `write_mondrian_schema` in [mara_mondrian/schema_generation.py](mara_mondrian/schema_generation.py).

Have a look at [https://github.com/mara/mara-example-project-1/blob/master/app/pipelines/update_frontends/__init__.py](https://github.com/mara/mara-example-project-1/blob/master/app/pipelines/update_frontends/__init__.py) for an example.

&nbsp;

## Mondrian cache flushing

With the function `flush_mondrian_cache` in [mara_mondrian/connection.py](mara_mondrian/connection.py) you can trigger a reload of the schema and a flushing of all caches in mondrian server.

This file also contains functions for making XMLA requests. 

&nbsp;

## Saiku authentication via [Mara ACL](https://github.com/mara/mara-acl)

Once you add the Saiku ACL resource in [mara_mondrian/views.py](mara_mondrian/views.py) to your project, you can control easily control which users can query which cubes:

![Saiku ACL](docs/acl.png)

In this example, users from the "Management" group can query all cubes, and users from "Marketing" only "Customers" and "Leads" (with the exception of Thomas who can also query "Order items" and "Sellers").

Please have a look at [https://github.com/project-a/mondrian-server/blob/master/README.md](https://github.com/project-a/mondrian-server/blob/master/README.md) for how to set this up.

Please make sure that the `/mondrian/saiku/authorize` endpoint is white-listed from the Mara ACL, as for example in [https://github.com/mara/mara-example-project-1/blob/master/app/ui/__init__.py](https://github.com/mara/mara-example-project-1/blob/master/app/ui/__init__.py):

```python
monkey_patch.patch(mara_acl.config.whitelisted_uris)(lambda: ['/mara-app/navigation-bar', '/mondrian/saiku/authorize'])
```

&nbsp;

The easiest way to try out Mara Mondrian is to run the [mara example project 1](https://github.com/mara/mara-example-project-1).