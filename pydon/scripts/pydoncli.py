#! /usr/bin/env python2
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

from pydon import metapydonhive, swpydonhive, minihiveosc, minihivejunxion
#try:
  #from pydon import lmpydonhive
  ##from lmpydonhive import *
#except:
  #pydon_have_libmapper = False
  ##print( "libmapper not available" )
  
import os
import sys
import logging
import logging.handlers as handlers


class LogFile(object):
    """File-like object to log text using the `logging` module."""

    def __init__(self, options, name=None):
        self.logger = logging.getLogger(name)
	#formatter = logging.Formatter('%(asctime)s %(levelname)s\t%(message)s')
	#formatter = logging.Formatter('%(asctime)s %(levelname)s\t%(message)s')
	level = logging.__dict__.get(options.loglevel.upper(),logging.DEBUG)
	self.logger.setLevel(level)
	 # Output logging information to screen
	if not options.quiet:
	  hdlr = logging.StreamHandler(sys.stderr)
	  #hdlr.setFormatter(formatter)
	  self.logger.addHandler(hdlr)

	# Output logging information to file
	logfile = os.path.join(options.logdir, options.logname )
	if options.clean and os.path.isfile(logfile):
	    os.remove(logfile)
	hdlr2 = handlers.RotatingFileHandler(logfile, maxBytes=5242880, backupCount=5)  #max 5 megabytes per file
	#hdlr2 = logging.FileHandler(logfile)
	#hdlr2.setFormatter(formatter)
	self.logger.addHandler(hdlr2)

    def write(self, msg, level=logging.INFO):
        self.logger.log(level, msg)

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()

    
#mpd = pydon.metapydonhive.MetaPydonHive()
mpd = metapydonhive.MetaPydonHive()
options = mpd.readOptions()

logfile = LogFile( options, 'stdoutAndErr')
sys.stdout = logfile
sys.stderr = logfile

mpd.writeOptions()
mpd.startHive()
