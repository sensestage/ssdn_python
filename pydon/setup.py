#! /usr/bin/env python
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


#from setuptools import setup, find_packages
from distutils.core import setup

files = ["pydon/*.py"]

setup(name='pydon',
      version='0.44',
      description='Python packages for the Sense/Stage DataNetwork and interaction with Sense/Stage MiniBees',
      long_description="""The Sense/Stage DataNetwork can be used to communicate between programs,
      such as SuperCollider, Max/MSP, PureData, Processing, C++ and Python, as well as to communicate
      to the wireless Sense/Stage MiniBees. This package provides the python client for the datanetwork,
      as well as the bridge between the datanetwork and the MiniBee network, as well as an osc sending
      application as a simple bridge to the MiniBee network""",
      author='Marije Baalman',
      author_email='sensestage@nescivi.nl',
      url='http://www.sensestage.eu',
      download_url='https://github.com/sensestage/ssdn_python',
      license='GNU Lesser General Public License',
      keywords=['XBee', 'OpenSoundControl', 'OSC', 'SenseStage', 'DataNetwork', 'MiniBee'],
      packages=['pydon'],
      package_data = {'pydon': files },
      scripts=['scripts/pydongui.py','scripts/pydoncli.py']
      #packages=find_packages(),
      #install_requires=[
         #'pyserial>=2.6',
    #]
)
         #'pyOSC>=0.3',
         #'xbee>=2.0.1'