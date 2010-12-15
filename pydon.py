#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time as myTime

#print myTime

import sys
import pycurl
import liblo
from liblo import *

# begin class HostPort
class HostPort:
    def __init__(self):
        self.contents = ''

    def body_callback(self, buf):
        self.contents = self.contents + buf
# end class HostPort

class DNOSCServer( ServerThread ):
  def __init__(self, port, dnosc ):
    ServerThread.__init__(self, port)
    self.dnosc = dnosc
    
  @make_method('/datanetwork/announce', 'si')
  def announced( self, path, args, types ):
    # could add a check if this is really me
    #self.dnosc.registered = True
    print "DataNetwork announced at:", args

  @make_method('/datanetwork/quit', 'si')
  def hasquit( self, path, args, types ):
    # could add a check if this is really me
    #self.dnosc.registered = True
    print "DataNetwork quit at:", args
  
  @make_method('/registered', 'is')
  def registered( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.set_registered( True )
    print "Registered as client:", args

  @make_method('/unregistered', 'is')
  def unregistered( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.set_registered( False )
    print "Unregistered as client:", args

  @make_method('/error', 'ssi')
  def error_msg( self, path, args, types ):
    # could add a check if this is really me
    print "Error from datanetwork:", args

  @make_method('/warn', 'ssi')
  def warn_msg( self, path, args, types ):
    # could add a check if this is really me
    print "Warning from datanetwork:", args

  @make_method('/ping', 'is')
  def pingpong( self, path, args, types ):
    self.dnosc.sendSimpleMessage( "/pong" )
    
  @make_method('/info/expected', None )
  def node_expected( self, path, args, types ):
    self.dnosc.expected_node( args[0] )
    print "Expected node:", args

  @make_method('/info/node', 'isii' )
  def node_info( self, path, args, types ):
    #print "Present node:", args
    self.dnosc.info_node( args[0], args[1], args[2], args[3] )
    print "Present node:", args

  @make_method('/info/slot', 'iisi' )
  def slot_info( self, path, args, types ):
    self.dnosc.info_slot( args[0], args[1], args[2], args[3] )
    #print "Present slot:", args

  @make_method('/info/client', 'sis' )
  def client_info( self, path, args, types ):
    # could add a check if this is really me
    print "Present client:", args

  @make_method('/info/setter', 'isii' )
  def node_setter( self, path, args, types ):
    # could add a check if this is really me
    print "Present setter:", args

  @make_method('/subscribed/node', 'isi' )
  def node_subscribed( self, path, args, types ):
    # could add a check if this is really me
    if 'subscribe' in self.dnosc.callbacks:
      #print self.dnosc.callbacks['subscribe']
      if args[2] in self.dnosc.callbacks['subscribe']:
	#print self.dnosc.callbacks['subscribe'][ args[2] ] 
	self.dnosc.callbacks['subscribe'][ args[2] ]( args[2] )
	return
    print "Subscribed to node:", args

  @make_method('/unsubscribed/node', 'isi' )
  def node_unsubscribed( self, path, args, types ):
    # could add a check if this is really me
    if 'unsubscribe' in self.dnosc.callbacks:
      #print self.dnosc.callbacks['subscribe']
      if args[2] in self.dnosc.callbacks['unsubscribe']:
	#print self.dnosc.callbacks['subscribe'][ args[2] ] 
	self.dnosc.callbacks['unsubscribe'][ args[2] ]( args[2] )
	return
    print "Unsubscribed from node:", args

  @make_method('/subscribed/slot', 'isii' )
  def slot_subscribed( self, path, args, types ):
    # could add a check if this is really me
    if 'subscribeSlot' in self.dnosc.callbacks:
      #print self.dnosc.callbacks['subscribe']
      if args[2] in self.dnosc.callbacks['subscribeSlot']:
	#print self.dnosc.callbacks['subscribe'][ args[2] ] 
	self.dnosc.callbacks['subscribeSlot'][ args[2] ]( args[2] )
	return
    print "Subscribed to slot:", args

  @make_method('/unsubscribed/slot', 'isii' )
  def slot_unsubscribed( self, path, args, types ):
    # could add a check if this is really me
    if 'unsubscribeSlot' in self.dnosc.callbacks:
      #print self.dnosc.callbacks['subscribe']
      if args[2] in self.dnosc.callbacks['unsubscribeSlot']:
	#print self.dnosc.callbacks['subscribe'][ args[2] ] 
	self.dnosc.callbacks['unsubscribeSlot'][ args[2] ]( args[2] )
	return
    print "Unsubscribed from slot:", args

  @make_method('/removed/node', 'i' )
  def node_removed( self, path, args, types ):
    # could add a check if this is really me
    if 'remove' in self.dnosc.callbacks:
      #print self.dnosc.callbacks['subscribe']
      if args[2] in self.dnosc.callbacks['remove']:
	#print self.dnosc.callbacks['subscribe'][ args[2] ] 
	self.dnosc.callbacks['remove'][ args[2] ]( args[2] )
	return
    print "Node removed:", args

  @make_method('/data/node', None )
  def node_data( self, path, args, types ):
    self.dnosc.data_for_node( args[0], args[1:] )
    #print "Node data:", args

  @make_method('/data/slot', 'iis' )
  def slot_datas( self, path, args, types ):
    self.dnosc.data_for_slot( args[0], args[1], args[2] )
    #print "Slot string data:", args

  @make_method('/data/slot', 'iif' )
  def slot_dataf( self, path, args, types ):
    self.dnosc.data_for_slot( args[0], args[1], args[2] )
    #print "Slot numerical data:", args

# start hive and minibee management

  @make_method('/registered/hive', 'isii')
  def registered_hive( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.set_registered_hive( True, args[2], args[3] )
    print "Registered as hive client:", args

  @make_method('/unregistered/hive', 'is')
  def unregistered_hive( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.set_registered_hive( False )
    print "Unregistered as hive client:", args

  @make_method('/map/minibee/output', 'ii')
  def map_minibee( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.map_minibee( args[0], args[1] )
    print "Map minibee:", args

  @make_method('/unmap/minibee/output', 'ii')
  def unmap_minibee( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.unmap_minibee( args[0], args[1] )
    print "Unmap Minibee:", args

  @make_method('/map/minibee/custom', 'ii')
  def map_minibee_custom( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.map_minibee_custom( args[0], args[1] )
    print "Map minibee custom:", args

  @make_method('/unmap/minibee/custom', 'ii')
  def unmap_minibee_custom( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.unmap_minibee_custom( args[0], args[1] )
    print "Unmap Minibee custom:", args

  @make_method('/mapped/minibee/output', 'ii')
  def mapped_minibee( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.mapped_minibee( args[0], args[1] )
    print "Mapped minibee:", args

  @make_method('/unmapped/minibee/output', 'ii')
  def unmapped_minibee( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.unmapped_minibee( args[0], args[1] )
    print "Unmapped Minibee:", args

  @make_method('/mapped/minibee/custom', 'ii')
  def mapped_minibee_custom( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.mapped_minibee_custom( args[0], args[1] )
    print "Mapped minibee custom:", args

  @make_method('/unmapped/minibee/custom', 'ii')
  def unmapped_minibee_custom( self, path, args, types ):
    # could add a check if this is really me
    self.dnosc.unmapped_minibee_custom( args[0], args[1] )
    print "Unmapped Minibee custom:", args

  @make_method('/info/minibee', None )
  def info_minibee( self, path, args, types ):
    self.dnosc.info_minibee( args[0], args[1], args[2] )
    print "Info minibee:", args

  @make_method('/info/hive', None )
  def info_hive( self, path, args, types ):
    #self.dnosc.info_minibee( args[0] )
    print "Info hive:", args

# end minibee management

  @make_method(None, None)
  def fallback(self, path, args, types, src):
    print "got unknown message '%s' from '%s'" % (path, src.get_url())
    for a, t in zip(args, types):
      print "argument of type '%s': %s" % (t, a)


# begin class DataNetworkOSC
class DataNetworkOSC(object):
  def __init__(self, hostip, myport, myname, network, cltype=0, nonodes=0 ):
    self.registered = False
    self.network = network
    self.createOSC( hostip, myport, myname, cltype, nonodes )
    self.callbacks = {}
    
  def add_hive( self, hive ):
    self.hive = hive
    
  def createOSC( self, hostip, myport, myname, cltype, nonodes ):
    self.name = myname
    self.hostIP = hostip
    self.port = myport
    self.findHost( hostip )
    print "Found host at", self.hostIP, self.hostPort
    self.resetHost()
    self.createClient()
    if cltype == 0:
      self.register()
    if cltype == 1:
      self.registerHive(nonodes)
    
    
  def createClient(self):
    try:
      self.server = DNOSCServer( self.port, self )
      self.server.start()
    except ServerError, err:
      print str(err)
      sys.exit()
    
  def resetHost(self):
    try:
      self.host = liblo.Address( self.hostIP, self.hostPort )
    except liblo.AddressError, err:
      print str(err)
      sys.exit()
      
  def findHost( self, hostip ):
    """retrieve the host port number"""
    url = hostip + "/SenseWorldDataNetwork"
    
    #fp = open(filename, "wb")
    hostport = HostPort()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.MAXREDIRS, 5)
    curl.setopt(pycurl.CONNECTTIMEOUT, 30)
    curl.setopt(pycurl.TIMEOUT, 300)
    curl.setopt(pycurl.NOSIGNAL, 1)
    curl.setopt(pycurl.WRITEFUNCTION, hostport.body_callback)
    try:
      curl.perform()
    except:
      import traceback
      traceback.print_exc(file=sys.stderr)
      sys.stderr.flush()
    curl.close()
    #print hostport.contents
    self.hostPort = hostport.contents
    del hostport
    
## data!
  def data_for_node( self, nodeid, data ):
    self.network.setNodeData( nodeid, data )

  def data_for_slot( self, nodeid, slotid, data ):
    self.network.setSlotData( nodeid, slotid, data )

  def expected_node( self, nodeid ):
    self.network.addExpectedNode( nodeid )

  def info_node( self, nodeid, label, size, dntype ):
    print "info_node", nodeid, label, size, dntype
    self.network.infoNode( nodeid, label, size, dntype )

  def info_slot( self, nodeid, slotid, label, dntype ):
    self.network.infoSlot( nodeid, slotid, label, dntype )

  def expected_node( self, nodeid ):
    self.network.addExpectedNode( nodeid )

## registering

  def register( self, mycallback = None ):
    self.sendSimpleMessage( "/register" )
    if mycallback != None:
      #if 'register' not in self.callbacks:
      self.callbacks[ 'register' ] = mycallback
    
  def unregister( self, mycallback = None ):
    if mycallback != None:
      #if 'register' not in self.callbacks:
      self.callbacks[ 'unregister' ] = mycallback
    self.sendSimpleMessage( "/unregister" )

  def set_registered( self, state ):
    if state:
      if 'register' in self.dnosc.callbacks:
	self.callbacks['register']( state )
    else:
      if 'unregister' in self.dnosc.callbacks:
	self.callbacks['unregister']( state )
    self.registered = state;
    if self.registered:
      self.queryAll()

## queries
  def queryAll( self ):
    self.sendSimpleMessage( "/query/all" )

  def queryExpected( self ):
    self.sendSimpleMessage( "/query/expected" )

  def queryNodes( self ):
    self.sendSimpleMessage( "/query/nodes" )

  def querySlots( self ):
    self.sendSimpleMessage( "/query/slots" )

  def queryClients( self ):
    self.sendSimpleMessage( "/query/clients" )

  def querySetters( self ):
    self.sendSimpleMessage( "/query/setters" )

  def querySubscriptions( self ):
    self.sendSimpleMessage( "/query/subscriptions" )

## end queries

## subscribe

  def subscribeAll( self ):
    self.sendSimpleMessage( "/subscribe/all" )

  def unsubscribeAll( self ):
    self.sendSimpleMessage( "/unsubscribe/all" )

  def removeAll( self ):
    self.sendSimpleMessage( "/remove/all" )

  def subscribeNode( self, nodeid, mycallback = None ):
    #print mycallback
    if mycallback != None:
      if 'subscribe' not in self.callbacks:
	self.callbacks[ 'subscribe' ] = {}
      self.callbacks[ 'subscribe' ][ nodeid ] = mycallback
    msg = liblo.Message( "/subscribe/node", self.port, self.name, nodeid )
    self.sendMessage( msg )
    del msg

  def unsubscribeNode( self, nodeid ):
    msg = liblo.Message( "/unsubscribe/node", self.port, self.name, nodeid )
    self.sendMessage( msg )
    del msg

  def subscribeSlot( self, nodeid, slotid ):
    msg = liblo.Message( "/subscribe/slot", self.port, self.name, nodeid, slotid )
    self.sendMessage( msg )
    del msg

  def unsubscribeSlot( self, nodeid, slotid ):
    msg = liblo.Message( "/unsubscribe/slot", self.port, self.name, nodeid, slotid )
    self.sendMessage( msg )
    del msg

  def getNode( self, nodeid ):
    msg = liblo.Message( "/get/node", self.port, self.name, nodeid )
    self.sendMessage( msg )
    del msg

  def getSlot( self, nodeid, slotid ):
    msg = liblo.Message( "/get/slot", self.port, self.name, nodeid, slotid )
    self.sendMessage( msg )
    del msg

  def setData( self, nodeid, data ):
    msg = liblo.Message( "/set/data", self.port, self.name, nodeid )
    for d in data:
      msg.add( d )
    self.sendMessage( msg )
    del msg

  def labelNode( self, nodeid, label ):
    msg = liblo.Message( "/label/node", self.port, self.name, nodeid, label )
    self.sendMessage( msg )
    del msg

  def labelSlot( self, nodeid, slotid, label ):
    msg = liblo.Message( "/label/slot", self.port, self.name, nodeid, slotid, label )
    self.sendMessage( msg )
    del msg

  def removeNode( self, nodeid ):
    msg = liblo.Message( "/remove/node", self.port, self.name, nodeid )
    self.sendMessage( msg )
    del msg

  def addExpected( self, nodeid, info ):
    msg = liblo.Message( "/set/data", self.port, self.name, nodeid )
    for d in info:
      msg.add( d )
    self.sendMessage( msg )
    del msg

## minibees and hives

  def registerHive( self, number ):
    #self.sendSimpleMessage( "/register/hive" )
    msg = liblo.Message( "/register/hive", self.port, self.name, number )
    self.sendMessage( msg )
    del msg
    
  def unregisterHive( self ):
    self.sendSimpleMessage( "/unregister/hive" )
    
  def set_registered_hive( self, state, minid, maxid ):
    self.registered = state
    if self.registered:
      self.queryAll()
      #self.hive.setNodeRange( minid, maxid )

  def queryHives( self ):
    self.sendSimpleMessage( "/query/hives" )

  # sending info about a minibee created
  def infoMinibee( self, mid, nin, nout ):
    #self.sendSimpleMessage( "/register/hive" )
    msg = liblo.Message( "/info/minibee", self.port, self.name, mid, nin, nout )
    self.sendMessage( msg )
    del msg

  # receiving confirmation of mapped minibee
  def mapped_minibee( self, nodeid, mid ):
    print "mapped minibee output", nodeid, mid

  # receiving confirmation of mapped minibee
  def unmapped_minibee( self, nodeid, mid ):
    print "unmapped minibee output", nodeid, mid

  # receiving confirmation of mapped minibee
  def mapped_minibee_custom( self, nodeid, mid ):
    print "mapped minibee custom", nodeid, mid

  # receiving confirmation of mapped minibee
  def unmapped_minibee_custom( self, nodeid, mid ):
    print "unmapped minibee custom", nodeid, mid

  # receiving minibee information
  def info_minibee( self, mid, nin, nout ):
    print "minibee info:", mid, nin, nout

  # receiving map request output
  def map_minibee( self, nodeid, mid ):
    self.subscribeNode( nodeid )
    # map data from subscribed node to minibee's data output
    msg = liblo.Message( "/mapped/minibee/output", self.port, self.name, nodeid, mid )
    self.sendMessage( msg )
    del msg

  # receiving map request custom
  def map_minibee_custom( self, nodeid, mid ):
    self.subscribeNode( nodeid )
    # map data from subscribed node to minibee's custom output
    msg = liblo.Message( "/mapped/minibee/custom", self.port, self.name, nodeid, mid )
    self.sendMessage( msg )
    del msg

  # receiving unmap request output
  def unmap_minibee( self, nodeid, mid ):
    self.unsubscribeNode( nodeid )
    # unmap data from subscribed node to minibee's data output
    msg = liblo.Message( "/unmapped/minibee/output", self.port, self.name, nodeid, mid )
    self.sendMessage( msg )
    del msg

  # receiving map request custom
  def unmap_minibee_custom( self, nodeid, mid ):
    self.unsubscribeNode( nodeid )
    # unmap data from subscribed node to minibee's custom output
    msg = liblo.Message( "/unmapped/minibee/custom", self.port, self.name, nodeid, mid )
    self.sendMessage( msg )
    del msg


## message sending
  def sendMessage( self, msg ):
    try:
      self.server.send( self.host, msg )
    except liblo.AddressError, err:
      print str(err)
  
  def sendSimpleMessage( self, path ):
    try:
      self.server.send( self.host, path, self.port, self.name )
    except liblo.AddressError, err:
      print str(err)
## end message sending
      
# end class DataNetworkOSC

# begin class DataNode
class DataNode(object):
  def __init__(self, network, nid, insize, label, dtype ):
    #print "new datanode", network, nid, insize, label, dtype
    self.network = network
    self.nodeid = nid
    self.size = insize
    self.label = label
    self.dtype = dtype
    self.action = None
    #print insize
    self.data = list( 0 for i in range( 1, insize+1 ) )    
    self.slotlabels = list( "slot_{0!s}_{1!s}".format( nid, i ) for i in range(1,insize+1) )
    #print "DataNode creation", self.data, self.slotlabels

    
  def setAction( self, action ):
    self.action = action

  def setSize( self, size ):
    self.size = size

  def setType( self, dtype ):
    self.dtype = dtype

  def setLabel( self, label ):
    self.label = label

  def setLabelSlot( self, slotid, label ):
    if slotid < self.size:
      self.slotlabels[slotid] = label

  def setDataSlot( self, slotid, data ):
    if slotid < self.size:
      self.data[slotid] = data
 
  def setData( self, data ):
    if len( data ) == self.size :
      self.data = data
      if self.action != None:
	self.action( self.data )

  def sendData( self ):
    self.network.sendData( self.nodeid, self.data )

  def sendLabel( self ):
    self.network.sendLabel( self.nodeid, self.label )


# end class DataNode

# begin class DataNetwork
class DataNetwork(object):
  def __init__(self, hostip, myport, myname, cltype=0, nonodes = 0 ):
    self.osc = DataNetworkOSC( hostip, myport, myname, self, cltype, nonodes )
    self.nodes = {} # contains the nodes we are subscribed to
    self.expectednodes = [] # contains node ids that are expected and could be subscribed to
    
  def addExpectedNode( self, nodeid ):
    self.expectednodes.append( nodeid )
    print "Expected nodes:", self.expectednodes

  def infoNode( self, nodeid, label, size, dntype ):
    #print "Info Node", nodeid, self.nodes, label, size, dntype
    if nodeid not in self.nodes:
      self.nodes[ nodeid ] = DataNode( self, nodeid, size, label, dntype )
      #print self.nodes[ nodeid ]
      #print self.nodes
    else:
      #print self.nodes[ nodeid ]
      #try:
      self.nodes[ nodeid ].setLabel( label )
      self.nodes[ nodeid ].setSize( size )
      self.nodes[ nodeid ].setType( dntype )
      #except:
    if nodeid not in self.nodes:
      print "InfoNode: nodeid ", nodeid, "not in nodes", self.nodes

  def infoSlot( self, nodeid, slotid, label, dntype ):
    if nodeid in self.nodes:
      self.nodes[ nodeid ].setLabelSlot( slotid, label )
    else:
      print "InfoSlot: nodeid ", nodeid, "not in nodes", self.nodes

  def setNodeData( self, nodeid, data ):
    if nodeid in self.nodes:
      self.nodes[ nodeid ].setData( data )
    else:
      print "DataNode: nodeid ", nodeid, "not in nodes", self.nodes

  def setSlotData( self, nodeid, slotid, data ):
    if nodeid in self.nodes:
      self.nodes[ nodeid ].setDataSlot( slotid, data )
    else:
      print "SlotData: nodeid ", nodeid, "not in nodes", self.nodes

  def sendData( self, nodeid, data ):
    self.osc.setData( nodeid, data )

  def sendLabel( self, nodeid, data ):
    self.osc.setLabel( nodeid, data )

# end class DataNetwork

def dataAction( data ):
  print "dataAction", data

def setDataAction( nodeid ):
  global datanetwork
  datanetwork.nodes[ nodeid ].setAction( dataAction )

#def wait( tim ):
  #time.sleep( tim )

if __name__ == "__main__":
  datanetwork = DataNetwork( "127.0.0.1", 57000, "pydon", 0, 20 )
  
  #wait( 2.0 )
  #time.sleep( 1.0 )
  
  #print datanetwork.nodes
  
  while not datanetwork.osc.registered:
    print "waiting to be registered"
    #print time
    myTime.sleep( 1.0 )
  
  datanetwork.osc.subscribeNode( 1, setDataAction )
  
  raw_input("press enter to quit...\n")

  datanetwork.osc.unregister()
