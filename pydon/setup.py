# -*- coding: utf-8 -*-

#############################################################################
#swpydonhive.py

#Part of the Pydon package
#interfacing with the Sense/Stage MiniBees and Sense/World DataNetwork
#For more information: http://docs.sensestage.eu

#created by Marije Baalman (c)2009-13


 #This program is free software; you can redistribute it and/or modify
 #it under the terms of the GNU General Public License as published by
 #the Free Software Foundation; either version 3 of the License, or
 #(at your option) any later version.

 #This program is distributed in the hope that it will be useful,
 #but WITHOUT ANY WARRANTY; without even the implied warranty of
 #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #GNU General Public License for more details.

 #You should have received a copy of the GNU General Public License
 #along with this program; if not, write to the Free Software
 #Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

#############################################################################


from setuptools import setup, find_packages

setup(name='pydon',
      version='0.32',
      description='Python packages for the Sense/Stage DataNetwork',
      long_description="""The Sense/Stage DataNetwork can be used to communicate between programs,
      such as SuperCollider, Max/MSP, PureData, Processing, C++ and Python, as well as to communicate
      to the wireless Sense/Stage MiniBees. This package provides the python client for the datanetwork,
      as well as the bridge between the datanetwork and the MiniBee network, as well as an osc sending
      application as a simple bridge to the MiniBee network""",
      scripts=['scripts/pydongui.py','scripts/pydoncli.py'],
      author='Marije Baalman',
      author_email='sensestage@nescivi.nl',
      url='http://www.sensestage.eu',
      license='GNU Lesser General Public License',
      keywords=['XBee', 'OpenSoundControl', 'OSC', 'SenseStage', 'DataNetwork', 'MiniBee'],
      py_modules=['pydon'],
      packages=find_packages(),
      install_requires=[
         #'pyOSC>=0.3',
         'pyserial>=2.6',
         #'xbee>=2.0.1'
    ]
)
