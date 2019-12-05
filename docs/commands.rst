.. ############################################################################
.. File  : h5sh/docs/commands.rst
.. ############################################################################

********
Commands
********

These are the available commands and descriptions inside the h5sh package
grouped roughly into categories.

Navigation
==========

cd
--

.. argparse::
   :module: h5sh.commands.registry
   :func: get_parser_cd

ls
--

.. argparse::
   :module: h5sh.commands.registry
   :func: get_parser_ls

pwd
---

Print the path to the current HDF5 group.

l
-

Alias for ``ls -l``.

up[p[...]]
----------

Shorthand for ``cd ..[/..[...]]`` to traverse upward in the directory
hierarchy. For example, ``uppp`` is a more typing-friendly equivalent to ``cd
../../..``.


Query
=====

attr
----

.. argparse::
   :module: h5sh.commands.registry
   :func: get_parser_attr

dump
----

.. argparse::
   :module: h5sh.commands.registry
   :func: get_parser_dump



System
======

In addition to the system "commands", you can use ``control-C`` to clear the
current command line and ``control-D`` to exit h5sh.

exit
----

Exits the h5sh shell.

help
----

Lists all available commands.

filename
--------

Print the name of the file being examined.

.. ############################################################################
.. end of h5sh/docs/commands.rst
.. ############################################################################
