===============
keystone-import
===============

---------------------------
Keystone Management Utility
---------------------------

:Author: keystone@lists.launchpad.net
:Date:   2011-10-31
:Copyright: OpenStack LLC
:Version: 0.1.2
:Manual section: 1
:Manual group: cloud computing

SYNOPSIS
========

  keystone-import [options] filename

DESCRIPTION
===========

keystone-import takes a file of commands written in the same format as using
:doc:`keystone-manage` and imports that data into Keystone. It is intended to
import users, tenants, and EC2 credentials from nova into keystone.

USAGE
=====

 ``keystone-import [options] filename``

Common Options:
^^^^^^^^^^^^^^^
   --version                     show program's version number and exit
   -h, --help                    show this help message and exit
   -v, --verbose                 Print more verbose output
   -d, --debug                   Print debugging output to console
   -c PATH, --config-file=PATH   Path to the config file to use. When not
                                 specified (the default), we generally look at
                                 the first argument specified to be a config
                                 file, and if that is also missing, we search
                                 standard directories for a config file.
   -p BIND_PORT, --port=BIND_PORT, --bind-port=BIND_PORT
                                 specifies port to listen on (default is 5000)
   --host=BIND_HOST, --bind-host=BIND_HOST
                                 specifies host address to listen on (default
                                 is all or 0.0.0.0)
   -t, --trace-calls             Turns on call tracing for troubleshooting
   -a PORT, --admin-port=PORT    Specifies port for Admin API to listen on
                                 (default is 35357)

Logging Options:
^^^^^^^^^^^^^^^^

The following configuration options are specific to logging
functionality for this program.

   --log-config=PATH             If this option is specified, the logging
                                 configuration file specified is used and
                                 overrides any other logging options specified.
                                 Please see the Python logging module
                                 documentation for details on logging
                                 configuration files.
   --log-date-format=FORMAT      Format string for %(asctime)s in log records.
                                 Default: %Y-%m-%d %H:%M:%S
   --log-file=PATH               (Optional) Name of log file to output to. If
                                 not set, logging will go to stdout.
   --log-dir=LOG_DIR             (Optional) The directory to keep log files in
                                 (will be prepended to --logfile)

FILES
=====

None

SEE ALSO
========

* `Keystone <http://github.com/openstack/keystone>`__

SOURCE
======

* Keystone is sourced in GitHub `Keystone <http://github.com/openstack/keystone>`__
* Keystone bugs are managed at Launchpad `Launchpad Keystone <https://bugs.launchpad.net/keystone>`__
