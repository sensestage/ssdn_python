#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, optparse
import optparse_gui

from pydon import lmpydonhive
from pydon import swpydonhive
from pydon import minihiveosc
from pydon import minihivejunxion

# main program:
if __name__ == "__main__":

  if 1 == len( sys.argv ):
    option_parser_class = optparse_gui.OptionParser
  else:
    option_parser_class = optparse.OptionParser

  parser = option_parser_class(description='MetaPydonHive - Create a client to communicate with the minibee network.')
  
  parser.add_option("-P", "--program", dest="program",
                      choices = ['datanetwork', 'osc', 'libmapper', 'junxion' ],
                      help="Which program/infrastructure do you want to use?")
  
  parser.add_option('-s','--serial', action='store',type="string",dest="serial",default="/dev/ttyUSB0",
		  help='the serial port [default:%s]'% '/dev/ttyUSB0')
		  
  parser.add_option('-a','--apimode', action='store_true', dest="apimode",default=False,
		  help='use API mode for communication with the minibees [default:%s]'% False)
		  
  parser.add_option('-v','--verbose', action='store_true', dest="verbose",default=False,
		  help='verbose printing [default:%i]'% False)
		  
  parser.add_option('-c','--config', action='store', type="string", dest="config",default="pydon/configs/hiveconfig.xml",
		  help='the name of the configuration file for the minibees [default:%s]'% 'pydon/configs/hiveconfig.xml')

  #specific for datanetwork, libmapper:
  parser.add_option('-n','--name', action='store', type="string", dest="name",default="pydonhive",
		  help='the name of the client in the datanetwork [default:%s] (needed for datanetwork or libmapper)'% "pydonhive" )


  parser.add_option('-b','--baudrate', action='store',type=int,dest="baudrate",default=57600,
		  help='the serial port [default:%i]'% 57600)
  parser.add_option('-m','--nr_of_minibees', type=int, action='store',dest="minibees",default=20,
		  help='the number of minibees in the network [default:%i]'% 20)
  parser.add_option('-o','--minibee_offset', type=int, action='store',dest="mboffset",default=1,
		  help='the offset of the number range for the minibees in the network [default:%i]'% 1)
  parser.add_option('-d','--host_ip', action='store',type="string", dest="host",default="127.0.0.1",
		  help='the ip address of the datanetwork host [default:%s]'% "127.0.0.1")

  #specific for osc or junxion
  parser.add_option('-t','--host_port', type=int, action='store',dest="hport",default=57120,
		  help='the port on which the application that has to receive the OSC messages will listen [default:%i] (needed for osc or junxion)'% 57120 )

  parser.add_option('-i','--ip', type="string", action='store',dest="ip",default="0.0.0.0",
		  help='the ip on which the client will listen [default:%s]'% "0.0.0.0" )
  parser.add_option('-p','--port', type=int, action='store',dest="port",default=57600,
		  help='the port on which the client will listen [default:%i]'% 57600 )

  (options,args) = parser.parse_args()
  #print args.accumulate(args.integers)
  #print options
  #print args
  print( "--------------------------------------------------------------------------------------" )
  print( "MetaPydonHive - a universal client to communicate with the minibee network." )
  print( " --- to find out more about the startup options start with \'metapydonhive.py -h\'" )
  print( " --- The client has been started with these options:" )
  print( options )
  print( "--------------------------------------------------------------------------------------" )
  
  if options.program == 'datanetwork':
    swhive = swpydonhive.SWPydonHive( options.host, options.port, options.ip, options.name, options.minibees, options.serial, options.baudrate, options.config, [options.mboffset,options.minibees], options.verbose, options.apimode )
    swhive.start()
  elif options.program == 'osc':
    swhive = minihiveosc.SWMiniHiveOSC( options.host, options.hport, options.ip, options.port, options.minibees, options.serial, options.baudrate, options.config, [1,options.minibees], options.verbose, options.apimode )
    print( "Created OSC listener at (%s,%i) and OSC sender to (%s,%i) and opened serial port at %s. Now waiting for messages."%(options.ip, options.port, options.host, options.hport, options.serial ) )
    swhive.start()
  elif options.program == 'junxion':
    swhive = minihivejunxion.SWMiniHiveJunxion( options.host, options.hport, options.ip, options.port, options.minibees, options.serial, options.baudrate, options.config, [1,options.minibees], options.verbose, options.apimode )
    print( "Created OSC listener at (%s,%i) and OSC sender to (%s,%i) and opened serial port at %s. Now waiting for messages."%(options.ip, options.port, options.host, options.hport, options.serial ) )
    swhive.start()
  elif options.program == 'libmapper':
    lmhive = lmpydonhive.LMPydonHive( options.host, options.port, options.ip, options.name, options.minibees, options.serial, options.baudrate, options.config, [options.mboffset,options.minibees], options.verbose, options.apimode )
    lmhive.start()
