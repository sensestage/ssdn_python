#import sys

#class Logger(object):
    #def __init__(self):
        #self.terminal = sys.stdout
        #self.log = open("log.dat", "a")

    #def write(self, message):
        #self.terminal.write(message)
        #self.log.write(message)  

#sys.stdout = Logger()

## prints "1 2" to <stdout> AND log.dat
#print "%d %d" % (1,2)

import os
import sys
import logging
import logging.handlers as handlers

from optparse import OptionParser

class LogFile(object):
    """File-like object to log text using the `logging` module."""

    def __init__(self, options, name=None):
        self.logger = logging.getLogger(name)
	formatter = logging.Formatter('%(asctime)s %(levelname)s\t%(message)s')
	level = logging.__dict__.get(options.loglevel.upper(),logging.DEBUG)
	self.logger.setLevel(level)
	 # Output logging information to screen
	if not options.quiet:
	  hdlr = logging.StreamHandler(sys.stderr)
	  hdlr.setFormatter(formatter)
	  self.logger.addHandler(hdlr)

	# Output logging information to file
	logfile = os.path.join(options.logdir, options.logname )
	#if options.clean and os.path.isfile(logfile):
	    #os.remove(logfile)
	hdlr2 = handlers.RotatingFileHandler(logfile, maxBytes=100, backupCount=5)       
	#hdlr2 = logging.FileHandler(logfile)
	hdlr2.setFormatter(formatter)
	self.logger.addHandler(hdlr2)

    def write(self, msg, level=logging.INFO):
        self.logger.log(level, msg)

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()

def initialize_logging(options):
    """ Log information based upon users options"""

    logger = logging.getLogger('project')
    formatter = logging.Formatter('%(asctime)s %(levelname)s\t%(message)s')
    level = logging.__dict__.get(options.loglevel.upper(),logging.DEBUG)
    logger.setLevel(level)

    # Output logging information to screen
    if not options.quiet:
        hdlr = logging.StreamHandler(sys.stderr)
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)

    # Output logging information to file
    logfile = os.path.join(options.logdir, "pydon.log")
    if options.clean and os.path.isfile(logfile):
        os.remove(logfile)
        
    hdlr2 = handlers.RotatingFileHandler(logfile, maxBytes=100, backupCount=5)
    hdlr2.setFormatter(formatter)
    logger.addHandler(hdlr2)

    return logger

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