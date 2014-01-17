#! /usr/bin/env python

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


import os
import sys
import logging
import logging.handlers as handlers

from optparse import OptionParser


from Tkinter import INSERT, LEFT


#def customEmit(self, record):
    ## Monkey patch Emit function to avoid new lines between records
    #try:
        #msg = self.format(record)
        #if not hasattr(types, "UnicodeType"): #if no unicode support...
            #self.stream.write(msg)
        #else:
            #try:
                #if getattr(self.stream, 'encoding', None) is not None:
                    #self.stream.write(msg.encode(self.stream.encoding))
                #else:
                    #self.stream.write(msg)
            #except UnicodeError:
                #self.stream.write(msg.encode("UTF-8"))
        #self.flush()
    #except (KeyboardInterrupt, SystemExit):
        #raise
    #except:
        #self.handleError(record)

#class NoNewLineLogHandler(handlers.RotatingFileHandler):
    #def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):

        ## Monkey patch 'emit' method
        #setattr(logging.StreamHandler, logging.StreamHandler.emit.__name__, customEmit)

        #handlers.RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay )

class WidgetLogger(logging.Handler):
    def __init__(self, widget):
      logging.Handler.__init__(self)
      self.widget = widget
      self.widget.mark_set("sentinel", INSERT)
      self.widget.mark_gravity("sentinel", LEFT)
      #print widget
    
    def emit(self, record):
      r = self.format( record )
      #print( r )
      self.acquire()
      # Append message (record) to the widget
      self.widget.insert(INSERT, r )
      self.widget.mark_set(INSERT, "%d.%d" % (0,0) )
      #self.widget.insert(o, r )
      self.release()


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
	hdlr2 = handlers.RotatingFileHandler(logfile, maxBytes=5242880, backupCount=20)  #max 5 megabytes per file
	#hdlr2 = logging.FileHandler(logfile)
	#hdlr2.setFormatter(formatter)
	self.logger.addHandler(hdlr2)
	
    def addWidgetHandler( self, whdlr):
      #formatter = logging.Formatter('%(message)s')
      #whdlr.setFormatter(formatter)
      self.logger.addHandler( whdlr )
#      print whdlr

    def removeWidgetHandler(self,  whdlr ):
        self.logger.removeHandler( whdlr )

    def write(self, msg, level=logging.INFO):
        self.logger.log(level, msg)

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    # Setup command line options
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("-l", "--logdir", dest="logdir", default=".", help="log DIRECTORY (default ./)")
    parser.add_option("-n", "--logname", dest="logname", default="pydon.log", help="log name (default pydon)")
    parser.add_option("-v", "--loglevel", dest="loglevel", default="debug", help="logging level (debug, info, error)")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", help="do not log to console")
    parser.add_option("-c", "--clean", dest="clean", action="store_true", default=False, help="remove old log file")

    # Process command line options
    (options, args) = parser.parse_args(argv)

    # Setup logger format and output locations
    #logger = initialize_logging(options)

    # Examples
    #logger.error("This is an error message.")
    #logger.info("This is an info message.")
    #logger.debug("This is a debug message.")
   
    #logging.basicConfig(level=logging.DEBUG, filename='mylog.log')

# Redirect stdout and stderr
    logfile = LogFile( options, 'stdoutAndErr')
    sys.stdout = logfile
    sys.stderr = logfile

    for i in range(50):
      print 'this should to write to the log file'

if __name__ == "__main__":
    sys.exit(main())
