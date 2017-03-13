# Getting started


Full documentation can be found here:

[Getting started with your MiniBees](https://docs.sensestage.eu/minibee/getting-started-with-sense-stage.html)



=====
XBees
=====

If you did not buy the MiniBees in a kit, you will need to configure your XBees as described on:
[https://docs.sensestage.eu/minibee/xbee-choice-and-configuration.html]()

========
MiniBees
========

These should be ready to go, unless you did not buy the MiniBees, but are using your own Arduino/XBee combination. In that case check the pages below on how to configure your setup.

* [https://docs.sensestage.eu/minibee/prepare-the-arduino-ide-for-use-with-sense-stage.html]()
* [https://docs.sensestage.eu/minibee/minibee-diy-use-your-own-arduino-and-xbee.html]()


=========
PYDONHIVE
=========
Pydonhive is a python client for the datanetwork that will talk to the MiniBees and send data to the datanetwork, or send data from the datanetwork to the MiniBees.

You start it with:

    $ pydongui.py

See also the [INSTALL](INSTALL.md) file for more detailed information.

===========
DataNetwork
===========
Install the the packages within SuperCollider

[https://docs.sensestage.eu/downloads]()

Start the Standalone, or within SuperCollider:

    x = SWDataNetwork.new.createHost;
    x.makeGui;

===========
YOUR DATANETWORK CLIENT
===========

Get the client for your environment from: [https://docs.sensestage.eu/downloads]()

To get the data from the MiniBees in your environment, you have to subscribe to the data.
If your MiniBee got id 1, e.g. in Pd or Max you would create a dn.node object that listens to id 1.

PureData:

    dn.node 1

Max:

    dn.node clientName 1


To send data to a node, you use `dn.mapnode`

    dn.mapnode 500 3 2
    
will make a node 500 with 3 slots, and tell the DataNetwork to map the data to the outputs of MiniBee with ID 2.
