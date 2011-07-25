# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(name='Pydon',
      version='0.6',
      description='Python packages for the Sense/Stage DataNetwork',
      author='Marije Baalman',
      author_email='sensestage@nescivi.nl',
      url='http://www.sensestage.eu',
      packages=find_packages(),
      install_requires=[
         'PyOSC>=0.3',
         'pyserial>=2.5'
    ]
)