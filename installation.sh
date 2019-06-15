#!/bin/sh

if [ -z "$1" ];
then MYP="python"
else MYP=$1
fi

echo "Using python executable:" $MYP
$MYP -V

ver=$($MYP -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
# echo $ver
if [ "$ver" -gt "30" ]; then
    echo "This script requires python 2.7 or greater, but not greater than python 3.0."
    echo "Your version is:"
    $MYP -V
    echo "Please try invoking the script with e.g. installation.sh python2"
    exit 1
fi
if [ "$ver" -lt "27" ]; then
    echo "This script requires python 2.7 or greater, but not greater than python 3.0"
    echo "Your version is:"
    $MYP -V
    echo "Please try invoking the script with e.g. installation.sh python2"
    exit 1
fi

tar xzvf pyosc.tar.gz
cd pyosc
$MYP setup.py install
cd ..

# # mkdir pyserial
# #tar xzvf pyserial-sensestage.tar.gz -C pyserial
tar xzvf pyserial-sensestage.tar.gz
cd pyserial
$MYP setup.py install
cd ..

tar xzvf XBee-2.0.1.tar.gz
cd XBee-2.0.1
$MYP setup.py install
cd ..

# tar xzvf optparse_gui-0.2.tar.gz
# cd optparse_gui-0.2
# sudo python setup.py install
# cd ..

cd pydon
$MYP setup.py install
cd ..
