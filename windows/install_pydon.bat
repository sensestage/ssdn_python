cd %~dp0

cd ssdn_python-master

echo "installing pyserial"
cd pyserial_leben
python.exe setup.py install
cd ..

echo "installing xbee"
cd XBee-2.0.1
python.exe setup.py install
cd ..

echo "installing pyosc"
cd pyosc
python.exe setup.py install
cd ..


echo "installing pydon"
cd pydon
python.exe setup.py install
cd ..

echo "done installing"
