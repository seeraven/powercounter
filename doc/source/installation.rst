Installation
============

The following installation methods are provided:

* a self-contained executable generated using PyInstaller_


Installation as the Self-Contained Executable
---------------------------------------------

Installation of the self-contained executable allows you to install
powercounter on systems even if they do not provide python themselfes.
However, the usage of powercounter is limited to the command line tool
itself, so the integration in other scripts won't be possible::

    $ wget https://github.com/seeraven/powercounter/releases/download/v1.0.0/powercounter_Ubuntu18.04_amd64
    $ mv powercounter_Ubuntu18.04_amd64 /usr/local/bin/powercounter
    $ chmod +x /usr/local/bin/powercounter


.. _PyInstaller: http://www.pyinstaller.org/
