cd %~dp0

cd ssdn_python-master

echo "installing pyserial"
cd pyserial-sensestage
C:\Python27\python.exe setup.py install
cd ..

echo "installing xbee"
cd XBee-2.0.1
C:\Python27\python.exe setup.py install
cd ..

echo "installing pyosc"
cd pyosc
C:\Python27\python.exe setup.py install
cd ..

echo "installing pydon"
cd pydon
C:\Python27\python.exe setup.py install
cd ..

echo "done installing"
