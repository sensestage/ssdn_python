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
import threading

import csv

import pydon
import pydonhive

class SWPydonHive( object ):
  def __init__(self, hostip, myport, myip, myname, swarmSize, serialPort, serialRate, config, idrange, verbose, apiMode, ignoreUnknown = False, checkXbeeError = False, hostport=57120 ):
    self.datanetwork = pydon.DataNetwork( hostip, myport, myname, 1, swarmSize, myip, hostport )
    self.datanetwork.setVerbose( verbose )

    self.verbose = verbose
    self.labelbase = "minibee"
    
    self.hive = pydonhive.MiniHive( serialPort, serialRate, apiMode )
    self.hive.set_id_range( idrange[0], idrange[1] )
    self.hive.load_from_file( config )
    self.hive.set_verbose( verbose )
    self.hive.set_ignore_unknown( ignoreUnknown )
    self.hive.set_check_xbee_error( checkXbeeError )
    
    self.datanetwork.setHive( self.hive )

    # self.datanetwork.setterCallback(
          
    self.hive.set_newBeeAction( self.hookBeeToDatanetwork )
    
    self.datanetwork.set_resetHiveAction( self.resetHive )
    self.datanetwork.set_resetAction( self.resetMiniBee )
    self.datanetwork.set_runAction( self.runMiniBee )
    self.datanetwork.set_loopAction( self.loopMiniBee )

    self.datanetwork.set_mapAction( self.mapMiniBee )
    
    self.datanetwork.set_mapAction( self.mapMiniBee )
    self.datanetwork.set_mapCustomAction( self.mapMiniBeeCustom )
    self.datanetwork.set_unmapAction( self.unmapMiniBee )
    self.datanetwork.set_unmapCustomAction( self.unmapMiniBeeCustom )

    self.datanetwork.set_triggerNodeAction( self.setupTriggerMiniBee )
    self.datanetwork.set_triggerRemoveNodeAction( self.unsetupTriggerMiniBee )
    self.datanetwork.set_privateNodeAction( self.setupPrivateMiniBee )
    self.datanetwork.set_privateRemoveNodeAction( self.unsetupPrivateMiniBee )

    self.datanetwork.osc.add_callback_noid( 'register', self.reregisterBees )

    self.datanetwork.set_quitAction( self.exit )

    self.datanetwork.startOSC()
    self.hive.start_serial()
    
    self.minibeeToTriggerNodes = {}
    self.minibeeToPrivateNodes = {}

  def exit( self ):
    self.hive.osclock.acquire()
    #print( "osc lock acquired by thread ", threading.current_thread().name, "exit" )
    self.datanetwork.osc.unregister()
    print( "\nClosing OSCServer." )
    self.datanetwork.osc.osc.close()
    print( "Waiting for Server-thread to finish" )
    self.hive.osclock.release()
    #print( "osc lock released by thread ", threading.current_thread().name, "exit" )
    self.datanetwork.osc.thread.join() ##!!!
    print( "Done; goodbye" )
    self.hive.exit()
    #sys.exit()

  def start( self ):
    print( "starting swpydonhive" )
    try :
      #while not self.datanetwork.osc.registered:
        #print( "waiting to be registered; is the DataNetwork host running?" )
        ##print time
        #print self.datanetwork.osc.registered
        #time.sleep( 1.0 )
      print( "now running hive", self.hive.running )
      self.hive.run()
    except (SystemExit, RuntimeError, KeyboardInterrupt, IOError ) :
      self.exit()
  
  def saveConfiguration( self, filename ):
    self.hive.write_to_file( filename )

# mapping support
  def mapMiniBee( self, nodeid, mid ):
    # check whether already mapped
    # check whether subscribed
    if self.datanetwork.subscribedToNode( nodeid ):
      # check whether mapped to minibee
      if nodeid in self.datanetwork.nodes:
	if self.datanetwork.nodes[ nodeid ].mapOutput != mid:
	  # change mapping, otherwise do nothing
	  self.datanetwork.nodes[ nodeid ].setMapOutput( mid )
	  self.datanetwork.nodes[ nodeid ].setMapCustom( None )
	  self.datanetwork.nodes[ nodeid ].setAction( lambda data: self.dataNodeDataToMiniBee( data, mid ) )
      else:
	self.datanetwork.osc.add_callback( 'info', nodeid, lambda nid: self.setMapAction( nid, mid ) )
    else:
      self.hive.osclock.acquire()
      self.datanetwork.osc.subscribeNode( nodeid, lambda nid: self.setMapAction( nid, mid ) )
      self.hive.osclock.release()
  
  def setMapAction( self, nodeid, mid ):
    if nodeid not in self.datanetwork.nodes:
      self.datanetwork.osc.add_callback( 'info', nodeid, lambda nid: self.setMapAction( nid, mid ) )
    else:
      self.datanetwork.nodes[ nodeid ].setMapOutput( mid )
      self.datanetwork.nodes[ nodeid ].setMapCustom( None )
      self.datanetwork.nodes[ nodeid ].setAction( lambda data: self.dataNodeDataToMiniBee( data, mid ) )

  def unmapMiniBee( self, nodeid, mid ):
    self.hive.osclock.acquire()
    self.datanetwork.osc.unsubscribeNode( nodeid )
    self.hive.osclock.release()
    self.datanetwork.nodes[ nodeid ].setMapOutput( None )
    self.datanetwork.nodes[ nodeid ].setAction( None )

  def setupTriggerMiniBee( self, mid, nodeid ):
    print( "triggers of minibee", mid, "to node", nodeid )
    self.minibeeToTriggerNodes[ mid ] = nodeid
    #FIXME
    #self.datanetwork.osc.addExpected( nid, [ mybee.getTriggerSize(), mybee.name ] )
    #self.datanetwork.createNode( nid, mybee.getTriggerSize(), mybee.name, 0 )    
    
  def unsetupTriggerMiniBee( self, mid, nodeid ):
    print( "triggers of minibee", mid, "not to node", nodeid )
    del self.minibeeToTriggerNodes[ mid ]

  def setupPrivateMiniBee( self, mid, nodeid, datasize ):
    print( "private of minibee", mid, "to node", nodeid )
    self.datanetwork.osc.addExpected( nodeid, [ datasize ] ) # , mybee.name
    self.datanetwork.createNode( nodeid, datasize, "", 0 )    
    self.minibeeToPrivateNodes[ mid ] = nodeid
    print( self.minibeeToPrivateNodes )
    
  def unsetupPrivateMiniBee( self, mid, nodeid ):
    print( "private of minibee", mid, "not to node", nodeid )
    del self.minibeeToPrivateNodes[ mid ]

  def mapMiniBeeCustom( self, nodeid, mid ):
    print( "map minibee custom", nodeid, "to", mid )
    if self.datanetwork.subscribedToNode( nodeid ):
      # check whether mapped to minibee
      if nodeid in self.datanetwork.nodes:
	if self.datanetwork.nodes[ nodeid ].mapCustom != mid:
	  # change mapping, otherwise do nothing
	  print( "mapping custom", nodeid, "to", mid )
	  self.datanetwork.nodes[ nodeid ].setMapOutput( None )
	  self.datanetwork.nodes[ nodeid ].setMapCustom( mid )
	  self.datanetwork.nodes[ nodeid ].setAction( lambda data: self.dataNodeDataToMiniBeeCustom( data, mid ) )
	else:
	  self.datanetwork.osc.add_callback( 'info', nodeid, lambda nid: self.setMapCustomAction( nid, mid ) )
    else:
      self.hive.osclock.acquire()
      print( "subscribing to node", nodeid )
      self.datanetwork.osc.subscribeNode( nodeid, lambda nid: self.setMapCustomAction( nodeid, mid ) )
      self.hive.osclock.release()
  
  def unmapMiniBeeCustom( self, nodeid, mid ):
    self.hive.osclock.acquire()
    self.datanetwork.osc.unsubscribeNode( nodeid )
    self.hive.osclock.release()
    self.datanetwork.nodes[ nodeid ].setMapCustom( None )
    self.datanetwork.nodes[ nodeid ].setAction( None )

  def setMapCustomAction( self, nodeid, mid ):
    print( "set map custom action", nodeid, "to", mid )
    if not nodeid in self.datanetwork.nodes:
      print( "not subscribed to node or node not present, wait for info message", nodeid )
      self.datanetwork.osc.add_callback( 'info', nodeid, lambda nid: self.setMapCustomAction( nid, mid ) )
    else:
      print( "mapping custom", nodeid, "to", mid )
      self.datanetwork.nodes[ nodeid ].setMapOutput( None )
      self.datanetwork.nodes[ nodeid ].setMapCustom( mid )
      self.datanetwork.nodes[ nodeid ].setAction( lambda data: self.dataNodeDataToMiniBeeCustom( data, mid ) )

  def resetHive( self ):
    self.hive.reset_hive()

  def resetMiniBee( self, mid ):
    self.hive.reset_bee( mid )

  def runMiniBee( self, mid, status ):
    if mid in self.hive.bees:
      self.hive.bees[ mid ].send_run( self.hive.serial, status )

  def loopMiniBee( self, mid, status ):
    if mid in self.hive.bees:
      self.hive.bees[ mid ].send_loopback( self.hive.serial, status )


# labeling
  def set_labelbase( self, newlabel ):
    self.labelbase = newlabel

# bee to datanode
  def hookBeeToDatanetwork( self, minibee ):
    minibee.set_info_action( self.sendInfoBee )
    minibee.set_status_action( self.sendStatusInfo )
    minibee.set_first_action( self.addAndSubscribe )
    minibee.set_action( self.minibeeDataToDataNode )
    minibee.set_private_action( self.minibeePrivateDataToDataNode )
    minibee.set_trigger_action( self.minibeeTriggerDataToDataNode )
    
  def sendInfoBee( self, minibee ):    
    self.hive.osclock.acquire()
    self.datanetwork.osc.infoMinibee( minibee.nodeid, minibee.getInputSize(), minibee.getOutputSize() )
    self.hive.osclock.release()

  def sendStatusInfo( self, nid, status ):
    self.hive.osclock.acquire()
    self.datanetwork.osc.statusMinibee( nid, status )
    self.hive.osclock.release()
    
  def reregisterBees( self, state ):
    if state:
      for beeid, bee in self.hive.bees.items():
	#print bee
	if beeid < 65535:
	  self.hookBeeToDatanetwork( bee )
	  self.hive.osclock.acquire()
	  self.datanetwork.osc.infoMinibee( bee.nodeid, bee.getInputSize(), bee.getOutputSize() )
	  self.sendStatusInfo( beeid, bee.status )
	  if bee.status == 'receiving':
	    self.datanetwork.osc.addExpected( beeid, [] )
	  self.hive.osclock.release()

  def addAndSubscribe( self, nid, data ):
    mybee = self.hive.bees[ nid ]
    if mybee.name == "":
      mybee.name = (self.labelbase + str(nid) )
    self.hive.osclock.acquire()
    self.datanetwork.osc.addExpected( nid, [ mybee.getInputSize(), mybee.name ] )
    self.datanetwork.createNode( nid, mybee.getInputSize(), mybee.name, 0 )
    self.hive.osclock.release()
    self.sendBeeLabels( mybee )

    
  def sendBeeLabels( self, mybee ):
    if mybee.cid > 0:
      count = 0
      mylabels = mybee.getLabels()
      self.hive.osclock.acquire()
#      if self.verbose:
#	print( "osc lock acquired by thread ", threading.current_thread().name, "send bee labels" )
      [ self.datanetwork.osc.labelSlot( mybee.nodeid, index, mybee.name + "_" + str( item )) for index, item in enumerate(mylabels)]
#      if self.verbose:
#	print( "osc lock released by thread ", threading.current_thread().name, "send bee labels" )
      self.hive.osclock.release()

  def minibeeDataToDataNode( self, data, nid ): # inverse argument order - why?
    self.hive.osclock.acquire()
    res = self.datanetwork.setNodeData( nid, data, False )
    self.hive.osclock.release()
    return res

  def minibeeTriggerDataToDataNode( self, mid, data ): # inverse argument order - why?
    if mid in self.minibeeToTriggerNodes:
      nid = self.minibeeToTriggerNodes[ mid ]
      self.hive.osclock.acquire()
      res = self.datanetwork.setNodeData( nid, data, False )
      self.hive.osclock.release()
    else:
      res = True
    return res

  def minibeePrivateDataToDataNode( self, mid, data ): # inverse argument order - why?
    if self.verbose:
      print( "private data from minibee", mid, data )
    print( self.minibeeToPrivateNodes, type( self.minibeeToPrivateNodes ), mid )
    if mid in self.minibeeToPrivateNodes:
      nid = self.minibeeToPrivateNodes[ mid ]
      self.hive.osclock.acquire()
      res = self.datanetwork.setNodeData( nid, data, False )
      self.hive.osclock.release()
    else:
      res = True
    return res

# data node to minibee
  def dataNodeDataToMiniBee( self, data, nid ):
    if self.verbose:
      print( "output mapped data", nid, data )
    if nid in self.hive.bees:
      self.hive.bees[ nid ].send_output( self.hive.serial, data )

  def dataNodeDataToMiniBeeCustom( self, data, nid ):
    if self.verbose:
      print( "custom mapped data", nid, data )
    if nid in self.hive.bees:
      self.hive.bees[ nid ].send_custom( self.hive.serial, data )

# logger:
  def initializeLogger( self ):
    # make filename with a date stamp    
    self.filename = 'logs/hivedebuglog' + time.strftime("_%j_%H_%M_%S") + '.csv'
    print( "opening new log file", self.filename )
    self.hiveLogFile = open(self.filename, 'wb')
    self.hiveLogWriter = csv.writer(self.hiveLogFile, dialect='excel-tab')
    self.starttime = time.time()
    self.maxrows = 60 * 60 * 10 * 4
    self.rows = 0
    self.hive.serial.set_log_action( self.writeLogAction )

  def openNewLogFile( self ):
    self.hiveLogFile.close()
    self.filename = 'logs/hivedebuglog' + time.strftime("_%j_%H_%M_%S") + '.csv'
    print( "opening new log file", self.filename )
    self.hiveLogFile = open(self.filename, 'wb')
    self.hiveLogWriter = csv.writer( self.hiveLogFile, dialect='excel-tab')

  def writeLogAction( self, data ):
    #print( "writing log data", data )
    self.rows = self.rows + 1
    self.hiveLogWriter.writerow( [time.strftime("%j:%H:%M:%S")] + [str(time.time() - self.starttime)] + data )
    if self.rows > self.maxrows:
      self.openNewLogFile()
      self.rows = 0

# main program:
if __name__ == "__main__":
  if 1 == len( sys.argv ) and haveGui:
    option_parser_class = optparse_gui.OptionParser
  else:
    option_parser_class = optparse.OptionParser

  parser = option_parser_class(description='Create a datanetwork client to communicate with the minibee network.')
  parser.add_option('-s','--serial', action='store',type="string",dest="serial",default="/dev/ttyUSB0",
		  help='the serial port [default:%s]'% '/dev/ttyUSB0')
  parser.add_option('-a','--apimode', action='store_true', dest="apimode",default=False,
		  help='use API mode for communication with the minibees [default:%s]'% False)
  parser.add_option('-v','--verbose', action='store_true', dest="verbose",default=False,
		  help='verbose printing [default:%i]'% False)
  parser.add_option('-n','--name', action='store', type="string", dest="name",default="pydonhive",
		  help='the name of the client in the datanetwork [default:%s]'% "pydonhive" )
  parser.add_option('-c','--config', action='store', type="string", dest="config",default="pydon/configs/hiveconfig.xml",
		  help='the name of the configuration file for the minibees [default:%s]'% 'pydon/configs/hiveconfig.xml')
  parser.add_option('-m','--nr_of_minibees', type=int, action='store',dest="minibees",default=20,
		  help='the number of minibees in the network [default:%i]'% 20)
  parser.add_option('-o','--minibee_offset', type=int, action='store',dest="mboffset",default=1,
		  help='the offset of the number range for the minibees in the network [default:%i]'% 1)
  parser.add_option('-d','--host_ip', action='store',type="string", dest="host",default="127.0.0.1",
		  help='the ip address of the datanetwork host [default:%s]'% "127.0.0.1")
  parser.add_option('-b','--baudrate', action='store',type=int,dest="baudrate",default=57600,
		  help='the serial port [default:%i]'% 57600)
  parser.add_option('-p','--port', type=int, action='store',dest="port",default=57600,
		  help='the port on which the client will listen [default:%i]'% 57600 )
  parser.add_option('-i','--ip', type="string", action='store',dest="ip",default="0.0.0.0",
		  help='the ip on which the client will listen [default:%s]'% "0.0.0.0" )

  (options,args) = parser.parse_args()
  #print args.accumulate(args.integers)
  #print options
  #print args
  print( "--------------------------------------------------------------------------------------" )
  print( "SWPydonHive - a SenseWorld DataNetwork client to communicate with the minibee network." )
  print( " --- to find out more about the startup options start with \'swpydonhive.py -h\'" )
  print( " --- The client has been started with these options:" )
  print( options )
  print( "--------------------------------------------------------------------------------------" )
  
  swhive = SWPydonHive( options.host, options.port, options.ip, options.name, options.minibees, options.serial, options.baudrate, options.config, [options.mboffset,options.minibees], options.verbose, options.apimode )
  
  swhive.start()
