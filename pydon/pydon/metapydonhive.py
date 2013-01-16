#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import optparse
try:
  import optparse_gui
  haveGui = True
  #import wx
  #import thread
  #from wx import *
except:
  haveGui = False
import ConfigParser

programchoices = ['datanetwork', 'osc', 'junxion' ]

try:
  import lmpydonhive
  programchoices.append( 'libmapper' )
  haveLibmapper = True
except:
  haveLibmapper = False

import swpydonhive
import minihiveosc
import minihivejunxion

#if haveGui:

  #class MainFrame(wx.Frame):
    #def __init__(self, parent, id, title, size, pos, style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE):
      #wx.Frame.__init__(self, parent, id, title, size, pos, style)
    
      #heading = wx.StaticText(self, -1, 'Communication with MiniBee network is running', (100, 15))

      #MsgBtn = wx.Button(self, -1, label="EXIT")
      #MsgBtn.Bind(wx.EVT_BUTTON, self.OnMsgBtn )

      ## Bind close event here
      #self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
      #self.Show(True)
        
    #def setHive( self, hiv ):
      #self.hive = hiv
      
    #def OnStart( self, evt ):
      #print( "starting thread ")
      #self.thread = threading.Thread(target=self.HiveThread)
      #self.thread.setDaemon(1)
      #self.alive.set()
      #self.thread.start()

    #def HiveThread( self ):
      #self.hive.start()

    ##OnCloseWindow is executed when EVT_CLOSE is received
    #def OnCloseWindow(self, evt):
      #self.Destroy()
      #if self.hive != None:
	#self.hive.exit()
      ##sys.exit()
      ##raise SystemExit
      ##print 'OnCloseWindow() destroyed'

    #def OnMsgBtn(self, event=None):
      #"""Bring up a wx.MessageDialog with a useless message."""
      #self.Close()

#def hive_in_thread_function( swhive ):
  #global swhive
  #swhive.start()

class MetaPydonHive:
  
  def __init__(self):
    print( "created metapydonhive" )
    
  def readOptions( self ):
    defaults = {'program': 'datanetwork', 'serial': '/dev/ttyUSB0', 'apimode': 'True', 'verbose': 'False', 'logdata': 'False', 'config': "configs/example_hiveconfig.xml", 'name': "pydonhive", "port": "57600", "host": "127.0.0.1", 'ip': "0.0.0.0", 'hport': "57120", 'minibees': "20", 'mboffset': "1", 'baudrate': "57600", 'ignore': 'False', 'xbeeerror': 'False', 'logname': 'pydon.log', 'loglevel': "debug" }
    
    configParser = ConfigParser.SafeConfigParser( defaults )
    configParser.read( "pydondefaults.ini" )
    if not configParser.has_section( 'osc' ):
      configParser.add_section( 'osc' )
    if not configParser.has_section( 'serial' ):
      configParser.add_section( 'serial' )
    if not configParser.has_section( 'hive' ):
      configParser.add_section( 'hive' )
    if not configParser.has_section( 'program' ):
      configParser.add_section( 'program' )
    
    option_parser_class = optparse.OptionParser
    
    parser = option_parser_class(description='MetaPydonHive - Create a client to communicate with the minibee network.')

    parser.add_option( "-P", "--program", 
			help='Which program/infrastructure do you want to use? options: datanetwork, osc, libmapper, junxion',
			dest="program",
			default = configParser.get( 'program', 'program' ),
			#group="program", option = "program",
			#choices = ['datanetwork', 'osc', 'libmapper', 'junxion' ],
			choices = programchoices
			)
    
    parser.add_option('-s','--serial', action='store',type="string",dest="serial",
		    default = configParser.get( 'serial', 'serial' ),
		    #group="serial", option = "serial",
		    help='the serial port [default:%s]'% '/dev/ttyUSB0')
		    
    parser.add_option('-a','--apimode', action='store_true', dest="apimode", 
		    #group="serial", option = "apimode",
		    #default=True,
		    default = configParser.get( 'serial', 'apimode' ),
		    help='use API mode for communication with the minibees [default:%s]'% False)
		    
    parser.add_option('-v','--verbose', action='store_true', dest="verbose",
		    #default=False, 
		    default = configParser.get( 'program', 'verbose' ),
		    #group="program", option="verbose",
		    help='verbose printing [default:%s]'% False)
    #parser.add_option('-q','--quiet', action='store_false', dest="verbose")

    parser.add_option('-u','--ignore-unknown', action='store_true', dest="ignore",
		    #default=False, 
		    default = configParser.get( 'hive', 'ignore' ),
		    #group="program", option="verbose",
		    help='ignore unknown minibees [default:%s]'% False)
    #parser.add_option('-q','--quiet', action='store_false', dest="verbose")

    parser.add_option('-x','--check-for-xbee-error', action='store_true', dest="xbeeerror",
		    #default=False, 
		    default = configParser.get( 'hive', 'xbeeerror' ),
		    #group="program", option="verbose",
		    help='check whether xbee-error occurred [default:%s]'% False)
    #parser.add_option('-q','--quiet', action='store_false', dest="verbose")

    parser.add_option('-l','--logdata', action='store_true', dest="logdata",
		    #default=False, 
		    default = configParser.get( 'program', 'logdata' ),
		    #group="program", option="verbose",
		    help='log data to file [default:%s]'% False)
    #parser.add_option('-q','--quiet', action='store_false', dest="verbose")

    parser.add_option('-c','--config', action='store', type="string", dest="config",
		    #default="pydon/configs/hiveconfig.xml",
		    default = configParser.get( 'hive', 'config' ),
		    #group="program", option="hiveconfig", 
		    help='the name of the configuration file for the minibees [default:%s]'% 'pydon/configs/hiveconfig.xml')

    #specific for datanetwork, libmapper:
    parser.add_option('-n','--name', action='store', type="string", dest="name",
		    #default="pydonhive", 
		    default = configParser.get( 'osc', 'name' ),
		    #group="osc", option="name",
		    help='the name of the client in the datanetwork [default:%s] (needed for datanetwork or libmapper)'% "pydonhive" )


    parser.add_option('-b','--baudrate', action='store',type=int,dest="baudrate",
		    #default=57600,
		    default = configParser.get( 'serial', 'baudrate' ),
		    #group="serial", option="baudrate",
		    help='the serial port [default:%i]'% 57600)
    parser.add_option('-m','--nr_of_minibees', type=int, action='store',dest="minibees",
		    #default=20, 
		    default = configParser.get( 'hive', 'minibees' ),
		    #group="program", option="minibees",
		    help='the number of minibees in the network [default:%i]'% 20)
    parser.add_option('-o','--minibee_offset', type=int, action='store',dest="mboffset",
		    default = configParser.get( 'hive', 'mboffset' ),
		    #group="program", option="mboffset",
		    help='the offset of the number range for the minibees in the network [default:%i]'% 1)
    parser.add_option('-d','--host_ip', action='store',type="string", dest="host",
		    #default="127.0.0.1",
		    default = configParser.get( 'osc', 'host' ),
		    #group="osc", option="hostip",
		    help='the ip address of the datanetwork host [default:%s]'% "127.0.0.1")

    #specific for osc or junxion
    parser.add_option('-t','--host_port', type=int, action='store',dest="hport",
		    #default=57120,
		    default = configParser.get( 'osc', 'hport' ),
		    #group="osc", option="hostport",
		    help='the port on which the application that has to receive the OSC messages will listen [default:%i] (needed for osc or junxion)'% 57120 )

    parser.add_option('-i','--ip', type="string", action='store',dest="ip",
		    #default="0.0.0.0",
		    default = configParser.get( 'osc', 'ip' ),
		    #group="osc", option="myip",
		    help='the ip on which the client will listen [default:%s]'% "0.0.0.0" )
    parser.add_option('-p','--port', type=int, action='store',dest="port",
		    #default=57600,
		    default = configParser.get( 'osc', 'port' ),
		    #group="osc", option="myport",
		    help='the port on which the client will listen [default:%i]'% 57600 )

    parser.add_option("-N", "--logname", dest="logname", default="pydon.log", help="log name (default pydon)")
    parser.add_option("-V", "--loglevel", dest="loglevel", default="debug", help="logging level (debug, info, error)")
    parser.add_option("-Q", "--quiet", action="store_true", dest="quiet", help="do not log to console")
    parser.add_option("-L", "--logdir", dest="logdir", default=".", help="log DIRECTORY (default ./)")
    parser.add_option("-C", "--clean", dest="clean", action="store_true", default=False, help="remove old log file")

    #cfgparser.add_optparse_help_option( parser )
    
    (self.options,args) = parser.parse_args( )
    
    
    return self.options
    
    
  def writeOptions( self ):
    
    self.option_dict = vars(self.options)
    
    config = ConfigParser.RawConfigParser()
    config.add_section( 'osc' )
    config.add_section( 'serial' )
    config.add_section( 'hive' )
    config.add_section( 'program' )

    for key in [ 'mboffset', 'minibees', 'config', 'ignore', 'xbeeerror' ]:
      #print key, option_dict[ key ]
      config.set( 'hive', key, self.option_dict[ key ] )

    for key in [ 'baudrate', 'serial', 'apimode' ]:
      #print key, option_dict[ key ]
      config.set( 'serial', key, self.option_dict[ key ] )

    for key in [ 'program', 'verbose', 'logdata', 'logname', 'loglevel' ]:
      #print key, option_dict[ key ]
      config.set( 'program', key, self.option_dict[ key ] )

    for key in [ 'name', 'ip', 'port', 'host', 'hport' ]:
      #print key, option_dict[ key ]
      config.set( 'osc', key, self.option_dict[ key ] )
    
    with open ('pydondefaults.ini', 'wb' ) as configfile:
      config.write( configfile )
      
  def startHive( self ):
    #if haveGui:
      #app = wx.PySimpleApp(True)
      #app = wx.PySimpleApp(False)
      #frame = MainFrame(None, -1, "MetaPydonHive", (-1,-1), (500,50))
      #app.SetOutputWindowAttributes( "MetaPydonHive Output" )

    print( "--------------------------------------------------------------------------------------" )
    print( "MetaPydonHive - a universal client to communicate with the minibee network." )
    print( " --- to find out more about the startup options start with \'metapydonhive.py -h\'" )
    print( " --- The client has been started with these options:" )
    #print( parser )
    print( self.options )
    print( "--------------------------------------------------------------------------------------" )
    
    if self.options.program == 'datanetwork':
      self.swhive = swpydonhive.SWPydonHive( self.options.host, self.options.port, self.options.ip, self.options.name, self.options.minibees, self.options.serial, self.options.baudrate, self.options.config, [self.options.mboffset,self.options.minibees], self.options.verbose, self.options.apimode, self.options.ignore, self.options.xbeeerror )
      if self.options.logdata:
	self.swhive.initializeLogger()
      #if haveGui:
	#print "start main loop"
	#frame.setHive( swhive )
	#app.MainLoop()
	#print "starting swhive"
	#swhive.start()
      #else:
      swhive.start()

    elif self.options.program == 'osc':
      self.swhive = minihiveosc.SWMiniHiveOSC( self.options.host, self.options.hport, self.options.ip, self.options.port, self.options.minibees, self.options.serial, self.options.baudrate, self.options.config, [1,self.options.minibees], self.options.verbose, self.options.apimode )
      print( "Created OSC listener at (%s,%i) and OSC sender to (%s,%i) and opened serial port at %s. Now waiting for messages."%(self.options.ip, self.options.port, self.options.host, self.options.hport, self.options.serial ) )
      #if haveGui:
	#frame.setHive( swhive )
	#print( "starting thread" )
	#thread.start_new_thread( hive_in_thread_function, (swhive) )
	#app.MainLoop()
	#print "starting swhive"      
	#swhive.start()
      #else:
      self.swhive.start()

    elif self.options.program == 'junxion':
      self.swhive = minihivejunxion.SWMiniHiveJunxion( self.options.host, self.options.hport, self.options.ip, self.options.port, self.options.minibees, self.options.serial, self.options.baudrate, self.options.config, [1,self.options.minibees], self.options.verbose, self.options.apimode )
      print( "Created OSC listener at (%s,%i) and OSC sender to (%s,%i) and opened serial port at %s. Now waiting for messages."%(self.options.ip, self.options.port, self.options.host, self.options.hport, self.options.serial ) )
      #if haveGui:
	#frame.setHive( swhive )
	#app.MainLoop()
	#swhive.start()
      #else:
      self.swhive.start()

    elif self.options.program == 'libmapper':
      if haveLibmapper:
	self.swhive = lmpydonhive.LMPydonHive( self.options.host, self.options.port, self.options.ip, self.options.name, self.options.minibees, self.options.serial, self.options.baudrate, self.options.config, [self.options.mboffset,self.options.minibees], self.options.verbose, self.options.apimode )
	#if haveGui:
	  #frame.setHive( swhive )
	  #app.MainLoop()
	  #swhive.start()
	#else:
	self.swhive.start()
      else:
	print( "libmapper is not available, please check your installation or choose another mode" )


# main program:
if __name__ == "__main__":
  
  defaults = {'program': 'datanetwork', 'serial': '/dev/ttyUSB0', 'apimode': "True", 'verbose': "False", 'logdata': "False", 'config': "configs/example_hiveconfig.xml", 'name': "pydonhive", "port": "57600", "host": "127.0.0.1", 'ip': "0.0.0.0", 'hport': "57120", 'minibees': "20", 'mboffset': "1", 'baudrate': "57600", 'ignore': "False", 'xbeeerror': "False" }
  
  configParser = ConfigParser.SafeConfigParser( defaults )
  configParser.read( "pydondefaults.ini" )
  if not configParser.has_section( 'osc' ):
    configParser.add_section( 'osc' )
  if not configParser.has_section( 'serial' ):
    configParser.add_section( 'serial' )
  if not configParser.has_section( 'hive' ):
    configParser.add_section( 'hive' )
  if not configParser.has_section( 'program' ):
    configParser.add_section( 'program' )
  
  if 1 == len( sys.argv ) and haveGui:
    option_parser_class = optparse_gui.OptionParser
  else:
    option_parser_class = optparse.OptionParser

  parser = option_parser_class(description='MetaPydonHive - Create a client to communicate with the minibee network.')

  parser.add_option( "-P", "--program", 
		      help='Which program/infrastructure do you want to use? options: datanetwork, osc, libmapper, junxion',
		      dest="program",
		      default = configParser.get( 'program', 'program' ),
		      #group="program", option = "program",
                      #choices = ['datanetwork', 'osc', 'libmapper', 'junxion' ],
                      choices = programchoices
                      )
  
  parser.add_option('-s','--serial', action='store',type="string",dest="serial",
		  default = configParser.get( 'serial', 'serial' ),
		  #group="serial", option = "serial",
		  help='the serial port [default:%s]'% '/dev/ttyUSB0')
		  
  parser.add_option('-a','--apimode', action='store_true', dest="apimode", 
		  #group="serial", option = "apimode",
		  #default=True,
		  default = configParser.get( 'serial', 'apimode' ),
		  help='use API mode for communication with the minibees [default:%s]'% False)
		  
  parser.add_option('-v','--verbose', action='store_true', dest="verbose",
		  #default=False, 
		  default = configParser.get( 'program', 'verbose' ),
		  #group="program", option="verbose",
		  help='verbose printing [default:%s]'% False)
  #parser.add_option('-q','--quiet', action='store_false', dest="verbose")

  parser.add_option('-u','--ignore-unknown', action='store_true', dest="ignore",
		  #default=False, 
		  default = configParser.get( 'hive', 'ignore' ),
		  #group="program", option="verbose",
		  help='ignore unknown minibees [default:%s]'% False)
  #parser.add_option('-q','--quiet', action='store_false', dest="verbose")

  parser.add_option('-x','--check-for-xbee-error', action='store_true', dest="xbeeerror",
		  #default=False, 
		  default = configParser.get( 'hive', 'xbeeerror' ),
		  #group="program", option="verbose",
		  help='check whether xbee-error occurred [default:%s]'% False)
  #parser.add_option('-q','--quiet', action='store_false', dest="verbose")

  parser.add_option('-l','--logdata', action='store_true', dest="logdata",
		  #default=False, 
		  default = configParser.get( 'program', 'logdata' ),
		  #group="program", option="verbose",
		  help='log data to file [default:%s]'% False)
  #parser.add_option('-q','--quiet', action='store_false', dest="verbose")

  parser.add_option('-c','--config', action='store', type="string", dest="config",
		  #default="pydon/configs/hiveconfig.xml",
		  default = configParser.get( 'hive', 'config' ),
		  #group="program", option="hiveconfig", 
		  help='the name of the configuration file for the minibees [default:%s]'% 'pydon/configs/hiveconfig.xml')

  #specific for datanetwork, libmapper:
  parser.add_option('-n','--name', action='store', type="string", dest="name",
		  #default="pydonhive", 
		  default = configParser.get( 'osc', 'name' ),
		  #group="osc", option="name",
		  help='the name of the client in the datanetwork [default:%s] (needed for datanetwork or libmapper)'% "pydonhive" )


  parser.add_option('-b','--baudrate', action='store',type=int,dest="baudrate",
		  #default=57600,
		  default = configParser.get( 'serial', 'baudrate' ),
		  #group="serial", option="baudrate",
		  help='the serial port [default:%i]'% 57600)
  parser.add_option('-m','--nr_of_minibees', type=int, action='store',dest="minibees",
		  #default=20, 
		  default = configParser.get( 'hive', 'minibees' ),
		  #group="program", option="minibees",
		  help='the number of minibees in the network [default:%i]'% 20)
  parser.add_option('-o','--minibee_offset', type=int, action='store',dest="mboffset",
		  default = configParser.get( 'hive', 'mboffset' ),
		  #group="program", option="mboffset",
		  help='the offset of the number range for the minibees in the network [default:%i]'% 1)
  parser.add_option('-d','--host_ip', action='store',type="string", dest="host",
		  #default="127.0.0.1",
		  default = configParser.get( 'osc', 'host' ),
		  #group="osc", option="hostip",
		  help='the ip address of the datanetwork host [default:%s]'% "127.0.0.1")

  #specific for osc or junxion
  parser.add_option('-t','--host_port', type=int, action='store',dest="hport",
		  #default=57120,
		  default = configParser.get( 'osc', 'hport' ),
		  #group="osc", option="hostport",
		  help='the port on which the application that has to receive the OSC messages will listen [default:%i] (needed for osc or junxion)'% 57120 )

  parser.add_option('-i','--ip', type="string", action='store',dest="ip",
		  #default="0.0.0.0",
		  default = configParser.get( 'osc', 'ip' ),
		  #group="osc", option="myip",
		  help='the ip on which the client will listen [default:%s]'% "0.0.0.0" )
  parser.add_option('-p','--port', type=int, action='store',dest="port",
		  #default=57600,
		  default = configParser.get( 'osc', 'port' ),
		  #group="osc", option="myport",
		  help='the port on which the client will listen [default:%i]'% 57600 )

  #cfgparser.add_optparse_help_option( parser )
  
  (options,args) = parser.parse_args( )
  
  option_dict = vars(options)
   
  config = ConfigParser.RawConfigParser()
  config.add_section( 'osc' )
  config.add_section( 'serial' )
  config.add_section( 'hive' )
  config.add_section( 'program' )

  for key in [ 'mboffset', 'minibees', 'config', 'ignore', 'xbeeerror' ]:
    #print key, option_dict[ key ]
    config.set( 'hive', key, option_dict[ key ] )

  for key in [ 'baudrate', 'serial', 'apimode' ]:
    #print key, option_dict[ key ]
    config.set( 'serial', key, option_dict[ key ] )

  for key in [ 'program', 'verbose', 'logdata' ]:
    #print key, option_dict[ key ]
    config.set( 'program', key, option_dict[ key ] )

  for key in [ 'name', 'ip', 'port', 'host', 'hport' ]:
    #print key, option_dict[ key ]
    config.set( 'osc', key, option_dict[ key ] )
  
  with open ('pydondefaults.ini', 'wb' ) as configfile:
    config.write( configfile )


  #if haveGui:
    #app = wx.PySimpleApp(True)
    #app = wx.PySimpleApp(False)
    #frame = MainFrame(None, -1, "MetaPydonHive", (-1,-1), (500,50))
    #app.SetOutputWindowAttributes( "MetaPydonHive Output" )

  print( "--------------------------------------------------------------------------------------" )
  print( "MetaPydonHive - a universal client to communicate with the minibee network." )
  print( " --- to find out more about the startup options start with \'metapydonhive.py -h\'" )
  print( " --- The client has been started with these options:" )
  #print( parser )
  print( options )
  print( "--------------------------------------------------------------------------------------" )
  
  if options.program == 'datanetwork':
    swhive = swpydonhive.SWPydonHive( options.host, options.port, options.ip, options.name, options.minibees, options.serial, options.baudrate, options.config, [options.mboffset,options.minibees], options.verbose, options.apimode, options.ignore, options.xbeeerror )
    if options.logdata:
      swhive.initializeLogger()
    #if haveGui:
      #print "start main loop"
      #frame.setHive( swhive )
      #app.MainLoop()
      #print "starting swhive"
      #swhive.start()
    #else:
    swhive.start()

  elif options.program == 'osc':
    swhive = minihiveosc.SWMiniHiveOSC( options.host, options.hport, options.ip, options.port, options.minibees, options.serial, options.baudrate, options.config, [1,options.minibees], options.verbose, options.apimode )
    print( "Created OSC listener at (%s,%i) and OSC sender to (%s,%i) and opened serial port at %s. Now waiting for messages."%(options.ip, options.port, options.host, options.hport, options.serial ) )
    #if haveGui:
      #frame.setHive( swhive )
      #print( "starting thread" )
      #thread.start_new_thread( hive_in_thread_function, (swhive) )
      #app.MainLoop()
      #print "starting swhive"      
      #swhive.start()
    #else:
    swhive.start()

  elif options.program == 'junxion':
    swhive = minihivejunxion.SWMiniHiveJunxion( options.host, options.hport, options.ip, options.port, options.minibees, options.serial, options.baudrate, options.config, [1,options.minibees], options.verbose, options.apimode )
    print( "Created OSC listener at (%s,%i) and OSC sender to (%s,%i) and opened serial port at %s. Now waiting for messages."%(options.ip, options.port, options.host, options.hport, options.serial ) )
    #if haveGui:
      #frame.setHive( swhive )
      #app.MainLoop()
      #swhive.start()
    #else:
    swhive.start()

  elif options.program == 'libmapper':
    if haveLibmapper:
      swhive = lmpydonhive.LMPydonHive( options.host, options.port, options.ip, options.name, options.minibees, options.serial, options.baudrate, options.config, [options.mboffset,options.minibees], options.verbose, options.apimode )
      #if haveGui:
	#frame.setHive( swhive )
	#app.MainLoop()
	#swhive.start()
      #else:
      swhive.start()
    else:
      print( "libmapper is not available, please check your installation or choose another mode" )
