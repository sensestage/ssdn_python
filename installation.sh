#!/bin/sh

tar xzvf pyosc.tar.gz
cd pyosc
sudo python setup.py install
cd ..

tar xzvf XBee-2.0.1.tar.gz
cd XBee-2.0.1
sudo python setup.py install
cd ..

tar xzvf optparse_gui-0.2.tar.gz
cd optparse_gui-0.2
sudo python setup.py install
cd ..

cd pydon
sudo python setup.py install