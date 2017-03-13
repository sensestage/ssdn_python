==========
Installing
==========

INSTALLATION

On Linux and OSX you should be able to just execute the installation.sh script, so open a terminal, navigate to the folder where you put the pydon download, and execute:
    $ ./installation.sh
You may need to do this as the superuser (root), which on most systems can be done with:
    $ sudo ./installation.sh
    

You need `python2` to run the script, NOT `python3`.

For Windows, you will have to do this manually.


See [Sense/Stage Documentation](https://docs.sensestage.eu/minibee/install-the-hive-software.html) for a more complete guide on installation.



==========


(
links for getting to a Windows installer, still on the TODO list
* http://cyrille.rossant.net/create-a-standalone-windows-installer-for-your-python-application/
* http://docs.python-guide.org/en/latest/starting/install/win/
* http://docs.python.org/2/distutils/builtdist.html
)


The instructions below are for more detailed steps, if the installation script is not working.

==========

Dependencies are:
* python2 (version 2.6 or higher; not python3) - e.g. http://www.python.org/download/releases/2.7.1/
* pyserial (version 2.6 with mods from Jakob Leben) - https://github.com/jleben/python-serial/ (included in the packaged version)
* pyOSC - http://gitorious.org/pyosc (checkout included in the packaged version)
* python-xbee-api (version 2.0.1 or higher) - (included in the packaged version)
* python libmapper, see: http://www.idmil.org/software/libmapper/downloads ; will be gracefully skipped if not needed

To use the XBee Xplorer coordinator board, you will also need an FTDI driver for your platform: http://www.ftdichip.com/Drivers/VCP.htm

### python

check which version you have:

    $ python --version
    
If it is lower than 2.6 you will need to get a version higher than 2.6, but not above 3.

(make sure Python is in your path (esp. for Windows!))

Install the dependencies:

###pyOSC :

extract archive and:

    $ cd pyosc
    $ sudo python setup.py install

Go back to the main folder:

    $ cd ..

### pyserial :

extract archive and:

    $ cd python-serial
    $ sudo python setup.py install

Go back to the main folder:

    $ cd ..

### XBee-2.0.1 :

extract archive and:

    $ cd XBee-2.0.1
    $ sudo python setup.py install

Go back to the main folder:

    $ cd ..

### pydon:

    $ cd pydon
    $ sudo python setup.py install

Go back to the main folder:

    $ cd ..


-------------------------------------------------------------------  
Start the GUI interface:

    $ pydongui.py

will pop up a gui where you can set the options; the default options are saved to a file named `pydondefaults.ini`, so that next time you open the program, you'll have the same defaults

Now you can choose which kind of client to use:
  - datanetwork: integrate with the SenseWorld DataNetwork
  - libmapper: integrate with the libmapper world (from IDMIL)
  - osc: send osc messages to a certain destination (MiniHiveOSC)
  - junXion: send osc messages that STEIM's JunXion can deal with

Serial port:
`/dev/ttyUSB0` is the address of your serial port, it will be different on a mac (something like: `/dev/tty-ASSFADF0002332`), you can select it from a dropdown menu

-------------------------------------------------------------------
Command line start:

    $ pydoncli.py -h
  this will print the help

    $ pydoncli.py
    
  will take the defaults found in the `pydondefaults.ini` file in the same folder, settings that need to be changed can be changed with the command line arguments

