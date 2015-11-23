#!/bin/sh

tar xzvf pyosc.tar.gz
cd pyosc
python setup.py install
cd ..

mkdir pyserial
tar xzvf pyserial-sensestage.tar.gz -C pyserial
cd pyserial
python setup.py install
cd ..

tar xzvf XBee-2.0.1.tar.gz
cd XBee-2.0.1
python setup.py install
cd ..

# tar xzvf optparse_gui-0.2.tar.gz
# cd optparse_gui-0.2
# sudo python setup.py install
# cd ..

cd pydon
python setup.py install
cd ..
