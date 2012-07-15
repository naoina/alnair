Alnair
======

Alnair is a simple system configuration framework.
And also are intended to be used in conjunction with the Fabric (https://github.com/fabric/fabric).

Requirement
-----------

- Python 2.6 and later (but does not work in 3.x)

Installation
------------

from pypi::

   # using pip
   % pip install -U alnair

   # or using easy_install
   % easy_install -U alnair

from source::

   % python setup.py install

Basic usage
-----------

First, generate the recipes template set by following command::

   % alnair generate template archlinux

In this example, distribution name using ``archlinux``.
``recipes/archlinux/common.py`` directories and file are created to current directory by this command.
Also ``"g"`` as an alias for the `generate` command has been defined.
The following command is same meaning as above::

   % alnair g template archlinux

Next, edit `install_command` variable in ``common.py`` for the target distribution::

   # common.py
   install_command = 'pacman -Sy'

Next, generate recipe template for package setup by following command::

   % alnair g recipe python

``python.py`` file is created on ``recipes/archlinux/`` directory by this command.
In fact, directories where you want to create the files are ``recipes/\*/``.

Finally, edit ``python.py`` for more settings if necessary and setup to the server by following command::

   % alnair setup archlinux python

Using as a library
------------------

You can use the following code instead of `alnair setup archlinux python` command::

   from alnair import Distribution

   distname = 'archlinux'
   with Distribution(distname) as dist:
       dist.setup('python')

For more documentation, read the sources or please wait while the document is being prepared.
