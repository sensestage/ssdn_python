#! /usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################################
#metapydonhive.py

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

from pydon import pydonguifront, pydonlogger
#from pydonlogger import *

from pydon import metapydonhive, swpydonhive, minihiveosc, minihivejunxion
try:
  from pydon import lmpydonhive
  ##from lmpydonhive import *
except:
  pydon_have_libmapper = False
  ##print( "libmapper not available" )


app = pydonguifront.HiveApp()
app.openConfigMenu()
app.mainloop()
