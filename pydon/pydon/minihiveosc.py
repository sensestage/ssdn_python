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

import optparse
try:
  import optparse_gui
  haveGui = True
except:
  haveGui = False
# from Python v2.7 on should become argparse
import sys
import time

import OSC
import threading

import pydonhive

class MiniHiveOSC(object):
  #def __init__(self, port, dnosc ):
    #ServerThread.__init__(self, port)
    #self.dnosc = dnosc
    
  def setVerbose( self, onoff ):
    self.verbose = onoff;
    self.osc.print_tracebacks = onoff
    
  def add_handlers( self ):
    
    self.osc.addMsgHandler( "/minihive/quit", self.handler_quit )
    
    self.osc.addMsgHandler( "/minihive/reset", self.handler_reset_hive )
    self.osc.addMsgHandler( "/minihive/ids/save", self.handler_saveids )

    self.osc.addMsgHandler( "/minibee/reset", self.handler_reset_minibee )
    self.osc.addMsgHandler( "/minibee/saveid", self.handler_mbsaveid )
    self.osc.addMsgHandler( "/minibee/announce", self.handler_mbannounce )

    #self.osc.addMsgHandler( "/minibee", self.handler_output )
    self.osc.addMsgHandler( "/minibee/output", self.handler_output )
    self.osc.addMsgHandler( "/minibee/custom", self.handler_custom )
    self.osc.addMsgHandler( "/minibee/run", self.handler_run )
    self.osc.addMsgHandler( "/minibee/loopback", self.handler_loopback )
    
    self.osc.addMsgHandler( "/minibee/configuration", self.handler_mbconfig )
    self.osc.addMsgHandler( "/minibee/configuration/query", self.handler_mbconfig_query )

    self.osc.addMsgHandler( "/minihive/configuration/save", self.handler_cfsave )
    self.osc.addMsgHandler( "/minihive/configuration/load", self.handler_cfload )
    
    self.osc.addMsgHandler( "/minihive/configuration/create", self.handler_config )
    self.osc.addMsgHandler( "/minihive/configuration/delete", self.handler_config_delete )    
    self.osc.addMsgHandler( "/minihive/configuration/query", self.handler_config_query )
    
    self.osc.addMsgHandler( "/minihive/configuration/short", self.handler_config_short )

    self.osc.addMsgHandler( "/minihive/configuration/pin", self.handler_configpin )
    self.osc.addMsgHandler( "/minihive/configuration/pin/query", self.handler_configpin_query )
    self.osc.addMsgHandler( "/minihive/configuration/twi", self.handler_configtwi )
    self.osc.addMsgHandler( "/minihive/configuration/twi/query", self.handler_configtwi_query )
    
    self.osc.addMsgHandler('default', self.osc.noCallback_handler)

  def call_callback( self, ctype, cid ):
    if ctype in self.callbacks:
      if cid in self.callbacks[ ctype ]:
	self.callbacks[ ctype ][ cid ]( cid )
	return
    #print ctype, cid

  #@make_method('/datanetwork/announce', 'si')
  #def announced( self, path, args, types ):

  def handler_mbsaveid( self, path, types, args, source ):    
    self.minibeeSaveID( args[0] )
    if self.verbose:
      print( "MiniBee save id:", args )

  def handler_mbannounce( self, path, types, args, source ):    
    self.minibeeAnnounce( args[0] )
    if self.verbose:
      print( "MiniBee announce:", args )

  def handler_saveids( self, path, types, args, source ):    
    self.saveIDs()
    if self.verbose:
      print( "MiniHive save ids:", args )  
  
  def handler_reset_hive( self, path, types, args, source ):
    self.reset_hive()
    print( "Reset hive:", args )

  def handler_reset_minibee( self, path, types, args, source ):
    self.reset_minibee( args[0] )
    print( "Reset minibee:", args )

  def handler_run( self, path, types, args, source ):    
    self.setRun( args[0], args[1] )
    if self.verbose:
      print( "MiniBee Run:", args )

  def handler_loopback( self, path, types, args, source ):    
    self.setLoopback( args[0], args[1] )
    if self.verbose:
      print( "MiniBee Loopback:", args )

  def handler_output( self, path, types, args, source ):    
    self.setOutput( args[0], args[1:] )
    if self.verbose:
      print( "MiniBee Output:", args )

  def handler_custom( self, path, types, args, source ):    
    self.setCustom( args[0], args[1:] )
    if self.verbose:
      print( "MiniBee Custom:", args )

  def handler_mbconfig( self, path, types, args, source ):    
    self.setMiniBeeConfiguration( args )
    if self.verbose:
      print( "MiniBee configuration:", args )

  def handler_mbconfig_query( self, path, types, args, source ):    
    self.queryMiniBeeConfiguration( args[0] )
    if self.verbose:
      print( "MiniBee configuration query:", args )

  def handler_config( self, path, types, args, source ):    
    self.setConfiguration( args[0], args[1:] )
    if self.verbose:
      print( "MiniHive configuration:", args )

  def handler_config_delete( self, path, types, args, source ):    
    self.deleteConfiguration( args[0] )
    if self.verbose:
      print( "MiniHive delete configuration:", args )

  def handler_config_short( self, path, types, args, source ):    
    self.setConfiguration( args[0], args[1:] )
    if self.verbose:
      print( "MiniHive configuration:", args )

  def handler_config_query( self, path, types, args, source ):    
    self.queryConfiguration( args[0] )
    if self.verbose:
      print( "MiniHive configuration query:", args )

  def handler_configpin( self, path, types, args, source ):    
    self.setPinConfiguration( args[0], args[1:] )
    if self.verbose:
      print( "MiniHive pin configuration:", args )

  def handler_configpin_query( self, path, types, args, source ):    
    self.queryPinConfiguration( args[0], args[1] )
    if self.verbose:
      print( "MiniHive pin configuration query:", args )

  def handler_configtwi( self, path, types, args, source ):    
    self.setTwiConfiguration( args[0], args[1:] )
    if self.verbose:
      print( "MiniHive twi configuration:", args )

  def handler_configtwi_query( self, path, types, args, source ):    
    self.queryTwiConfiguration( args[0], args[1] )
    if self.verbose:
      print( "MiniHive twi configuration query:", args )

  def handler_cfsave( self, path, types, args, source ):    
    self.saveConfiguration( args[0] )
    if self.verbose:
      print( "MiniBee save configuration:", args )

  def handler_cfload( self, path, types, args, source ):    
    self.loadConfiguration( args[0] )
    if self.verbose:
      print( "MiniBee load configuration:", args )
      
  def handler_quit( self, path, types, args, source ):    
    self.quit()
    print( "MiniHiveOSC quit:", args )     

  def fallback(self, path, args, types, src):
    print( "got unknown message '%s' from '%s'" % (path, src.get_url()) )
    for a, t in zip(args, types):
      print( "argument of type '%s': %s" % (t, a) )
      
## message sending
  def sendMessage( self, path, args ):
    msg = OSC.OSCMessage()
    msg.setAddress( path )
    #print args
    for a in args:
      msg.append( a )
    try:
      self.host.send( msg )
      if self.guiosc != None:
          self.guiosc.send( msg )
      if self.verbose:
        print( "sending message", msg )
    except OSC.OSCClientError:
      if self.verbose:
        print( "error sending message", msg )

  def loopbackMinibee( self, mid, data ):
    alldata = [ mid ]
    alldata.extend( data )
    self.sendMessage( "/minibee/loopback", alldata )
  
  def infoMiniBee( self, serial, mid, insize, outsize ):
    self.sendMessage( "/minibee/info", [ serial, mid, insize, outsize ] )
    
  def sendStatusInfo( self, nid, status ):
    self.sendMessage( "/minibee/status", [ nid, status ] )

  def rssiMiniBee( self, nid, rssi ):
    self.sendMessage( "/minibee/rssi", [ nid, rssi ] )

  def dataMiniBee( self, mid, data ):
    alldata = [ mid ]
    alldata.extend( data )
    self.sendMessage( "/minibee/data", alldata )
    if self.verbose:
      print( "sending osc message with data", mid, data )
      
  def triggerDataMiniBee( self, mid, data ):
    alldata = [ mid ]
    alldata.extend( data )
    self.sendMessage( "/minibee/trigger", alldata )
    if self.verbose:
      print( "sending osc message with trigger data", mid, data )

  def privateDataMiniBee( self, mid, data ):
    alldata = [ mid ]
    alldata.extend( data )
    self.sendMessage( "/minibee/private", alldata )
    if self.verbose:
      print( "sending osc message with private data", mid, data )      

  def setOutput( self, mid, data ):
    #print( self.hive, mid, data )
    self.hive.oscToMiniBee( mid, data )

  def setCustom( self, mid, data ):
    self.hive.oscToMiniBeeCustom( mid, data )

  def setRun( self, mid, data ):
    #print( self.hive, mid, data )
    self.hive.oscRunToMiniBee( mid, data )

  def setLoopback( self, mid, data ):
    #print( self.hive, mid, data )
    self.hive.oscLoopbackToMiniBee( mid, data )
    
  def reset_hive( self ):
    self.hive.oscResetToHive()

  def reset_minibee( self, mid ):
    self.hive.oscResetToMiniBee( mid )

  def minibeeAnnounce( self, mid ):
    self.hive.oscAnnounceToMiniBee( mid )

  def minibeeSaveID( self, mid ):
    self.hive.oscStoreToMinibee( mid )

  def saveIDs( self ):
    self.hive.oscStoreToHive()
    
  def setMiniBeeConfiguration( self, config ):
    if len( config ) == 3:
      # set minibee with serial number to given id
      if not self.hive.hive.map_serial_to_bee( config[2], config[0] ):
	# send error message
	self.sendMessage( "/minibee/configuration/error", config )
	return
    # continue with setting the configuration
    self.hive.hive.set_minibee_config( config[0], config[1] )
    self.sendMessage( "/minibee/configuration/done", config )

  def queryMiniBeeConfiguration( self, mid ):
    #FIXME: implement this
    print( "Query MiniBee configuration %i"%mid )

  def queryConfiguration( self, cid ):
    #FIXME: implement this
    print( "Query configuration %i"%cid )

  def queryPinConfiguration( self, cid, pid ):
    #FIXME: implement this
    print( "Query configuration %i, pin %s"%(cid,pid) )

  def queryTwiConfiguration( self, cid, tid ):
    #FIXME: implement this
    print( "Query configuration %i, twi %i"%(cid,tid) )

  def deleteConfiguration( self, cid ):
    if not self.hive.hive.delete_configuration( cid ):
      self.sendMessage( "/minihive/configuration/error", cid )
    else:
      self.sendMessage( "/minihive/configuration/delete/done", cid )

  def setConfiguration( self, cid, config ):
    allconfig = [ cid ]
    allconfig.extend( config )
    if not self.hive.hive.set_configuration( cid, config ):
      self.sendMessage( "/minihive/configuration/error", allconfig )
    else:
      self.sendMessage( "/minihive/configuration/done", allconfig )

  def setPinConfiguration( self, cid, pincfg ):
    allconfig = [ cid ]
    allconfig.extend( pincfg )
    if not self.hive.hive.set_pin_configuration( cid, pincfg ):
      self.sendMessage( "/minihive/configuration/pin/error", allconfig )
    self.sendMessage( "/minihive/configuration/pin/done", allconfig )

  def setTwiConfiguration( self, cid, twicfg ):
    allconfig = [ cid ]
    allconfig.extend( twicfg )
    if not self.hive.hive.set_twi_configuration( cid, twicfg ):
      self.sendMessage( "/minihive/configuration/twi/error", allconfig )
    else:
      self.sendMessage( "/minihive/configuration/twi/done", allconfig )

  def createdNewConfiguration( self, filename ):
    self.sendMessage( "/minihive/configuration/new", [ filename ] )
  
  def loadConfiguration( self, filename ):
    self.hive.hive.load_from_file( filename )
    print( "loaded configuration from:", filename )

  def saveConfiguration( self, filename ):
    self.hive.hive.write_to_file( filename )
    print( "saved configuration to:", filename )
    
  def quit( self ):
    self.hive.hive.exit()

# end class DNOSCServer

# begin class DataNetworkOSC
#class DataNetworkOSC(object):
  def __init__(self, hostip, hostport, myip, myport, hive, guiip, guiport ):
    self.verbose = False
    self.hive = hive
    self.hostport = hostport
    self.hostip = hostip
    self.port = myport    
    self.myip = myip
    
    self.host = OSC.OSCClient()
    send_address = ( self.hostip, self.hostport )
    self.host.connect( send_address )
    
    self.guiosc = None
    self.guiip = guiip
    self.guiport = guiport
    
    print( "gui interface", self.guiip, self.guiport )
    
    if self.guiport != None :
        print( "created gui osc" )
        self.guiosc = OSC.OSCClient()
        gui_send_address = ( self.guiip, self.guiport )
        self.guiosc.connect( gui_send_address )

    receive_address = ( self.myip, self.port )
    self.osc = OSC.OSCServer( receive_address )
    self.add_handlers()
    self.thread = threading.Thread( target = self.osc.serve_forever )
    self.thread.start()
    


class SWMiniHiveOSC( object ):
  def __init__(self, hostip, hostport, myip, myport, swarmSize, serialPort, serialRate, config, idrange, verbose, apiMode, ignoreUnknown = False, checkXbeeError = False, guiip = None, guiport = None ):
    
    self.hive = pydonhive.MiniHive( serialPort, serialRate, apiMode )
    self.hive.set_id_range( idrange[0], idrange[1] )
    self.hive.load_from_file( config )
    self.hive.set_verbose( verbose )
    self.hive.set_ignore_unknown( ignoreUnknown )
    self.hive.set_check_xbee_error( checkXbeeError )    

    self.osc = MiniHiveOSC( hostip, hostport, myip, myport, self, guiip, guiport )
    self.osc.setVerbose( verbose )
    
    self.verbose = verbose

    self.hive.set_newConfigAction( self.newconfigToOSC )
    self.hive.set_loopbackAction( self.loopBackToOSC )
    self.hive.set_newBeeAction( self.hookBeeToOSC )
    self.hive.start_serial()  
  
  def exit( self ):
    self.osc.osc.close()
    print( "Waiting for Server-thread to finish" )
    self.osc.thread.join() ##!!!
    print( "Done; goodbye" )
    self.hive.exit()
    #sys.exit()
  
  def start( self ):
    try :
      self.hive.run()
    except (SystemExit, RuntimeError,KeyboardInterrupt, IOError ) :
      self.exit()

  def saveConfiguration( self, filename ):
    self.hive.write_to_file( filename )

  #def setMapAction( self, nodeid, mid ):
    #self.datanetwork.nodes[ nodeid ].setAction( lambda data: self.dataNodeDataToMiniBee( data, mid ) )

  def newconfigToOSC( self, filename ):
    self.osc.createdNewConfiguration( filename )
  
  def loopBackToOSC( self, mid, data ):
    self.osc.loopbackMinibee( mid, data )
    
# bee to datanode
  def hookBeeToOSC( self, minibee ):
    self.osc.infoMiniBee( minibee.serial, minibee.nodeid, minibee.getInputSize(), minibee.getOutputSize() )
    minibee.set_action( self.minibeeDataToOSC )
    minibee.set_rssi_action( self.minibeeRSSIToOSC )
    minibee.set_trigger_action( self.minibeeTriggerDataToOSC )
    minibee.set_private_action( self.minibeePrivateDataToOSC )
    minibee.set_status_action( self.osc.sendStatusInfo )
    if self.verbose:
      print( "hooking bee to OSC out", minibee,  minibee.getInputSize(),  minibee.getOutputSize() )

  def minibeeDataToOSC( self, data, nid ):
    self.osc.dataMiniBee( nid, data )
    if self.verbose:
      print( "data", nid,  data )

  def minibeeRSSIToOSC( self, nid, rssi ):
    self.osc.rssiMiniBee( nid, rssi )
    if self.verbose:
      print( "rssi", nid,  rssi )

  def minibeeTriggerDataToOSC( self, data, nid ):
    self.osc.triggerDataMiniBee( nid, data )
    if self.verbose:
      print( "trigger", nid,  data )

  def minibeePrivateDataToOSC( self, nid, data ):
    self.osc.privateDataMiniBee( nid, data )
    if self.verbose:
      print( "private", nid,  data )

  def oscResetToHive( self ):
    self.hive.reset_hive()

  def oscStoreToHive( self ):
    self.hive.store_ids()

  def oscResetToMiniBee( self, nid ):
    self.hive.reset_bee( nid )

  def oscAnnounceToMiniBee( self, nid ):
    self.hive.announce_minibee_id( nid )

  def oscStoreToMinibee( self, nid ):
    self.hive.store_minibee_id( nid )

  def oscRunToMiniBee( self, nid, status ):
    if nid in self.hive.bees:
      self.hive.bees[ nid ].send_run( self.hive.serial, status )    
    if self.verbose:
      print( "minibee run", nid,  status )

  def oscLoopbackToMiniBee( self, nid, status ):
    if nid in self.hive.bees:
      self.hive.bees[ nid ].send_loopback( self.hive.serial, status )
    if self.verbose:
      print( "minibee loopback", nid,  status )

# data node to minibee
  def oscToMiniBee( self, nid, data ):
    if nid in self.hive.bees:
      self.hive.bees[ nid ].send_output( self.hive.serial, data )
    if self.verbose:
      print( "output", nid,  data )

  def oscToMiniBeeCustom( self, nid, data ):
    if nid in self.hive.bees:
      self.hive.bees[ nid ].send_custom( self.hive.serial, data )
    if self.verbose:
      print( "custom", nid,  data )

  #def dataNodeDataToMiniBeeCustom( self, data, nid ):
    #self.hive.bees[ nid ].send_custom( self.hive.serial, data )



# main program:
if __name__ == "__main__":
  if 1 == len( sys.argv ) and haveGui:
    option_parser_class = optparse_gui.OptionParser
  else:
    option_parser_class = optparse.OptionParser

  parser = option_parser_class(description='Create a program that speaks OSC to communicate with the minibee network.')
  parser.add_option('-s','--serial', action='store',type="string",dest="serial",default="/dev/ttyUSB0",
		  help='the serial port [default:%s]'% '/dev/ttyUSB0')
  parser.add_option('-a','--apimode', action='store_true', dest="apimode",default=False,
		  help='use API mode for communication with the minibees [default:%s]'% False)
  parser.add_option('-v','--verbose', action='store_true',dest="verbose",default=False,
		  help='verbose printing [default:%i]'% False)
  parser.add_option('-c','--config', action='store', type="string", dest="config",default="pydon/configs/hiveconfig.xml",
		  help='the name of the configuration file for the minibees [default:%s]'% 'pydon/configs/hiveconfig.xml')
  parser.add_option('-m','--nr_of_minibees', type=int, action='store',dest="minibees",default=10,
		  help='the number of minibees in the network [default:%i]'% 10)
  parser.add_option('-d','--host_ip', action='store',type="string", dest="host",default="127.0.0.1",
		  help='the ip address of the application that has to receive the OSC messages [default:%s]'% "127.0.0.1")
  parser.add_option('-t','--host_port', type=int, action='store',dest="hport",default=57120,
		  help='the port on which the application that has to receive the OSC messages will listen [default:%i]'% 57120 )
  parser.add_option('-b','--baudrate', action='store',type=int,dest="baudrate",default=57600,
		  help='the serial port [default:%i]'% 57600)
  parser.add_option('-i','--ip', type="string", action='store',dest="ip",default="0.0.0.0",
		  help='the ip on which the client will listen [default:%s]'% "0.0.0.0" )
  parser.add_option('-p','--port', type=int, action='store',dest="port",default=57600,
		  help='the port on which the minihiveosc will listen [default:%i]'% 57600 )
  parser.add_long_option('--gui_ip', action='store',type="string", dest="guiip",default="127.0.0.1",
		  help='the ip address of the gui interface that has to receive the OSC messages [default:%s]'% "127.0.0.1")
  parser.add_long_option('--gui_port', type=int, action='store',dest="guiport",default=None,
		  help='the port on which the gui interface will listen to receive the OSC messages [default: None (no gui)]' )

  (options,args) = parser.parse_args()
  #print args.accumulate(args.integers)
  #print options
  #print args
  #print( options.host )
  
  print( "MiniHiveOSC - communicating via OSC with the MiniBee network" )
  swhive = SWMiniHiveOSC( options.host, options.hport, options.ip, options.port, options.minibees, options.serial, options.baudrate, options.config, [1,options.minibees], options.verbose, options.apimode, options.guiip, options.guiport )
  print( "Created OSC listener at (%s,%i) and OSC sender to (%s,%i) and opened serial port at %s. Now waiting for messages."%(options.ip, options.port, options.host, options.hport, options.serial ) )
  print( "Created OSC sender to GUI at (%s,%i)."%(options.guiip, options.guiport ) )
  swhive.start()
