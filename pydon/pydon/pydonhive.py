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

import serial
import time
import sys
import os
import datetime
import math
import threading
import copy

import optparse
#print time

#from pydon 
import minibeexml
from hiveserial import HiveSerial # AT based communication
from hiveserialapi import HiveSerialAPI # API based communication (in development)

from collections import deque

## {{{ http://code.activestate.com/recipes/210459/ (r2)
class QueueFifo:
    """A sample implementation of a First-In-First-Out
       data structure."""
    def __init__(self):
        self.in_stack = []
        self.out_stack = []
    def size(self):
      return ( len( self.out_stack ) + len( self.in_stack ) )
    def push(self, obj):
        self.in_stack.append(obj)
    def pop(self):
        if not self.out_stack:
            self.in_stack.reverse()
            self.out_stack = self.in_stack
            self.in_stack = []
        if len( self.out_stack ) > 0:
            return self.out_stack.pop()
        else:
            return None
## end of http://code.activestate.com/recipes/210459/ }}}

### convenience function
def find_key(dic, val):
  #
  """return the key of dictionary dic given the value"""
  #
  return [k for k, v in dic.iteritems() if v == val][0]

### end convenience function

# beginning of message queue

#class HiveBeeQueue(object):
  #def __init__(self):
    #queue = deque()

  #def addBee( self, bee ):
    
## beginning of message queue


# beginning of serial interface:


# beginning of MiniHive:

class MiniHive(object):
  def __init__(self, serial_port, baudrate = 57600, apiMode = False, poll = None ):
    #self.minibeeCount = 0
    self.name = ""
    self.bees = {}
    self.mapBeeToSerial = {}
    self.configs = {}
    self.apiMode = apiMode
    self.loopbackAction = None
    self.running = True
    self.newBeeAction = None
    self.newConfigAction = None
    self.verbose = False
    self.ignoreUnknown = False
    self.checkXBeeError = False
    #self.redundancy = 10
    self.create_broadcast_bee()
    self.poll = poll
    self.serial_port = serial_port
    self.baudrate = baudrate
    self.serial = None    
    self.countSinceLastData = 0
    self.seriallock = threading.RLock()
    self.osclock = threading.RLock()
    self.createNewFileForUnknownConfig = True
  
  def loopback( self, mid, data ):
    if self.loopbackAction:
      self.loopbackAction( mid, data )
  
  def set_create_newfile_for_unknown( self, state ):
    print( "create new files for unknown minibees", state );
    self.createNewFileForUnknownConfig = state
      
  def start_serial( self ):
    if self.apiMode:
      self.serial = HiveSerialAPI( self.serial_port, self.baudrate )
    else:
      self.serial = HiveSerial( self.serial_port, self.baudrate )
    self.serial.set_verbose( self.verbose )
    self.serial.set_hive( self )
    if self.serial.isOpen():
      self.serial.init_comm()
      self.seriallock.acquire()
      #if self.verbose:
      #print( "lock acquired by thread ", threading.current_thread().name, "announce" )
      self.serial.announce()
      self.seriallock.release()

  def set_ignore_unknown( self, onoff ):
    self.ignoreUnknown = onoff
    print( "ignoring unknown minibees", self.ignoreUnknown )
    
  def set_check_xbee_error( self, onoff ):
    self.checkXBeeError = onoff
    print( "check for xbee errors", self.checkXBeeError )

  def set_verbose( self, onoff ):
    self.verbose = onoff
    if self.serial != None:
      self.serial.set_verbose( onoff )
  
  def set_id_range( self, minid, maxid ):
    self.idrange = range( minid, maxid )
    self.idrange.reverse()
    
  def get_new_minibee_id( self, rid = None ):
    #print self.idrange
    if len( self.idrange ) == 0:
      print( "no more minibee ids available; increase the available number in the startup options!", self.idrange )
      return None
    if rid != None:
      # get a given id, if within range
      if rid in self.idrange:
          self.idrange.remove( rid )
          return rid
      else:
          print( "requested minibee id not in available range", rid, self.idrange )
          return None
    else: # get a new id
      rid = self.idrange.pop()
      #print self.idrange, rid
      return rid

  def gotData( self ):
    self.countSinceLastData = 0

  def run( self ):
    self.hadXBeeError = False 
    #print( "running", self.running )  
    while self.running:
        #if self.verbose:
            #print( "pydonhive run loop: serial open", self.serial.isOpen(), self.countSinceLastData, self.serial.hasXBeeError() )
        if self.serial.isOpen():
            self.countSinceLastData = self.countSinceLastData + 1
            if not self.apiMode:
                self.serial.read_data()
            elif self.checkXBeeError:
                # check whether thread alive, if not start it again
                #if not self.serial.isRunning():
                    #if not self.serial.hasXBeeError():
                        #self.serial.start()   # serial.start is automatic because of dispatch method
                    #else:
                if self.serial.hasXBeeError():
                    print "xbee serial error, closing serial port"
                    self.serial.halt()
                    self.serial.closePort()
                    self.hadXBeeError = True
            elif self.countSinceLastData > 60000: # we did not receive any data for about 60 seconds, something's up, let's close and reopen the serial port
                print "no data for 60 seconds, opening serial port again"
                self.serial.halt()
                self.serial.closePort()
                self.countSinceLastData = 0
                self.hadXBeeError = True
            for beeid, bee in self.bees.items():
                #print beeid, bee
                bee.countsincestatus = bee.countsincestatus + 1
                if bee.countsincestatus > 12000:
                    bee.set_status( 'off' )
                if bee.status == 'waiting':
                    bee.waiting = bee.waiting + 1
                    if bee.waiting > 1000:
                        #self.seriallock.acquire()
                        self.wait_config( beeid, bee.cid, True )
                        #self.seriallock.release()
                        #self.seriallock.acquire()
                        #if self.verbose:
                            #print( "lock acquired by thread ", threading.current_thread().name, "sending me" )
                        #self.serial.send_me( bee.serial, 1 )
                        #self.seriallock.release()
                        #time.sleep( 0.005 )
                else:
                    bee.send_data( self.verbose )
                    #self.seriallock.acquire()
                    #print( "lock acquired by thread ", threading.current_thread().name, "sending output data" )
                    bee.repeat_output( self.serial, self.seriallock, self.verbose )
                    bee.repeat_custom( self.serial, self.seriallock, self.verbose )
                    bee.repeat_run( self.serial, self.seriallock, self.verbose )
                    bee.repeat_loop( self.serial, self.seriallock, self.verbose )
                    #self.seriallock.release()
                    #if bee.status == 'receiving':
                        #bee.count = bee.count + 1
                        #if bee.count > 5000:
                            #bee.count = 0
                    #self.serial.send_me( bee.serial, 0 )
        
        else:
            time.sleep( 0.1 )
            print "serial port is closed, trying to open serial port again"
            #self.seriallock.acquire()
            #if self.verbose:
            #print( "lock acquired by thread ", threading.current_thread().name )
            self.serial.open_serial_port()
            #self.seriallock.release()
            time.sleep( 0.1 )
            if self.serial.isOpen():
                print "serial port is open again"
            #if self.verbose:
                #print( "lock acquired by thread ", threading.current_thread().name )
                self.serial.init_comm() # initComm start the thread
                if not self.hadXBeeError:
                    self.seriallock.acquire()
                    self.serial.announce()
                    self.seriallock.release()
                else:
                    self.hadXBeeError = False
            else:
                print "serial port was not opened"
        if self.poll:
            self.poll()
        else:
            time.sleep(0.001)
    print( "hive loop not running anymore", self.running )

  def exit( self ):
    print( "exiting hive loop" );
    self.running = False
    if self.serial.isOpen():
      self.seriallock.acquire()
      #if self.verbose:
      #print( "lock acquired by thread ", threading.current_thread().name )
      self.serial.quit()
      self.seriallock.release()
    
  def map_serial_to_bee( self, serial, mid ):
    if serial in self.mapBeeToSerial:
      oldid = self.mapBeeToSerial[ serial ]
      if oldid == mid: # do nothing
          return True
      else: # the minibee had an id, and we are assigning a new one
          minibee = self.bees[ oldid ]
          # remove the bee from the list at the old id
          del self.bees[ oldid ]
          # add it with the new id
          minibee.set_nodeid( mid )
          self.bees[ mid ] = minibee
    else:
      if mid in self.bees: # another bee has this ID, return an error message!
          print( "There is already a MiniBee with ID %i (with serial number %s), please assign a different ID"%(mid,self.bees[mid].serial) )
          return False
      else: # there is no minibee with that id, and no minibee yet with the serial, so create a new one:
          minibee = MiniBee( mid, serial )
          self.bees[ mid ] = minibee
          self.mapBeeToSerial[ serial ] = mid
    # if we got to the end, all went well
    return True

  def set_pin_configuration( self, cid, pincfg ):
    if not cid in self.configs:
      print( "There is no configuration with ID %i"%(cid) )
      return False
    config = self.configs[ cid ]
    config.setPinConfig( pincfg[0], pincfg[1] )
    config.setPinLabel( pincfg[0], pincfg[2] )
    return True

  def set_twi_configuration( self, cid, twicfg ):
    if not cid in self.configs:
      print( "There is no configuration with ID %i"%(cid) )
      return False
    config = self.configs[ cid ]
    config.setTwiConfig( twicfg[0], twicfg[1] )
    config.setTwiLabel( twicfg[0], twicfg[2] )
    return True

  def delete_configuration( self, cid ):
    if not cid in self.configs:
      print( "There is no configuration with ID %i"%(cid) )
      return False
    del self.configs[ cid ]
    return True
    
  def query_configurations( self, network ):
    for cid, config in self.configs.items():
      #print( cid, config )
      network.infoConfig( config.getConfigInfo() )

  def set_configuration( self, cid, config ):
    if cid in self.configs:
      # cid already exists - should not overwrite it
      print( "There is already a configuration with ID %i, please use a different ID, or delete this configuration first"%(cid) )
      return False
    newconfig = MiniBeeConfig( cid, config[0], config[1], config[2] ) # cid, name, samples per message, message_interval
    self.configs[ cid ] = newconfig
    numberPins = config[3]
    numberTWIs = config[4]
    #print( len( config ), numberPins, numberTWIs )
    if numberTWIs > 0:
      newconfig.setPinConfig( 'A5', 'TWIClock' )
      newconfig.setPinConfig( 'A4', 'TWIData' )
    pinid = 5
    for pin in range(numberPins):
      newconfig.setPinConfig( config[ pinid ], config[ pinid+1 ] )
      newconfig.setPinLabel( config[ pinid ], config[ pinid+2 ] )
      pinid = pinid + 3
    #twis = config[(numberPins*2 + 5): (numberPins*2+numberTWIs*2+4) ]
    #print ( len( twis ) )
    for tw in range(numberTWIs):
      newconfig.setTwiConfig( config[ pinid ], config[ pinid+1 ] )
      newconfig.setTwiLabel( config[ pinid ], config[ pinid+2 ] )
      #TODO: how to make labels for this?
      pinid = pinid + 3
    # update any minibees which should have this config (only if their config number was updated recently
    for beeid, bee in self.bees.items():
      if bee.cid == cid and bee.has_new_config_id():
          bee.set_config( cid, newconfig )
          if self.serial.isOpen():
              self.seriallock.acquire()
              #if self.verbose:
              #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.send_id( bee.serial, bee.nodeid, bee.cid )
              self.seriallock.release()
          bee.set_status( 'waiting' )
          bee.waiting = 0
    return True
  
  def store_ids( self ):
    if self.apiMode:
      if self.serial.isOpen():
          self.seriallock.acquire()
          #if self.verbose:
          #print( "lock acquired by thread ", threading.current_thread().name )
          self.serial.store_remote_at16( 0xFFFF )
          self.seriallock.release()
    
  def store_minibee_id( self, mid ):
    if self.apiMode:
      if mid in self.bees:
          minibee = self.bees[ mid ]
          if self.serial.isOpen():
              self.seriallock.acquire()
              #if self.verbose:
              #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.store_remote_at64( minibee.serial )
              self.seriallock.release()

  def announce_minibee_id( self, mid ):
    if self.apiMode:
      if mid in self.bees:
          #minibee = self.bees[ mid ]
          print( "sending announce to minibee", mid )
          if self.serial.isOpen():
              self.seriallock.acquire()
              #if self.verbose:
              #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.announce( mid )
              self.seriallock.release()

  def set_minibee_config( self, mid, cid ):
    if mid in self.bees: # if the minibee exists
      minibee = self.bees[ mid ]      
      if cid in self.configs:
          config = self.configs[ cid ]
          minibee.set_config( cid, config )
      else:
          minibee.set_config_id( cid )
      if self.serial.isOpen():
          self.seriallock.acquire()
          #if self.verbose:
          #print( "lock acquired by thread ", threading.current_thread().name )
          self.serial.send_id( minibee.serial, minibee.nodeid, minibee.cid )
          self.seriallock.release()
      minibee.set_status( 'waiting' )
      minibee.waiting = 0
      if self.newBeeAction:
          self.newBeeAction( minibee )

  def create_broadcast_bee( self ):
    mid = 0xFFFF;
    minibee = MiniBee( mid, serial )
    minibee.set_lib_revision( 9, 'F', 0 )
    self.bees[ mid ] = minibee
    if self.newBeeAction: # and firsttimenewbee:  
      self.newBeeAction( minibee )    

  def new_bee_no_config( self, serial, useLock = False ):
    firsttimenewbee = False
    # see if we already have this serial number in our config or minibee set, if so use that minibee
    #self.minibeeCount += 1
    if serial in self.mapBeeToSerial:
      # we already know the minibee, so send it its id and configid
      minibee = self.bees[ self.mapBeeToSerial[ serial ] ]
    else:
      # new minibee, so generate a new id
      mid = self.get_new_minibee_id()
      minibee = MiniBee( mid, serial )
      minibee.set_lib_revision( 9, 'F', 0 ) # FIXME
      self.bees[ mid ] = minibee
      self.mapBeeToSerial[ serial ] = mid
      firsttimenewbee = True
      
    if self.serial.isOpen():
      if useLock:
          self.seriallock.acquire()
          #if self.verbose:
          #print( "lock acquired by thread ", threading.current_thread().name )
      self.serial.send_id( serial, minibee.nodeid )
      if useLock:
          self.seriallock.release()
    if self.newBeeAction: # and firsttimenewbee:  
      self.newBeeAction( minibee )
      
  def reset_hive( self ):
    if self.apiMode:
      #self.seriallock.acquire()
      #if self.verbose:
      #print( "lock acquired by thread ", threading.current_thread().name )
      #FIXME: this needs a cleaner solution
      self.serial.halt()
      self.serial.closePort()
      self.hadXBeeError = True
      #self.seriallock.release()
   
  def reset_bee( self, beeid ):
    if self.apiMode:
      if beeid in self.bees:
          #TODO: this should be a state machine, rather than have busy waits in the loop
          minibee = self.bees[ beeid ]
          if self.serial.isOpen():
              # check whether 5 is right (otherwise 4)
              self.seriallock.acquire()
              #if self.verbose:
              #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.set_digital_out3( minibee.serial, 5 )
              self.seriallock.release()
              #TODO: these should be callbacks:
              time.sleep(0.05)
              self.seriallock.acquire()
              #if self.verbose:
              #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.reset_minibee( minibee.serial )
              self.seriallock.release()
              time.sleep(0.20)
              self.seriallock.acquire()
              #if self.verbose:
              #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.restart_minibee( minibee.serial )
              self.seriallock.release()

  def reset_unknown_bee( self, beeid ):
    if self.apiMode:
      #TODO: this should be a state machine, rather than have busy waits in the loop
      if self.serial.isOpen():
          # check whether 5 is right (otherwise 4)
          self.seriallock.acquire()
          self.serial.set_digital_out3_short( beeid, 5 )
          self.seriallock.release()
          #TODO: these should be callbacks:
          time.sleep(0.05)
          self.seriallock.acquire()
          self.serial.reset_minibee_short( beeid )
          self.seriallock.release()
          time.sleep(0.20)
          self.seriallock.acquire()
          self.serial.restart_minibee_short( beeid )
          self.seriallock.release()

  def new_bee( self, serial, libv, rev, caps, remConf = True, useLock = False ):
    firsttimenewbee = False
    # see if we already have this serial number in our config or minibee set, if so use that minibee
    #self.minibeeCount += 1
    if serial in self.mapBeeToSerial:
      # we already know the minibee, so send it its id and configid
      minibee = self.bees[ self.mapBeeToSerial[ serial ] ]
    else:
      #check whether valid serial number
      #print( "check valid", serial, serial.find( "0013A2" ) );
      if serial.find( "0013A2" ) == 0:
        # new minibee, so generate a new id
        mid = self.get_new_minibee_id()
        minibee = MiniBee( mid, serial )
        minibee.set_lib_revision( libv, rev, caps )
        self.bees[ mid ] = minibee
        self.mapBeeToSerial[ serial ] = mid
        firsttimenewbee = True
      else: ##faulty serial numer
        #if self.verbose:
        print( "faulty serial number", serial )
        return     
    #print minibee
    if bool( remConf ):
        if minibee.cid > 0:
            if self.serial.isOpen():
                if useLock:
                    self.seriallock.acquire()                    
                self.serial.send_id( serial, minibee.nodeid, minibee.cid )
                if useLock:
                    self.seriallock.release()
            #minibee.set_status( 'waiting' )
            minibee.waiting = 0
        elif firsttimenewbee and not self.ignoreUnknown: # this could be different behaviour! e.g. wait for a new configuration to come in
            print( "--------------------------------" )
            print( "no configuration defined for minibee", serial, minibee.nodeid, minibee.name )
            if self.createNewFileForUnknownConfig:
                filename ="newconfig_" + time.strftime("%Y_%b_%d_%H-%M-%S", time.localtime()) + ".xml"
                self.write_to_file( filename )
                print( "Configuration saved to " + filename + " in folder " + os.getcwd() )
                print( "Please adapt (at least define a config id other than -1 for the node), save to a new name, and restart the program with that configuration file. Alternatively send a message with a new configuration (via osc, or via the datanetwork)." )
                print( "Check documentation for details." )
                print( "--------------------------------" )
                if self.newConfigAction != None:
                    self.newConfigAction( filename )
        else:
            if self.serial.isOpen():
                if useLock:
                    self.seriallock.acquire()
                self.serial.send_id( serial, minibee.nodeid )
                if useLock:
                    self.seriallock.release()
    if firsttimenewbee and not self.ignoreUnknown: # this could be different behaviour! e.g. wait for a new configuration to come in
        print( "no configuration defined for minibee", serial, minibee.nodeid, minibee.name )
    if self.newBeeAction: # and firsttimenewbee:
        self.newBeeAction( minibee )
  
  def set_loopbackAction( self, action ):
    self.loopbackAction = action
  
  def set_newBeeAction( self, action ):
    self.newBeeAction = action
    
  def set_newConfigAction( self, action ):
    self.newConfigAction = action

  
  def new_paused( self, beeid, msgid, rssi = 0, useLock = False ):    
    if self.verbose:
        print( "received paused message", beeid, msgid )
    if beeid in self.bees:
        self.bees[ beeid ].set_status( 'paused' )

  def new_active( self, beeid, msgid, rssi = 0, useLock = False ):    
    if self.verbose:
      print( "received active message", beeid, msgid )
    if beeid in self.bees:
      self.bees[ beeid ].set_status( 'active' )

  def new_data( self, beeid, msgid, data, rssi = 0, useLock = False ):    
    if self.verbose:
      print( "received new data", beeid, msgid, data )
    # find minibee, set data to it
    if beeid in self.bees:
      self.gotData()
      self.bees[beeid].parse_data( msgid, data, self.verbose, rssi )
    else:
      print( "received data from unknown minibee", beeid, msgid, data )
      if self.apiMode:
          if beeid == 0xFFFA: #unconfigured minibee
              if self.serial.isOpen():
                  if useLock:
                      self.seriallock.acquire()
                      #if self.verbose:
                      #print( "lock acquired by thread ", threading.current_thread().name )
                  self.serial.announce( 0xFFFA )
                  if useLock:
                      self.seriallock.release()
          else:
              self.reset_unknown_bee( beeid )

  def new_trigger_data( self, beeid, msgid, data, rssi = 0, useLock = False ):    
    if self.verbose:
      print( "received new trigger data", beeid, msgid, data )
    # find minibee, set data to it
    if beeid in self.bees:
      self.gotData()
      self.bees[beeid].parse_trigger_data( msgid, data, self.verbose, rssi )
    else:
      print( "received trigger data from unknown minibee", beeid, msgid, data )
      if self.apiMode and beeid == 0xFFFA: #unconfigured minibee
          if self.serial.isOpen():
              if useLock:
                  self.seriallock.acquire()
                  #if self.verbose:
                  #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.announce( 0xFFFA )
              if useLock:
                  self.seriallock.release()

  def new_private_data( self, beeid, msgid, data, rssi = 0, useLock = False ):    
    if self.verbose:
      print( "received new private data", beeid, msgid, data )
    # find minibee, set data to it
    if beeid in self.bees:
      self.gotData()
      self.bees[beeid].parse_private_data( msgid, data, self.verbose, rssi )
    else:
      print( "received private data from unknown minibee", beeid, msgid, data )
      if self.apiMode and beeid == 0xFFFA: #unconfigured minibee
          if self.serial.isOpen():
              if useLock:
                  self.seriallock.acquire()
              #if self.verbose:
              #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.announce( 0xFFFA )
              if useLock:
                  self.seriallock.release()

  def bee_active( self, beeid, msgid ):
    if beeid in self.bees:
      self.bees[beeid].set_status( 'active', msgid )
    else:
      print( "received active message from unknown minibee", beeid, msgid )
    if self.verbose:
      print( "received active message", beeid, msgid )
    # find minibee, set data to it

  def bee_paused( self, beeid, msgid ):
    if beeid in self.bees:
      self.bees[beeid].set_status( 'pausing', msgid )
    else:
      print( "received paused message from unknown minibee", beeid, msgid )
    if self.verbose:
      print( "received paused message", beeid, msgid )
    # find minibee, set data to it

  def wait_config( self, beeid, configid, useLock = False ):
    #print "sending configuration"
    if beeid in self.bees:
        #print beeid, configid
        if configid == self.bees[ beeid ].cid:
          #self.serial.send_me( self.bees[ beeid ].serial, 1 )
          print( "Sending config message for MiniBee {}, revision {}, firmware {}".format( beeid, self.bees[ beeid ].revision, self.bees[ beeid ].libversion ) )
          configuration = self.configs[ configid ]
          configMsg = configuration.getConfigMessage( self.bees[ beeid ].revision )
          self.bees[ beeid ].set_status( 'waiting' )
          self.bees[ beeid ].waiting = 0
          if self.verbose:
              print( "sent configmessage to minibee", configMsg )
          if self.serial.isOpen():
              if useLock:
                self.seriallock.acquire()
              #if self.verbose:
                #print( "lock acquired by thread ", threading.current_thread().name )
              self.serial.send_config( beeid, configMsg )
              if useLock:
                self.seriallock.release()
            #time.sleep( 0.005 ) #TODO: why are we waiting here?
        else:
            print( "received wait for config from known minibee, but with wrong config", beeid, configid )
    else:
        print( "received wait for config from unknown minibee", beeid, configid )
    #print "end sending configuration"

  def check_config( self, beeid, configid, confirmconfig ):
    #print( "MiniHive:check_config - confirming configuration" )
    if beeid in self.bees:
      if not self.bees[beeid].status == 'configured':
        if not self.bees[beeid].check_config( configid, confirmconfig, self.verbose ):
          self.wait_config( beeid, configid )
          print( "minibee %i is not configured yet"%beeid )
        else:
          print( "minibee %i is configured"%beeid )
          print( "--------------------------------" )
          if self.serial.isOpen():
              # don't use lock, this is called from the serial thread anyways
              #self.seriallock.acquire()
              #if self.verbose:
                #print( "lock acquired by thread ", threading.current_thread().name )
            self.serial.send_me( self.bees[beeid].serial, 0 )
            #self.seriallock.release()
            #time.sleep( 0.005 ) #TODO: why are we waiting here?
    else:
      print( "received configuration confirmation from unknown minibee", beeid, configid, confirmconfig )
    #minibee.set_config( configuration )
    #serial.send_config( configuration )
    #print "end confirming configuration"
    
  def load_from_file( self, filename ):
    cfgfile = minibeexml.HiveConfigFile()
    hiveconf = cfgfile.read_file( filename )
    if hiveconf != None :
      #print hiveconf
      #print hiveconf[ 'configs' ]
      self.name = hiveconf[ 'name' ]
      for cid, config in hiveconf[ 'configs' ].items():
        #print cid, config
        self.configs[ int( cid ) ] = MiniBeeConfig( config[ 'cid' ], config[ 'name' ], config[ 'samples_per_message' ], config[ 'message_interval' ] )
        self.configs[ int( cid ) ].setRedundancy( config['redundancy' ] );
        #self.configs[ int( cid ) ].setRSSI( config['rssi' ] );
        #print config[ 'pins' ]
        self.configs[ int( cid ) ].setPins( config[ 'pins' ] )
        self.configs[ int( cid ) ].setPinLabels( config[ 'pinlabels' ] )
        self.configs[ int( cid ) ].setTWIs( config[ 'twis' ] )
        self.configs[ int( cid ) ].setTwiLabels( config[ 'twilabels' ] )
        self.configs[ int( cid ) ].setTwiSlotLabels( config[ 'twislots' ] )
        if 'customdata' in config:
            self.configs[ int( cid ) ].set_custom( config[ 'customdata' ] )
        #print self.configs[ int( cid ) ]
    for ser, bee in hiveconf[ 'bees' ].items():
        #print bee
        mid = self.get_new_minibee_id( bee[ 'mid' ] ) # this only works when loading first time and no minibees active
        if mid != bee[ 'mid' ]: # check if minibee was already there and did not yet have a configuration
            mybee = self.bees[ bee['mid'] ]
            print mybee
            if mybee != None:
                print mybee.cid
                if mybee.cid == -1:
                    mid = bee['mid']
                    # should send new config now
                else:
                    print( "WARNING: trying to assign new configuration to running minibee %i, which is already assigned configuration %i"%(bee[ 'mid' ],mybee.cid) )
        if mid == bee[ 'mid' ]:
            print "assigning minibee"
            self.mapBeeToSerial[ ser ] = bee[ 'mid' ]
            if self.apiMode: # api mode
                if len( bee['serial'] ) == 14:
                    self.bees[ bee[ 'mid' ] ] = MiniBee( bee[ 'mid' ], "00" + bee[ 'serial' ] )
                else:
                    self.bees[ bee[ 'mid' ] ] = MiniBee( bee[ 'mid' ], bee[ 'serial' ] )
            else: # not api mode
                if len( bee['serial'] ) == 16:
                    self.bees[ bee[ 'mid' ] ] = MiniBee( bee[ 'mid' ], bee[ 'serial' ][2:] )
                else:
                    self.bees[ bee[ 'mid' ] ] = MiniBee( bee[ 'mid' ], bee[ 'serial' ] )
            self.bees[ bee[ 'mid' ] ].set_lib_revision( bee[ 'libversion' ], bee[ 'revision' ], bee[ 'caps' ] )
        else:
            print( "WARNING: trying to assign duplicate minibee id %i"%bee[ 'mid' ] )
        print bee[ 'configid' ]
        #thisconf = self.configs[ bee[ 'configid' ] ]
        if bee[ 'configid' ] > 0:
            self.bees[ bee[ 'mid' ] ].set_config( bee[ 'configid' ], self.configs[ bee[ 'configid' ] ] )
        if 'customdata' in bee:
            self.bees[ bee[ 'mid' ] ].set_custom( bee[ 'customdata' ] )

  def write_to_file( self, filename ):
    cfgfile = minibeexml.HiveConfigFile()
    #hiveconf = {}
    #hiveconf[ 'name' ] = filename
    #hiveconf[ 'configs' ] = {}
    #for confid, conf in self.configs.items():
      #hiveconf[ 'configs' ][ confid ] = conf.getConfigForFile()
    #hiveconf[ 'bees' ] = {}
    #for beeid, bee in self.bees.items():
      #hiveconf[ 'bees' ][ beeid ] = bee.getBeeForFile()

    cfgfile.write_file( filename, self )

    #self.bees = {}
    #self.mapBeeToSerial = {}
    #self.configs = {}
    


# end of MiniHive

# custom elements

class MiniBeeCustomConfig(object):
  def __init__(self):
    self.dataInSizes = []
    self.labels = []
    self.dataScales = []
    self.dataOffsets = []
    
  def set_conf( self, customconf ):
    hasCustom = False;
    self.labels = []
    self.dataScales = []
    self.dataOffsets = []
    sortedConf = [ (k,customconf[k]) for k in sorted(customconf.keys())]
    #print sortedConf
    for cid, cdat in sortedConf:
      #print cid, cdat
      hasCustom = True
      self.labels.append( cdat[ "name" ] )
      self.dataScales.append( cdat[ "scale" ] )
      self.dataOffsets.append( cdat[ "offset" ] )
      self.dataInSizes.append( cdat[ "size" ] )
    return hasCustom

# MiniBee Config

class MiniBeeConfig(object):

  analogPins = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']
  digitalPins = [ 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13' ]
  #pinNames =  
  miniBeePinConfig = { 'NotUsed': 0, 'DigitalIn': 1, 'DigitalOut': 2, 'AnalogIn': 3, 'AnalogOut': 4, 'AnalogIn10bit': 5, 'SHTClock': 6, 'SHTData': 7, 'TWIClock': 8, 'TWIData': 9, 'Ping': 10, 'DigitalInPullup': 11, 'Custom': 100, 'Me': 150, 'UnConfigured': 200 };

  miniBeeTwiConfig = { 'ADXL345': 10, 'LIS302DL': 11, 'BMP085': 20, 'TMP102': 30, 'HMC58X3': 40 };
  miniBeeTwiDataSize = { 'ADXL345': [2,2,2], 'LIS302DL': [1,1,1], 'BMP085': [2,3,3], 'TMP102': [2], 'HMC58X3': [2,2,2] };
  miniBeeTwiDataScale = { 'ADXL345': [8191,8191,8191], 'LIS302DL': [255,255,255], 'BMP085': [100,100,100], 'TMP102': [16], 'HMC58X3': [2047,2047,2047] }; # 
  miniBeeTwiDataOffset = { 'ADXL345': [0,0,0], 'LIS302DL': [0,0,0], 'BMP085': [27300,0,10000], 'TMP102': [2048], 'HMC58X3': [2048,2048,2048] };
  miniBeeTwiDataLabels = { 'ADXL345': ['accel_x','accel_y','accel_z'], 'LIS302DL': ['accel_x','accel_y','accel_z'], 'BMP085': ['temperature','barometric_pressure','altitude'], 'TMP102': ['temperature'], 'HMC58X3': ['magn_x','magn_y','magn_z'] };

  def __init__(self, cfgid, cfgname, cfgspm, cfgmint ):
    self.name = cfgname
    self.pins = {}
    self.twis = {}
    self.pinlabels = {}
    self.twilabels = {}
    self.twislotlabels = {}
    self.configid = cfgid
    self.samplesPerMessage = cfgspm
    self.messageInterval = cfgmint
    self.sampleInterval = self.messageInterval / self.samplesPerMessage
    self.dataInSizes = []
    self.dataScales = []
    self.dataOffsets = []
    self.dataOutSizes = []
    self.logDataFormat = []
    self.logDataLabels = []
    self.digitalIns = 0
    self.redundancy = 3
    #self.rssi = False
    self.hasCustom = False
    self.custom = MiniBeeCustomConfig()

  #def getConfigForFile( self ):
    #fileconf = {}
    #fileconf[ 'cid' ] = self.configid
    #fileconf[ 'name' ] = self.name
    #fileconf[ 'samples_per_message' ] = self.samplesPerMessage
    #fileconf[ 'message_interval' ] = self.messageInterval
    #fileconf[ 'pins' ] = self.getPinsForFile()
    #return fileconf

  #def getPinsForFile( self ):
    #filepins = {}
    #for pinname, pinconf in self.pins:
      #filepins[ pinname ] = pinconf
    #return filepins
  
  def setRedundancy( self, redun ):
    self.redundancy = redun
    #print self.redundancy

  #def setRSSI( self, rssi ):
    #self.rssi = rssi
  
  def setPins( self, filepins ):
    #print filepins
    for pinname, pinfunc in filepins.items():
      #print pinname, pinfunc
      self.setPinConfig( pinname, pinfunc ) 

  def setTWIs( self, filetwis ):
    #print filepins
    for pinname, pinfunc in filetwis.items():
      #print pinname, pinfunc
      self.setTwiConfig( pinname, pinfunc ) 

  def setPinLabels( self, filepins ):
    #print filepins
    for pinname, pinfunc in filepins.items():
      #print pinname, pinfunc
      self.setPinLabel( pinname, pinfunc ) 

  def setTwiLabels( self, filepins ):
    #print filepins
    for pinname, pinfunc in filepins.items():
      #print pinname, pinfunc
      self.setTwiLabel( pinname, pinfunc ) 

  def setTwiSlotLabels( self, filepins ):
    #print filepins
    for pinname, pinfunc in filepins.items():
      #print pinname, pinfunc
      #for twislot, twislotlabel in pinfunc.items():
      self.twislotlabels[ pinname ] = pinfunc

  def setPinLabel( self, pinname, pinconfig ):
    self.pinlabels[ pinname ] = pinconfig

  def setTwiLabel( self, pinname, pinconfig ):
    self.twilabels[ pinname ] = pinconfig

  def setPinConfig( self, pinname, pinconfig ):
    if isinstance( pinconfig, int ):
      pinconfig = find_key( MiniBeeConfig.miniBeePinConfig, pinconfig )
    self.pins[ pinname ] = pinconfig

  def setTwiConfig( self, tid, twidev ):
    if isinstance( twidev, int ):
      pinconfig = find_key( MiniBeeConfig.miniBeeTwiConfig, twidev )
    self.twis[ str(tid) ] = twidev

  def getConfigInfo( self ):
    #print "-----MAKING CONFIG MESSAGE------"
    configInfo = []
    configInfo.append( self.configid )
    configInfo.append( self.name )
    configInfo.append( self.samplesPerMessage )
    configInfo.append( self.messageInterval )
    #FIXME: these should be added, but check where this might cause problems
    #configInfo.append( self.redundancy )
    #configInfo.append( self.rssi )

    configInfo.append( len( self.pins ) )
    configInfo.append( len( self.twis ) )
    
    for pid, pincf in self.pins.items():
      configInfo.append( pid )
      configInfo.append( pincf )
      
    for twid, twidev in self.twis.items():
      configInfo.append( "TWI%s"%twid )
      configInfo.append( twidev )
    return configInfo

  def getConfigMessage( self, revision ):
    #print "-----MAKING CONFIG MESSAGE------"
    #print revision
    #print self.pins
    configMessage = []
    configMessage.append( self.configid )
    configMessage.append( self.messageInterval / 256 )
    configMessage.append( self.messageInterval % 256 )
    configMessage.append( self.samplesPerMessage )
    if revision == 'Z':
      digpins = MiniBeeConfig.digitalPins
      anapins = MiniBeeConfig.analogPins[:6]
    else :
      digpins = MiniBeeConfig.digitalPins[1:]
      anapins = MiniBeeConfig.analogPins
    #print( digpins, anapins )
    pinslocal, pinslabels = self.adjust_config( revision )
    #print self.pins, pinslocal
    print "Configuration:", pinslocal
            
    for pinname in digpins:
      if pinname in pinslocal:
          configMessage.append( MiniBeeConfig.miniBeePinConfig[ pinslocal[ pinname ] ] )
      else:
          configMessage.append( MiniBeeConfig.miniBeePinConfig[ 'UnConfigured' ] )

    for pinname in anapins:
      if pinname in pinslocal:
          configMessage.append( MiniBeeConfig.miniBeePinConfig[ pinslocal[ pinname ] ] )
      else:
          configMessage.append( MiniBeeConfig.miniBeePinConfig[ 'UnConfigured' ] )

    configMessage.append( len( self.twis ) )
    #print self.twis
    for twid, twidev in self.twis.items():
      #print twid, twidev
      configMessage.append( MiniBeeConfig.miniBeeTwiConfig[ twidev ] )
    #print configMessage
    #print "-----END MAKING CONFIG MESSAGE------"
    return configMessage

  def set_custom(self, customconf ):
    self.hasCustom = self.custom.set_conf( customconf )
    #print( "set_custom_config", self.hasCustom, self.custom.dataInSizes )

  def adjust_config( self, rev ):
    # for revision F if pin D2 is defined in the configuration, then that replaces the configuration for pin D7      
    pinsconfigs = {}
    pinslabels = {}
    # make a copy
    for pin in self.pins:
        pinsconfigs[ pin ] = self.pins[ pin ]
        pinslabels[ pin ] = self.pinlabels[ pin ]
    # adjust for D2
    if 'D2' in self.pins:
        if rev == 'F':
            pinsconfigs[ 'D7' ] = self.pins[ 'D2' ]
            pinslabels[ 'D7' ] = self.pinlabels[ 'D2' ]
        del pinsconfigs[ 'D2' ]
        del pinslabels[ 'D2' ]
    return pinsconfigs, pinslabels

#MiniBeeConfig
  def check_config( self, libv, rev ):
    #print( "MiniBeeConfig:check_config" )
    #print( "begin check config", self.dataInSizes, self.custom.dataInSizes )
    if self.hasCustom:
      self.dataScales = list( self.custom.dataScales )
      self.dataOffsets = list( self.custom.dataOffsets )
      self.dataInSizes = list( self.custom.dataInSizes )
    else:
      self.dataScales = []
      self.dataOffsets = []
      self.dataInSizes = []
      
    #print "-----CHECKING CONFIG------"
    self.digitalIns = 0
    self.dataOutSizes = []
    self.logDataFormat = []
    self.logDataLabels = []

    if rev == 'Z':
      digpins = MiniBeeConfig.digitalPins
      anapins = MiniBeeConfig.analogPins[:6]
    else :
      digpins = MiniBeeConfig.digitalPins[1:]
      anapins = MiniBeeConfig.analogPins
    pinslocal, pinslabels = self.adjust_config( rev )
    #print "Configuration for MiniBee:", self.nodeid, pinslocal

    if libv >= 4:
      for pinname in digpins + anapins: # iterate over all pins
        if pinname in pinslocal:
            if pinslocal[ pinname ] == 'DigitalIn':
                self.digitalIns = self.digitalIns + 1
                #self.dataInSizes.append( 1 )
                self.dataScales.append( 1 )
                self.dataOffsets.append( 0 )
                self.logDataFormat.append( 1 )
                self.logDataLabels.append( pinslabels[ pinname ] )
            elif pinslocal[ pinname ] == 'DigitalInPullup':
                self.digitalIns = self.digitalIns + 1
                #self.dataInSizes.append( 1 )
                self.dataScales.append( 1 )
                self.dataOffsets.append( 0 )
                self.logDataFormat.append( 1 )
                self.logDataLabels.append( pinslabels[ pinname ] )
            elif pinslocal[ pinname ] == 'DigitalOut':
                self.dataOutSizes.append( 1 )

    for pinname in anapins: # iterate over analog pins
      if pinname in pinslocal:
        if pinslocal[ pinname ] == 'AnalogIn':
            self.dataInSizes.append( 1 )
            self.dataScales.append( 255 )
            self.dataOffsets.append( 0 )
            self.logDataFormat.append( 1 )
            self.logDataLabels.append( pinslabels[ pinname ] )

        elif pinslocal[ pinname ] == 'AnalogIn10bit':
            self.dataInSizes.append( 2 )
            self.dataScales.append( 1023 )
            self.dataOffsets.append( 0 )
            self.logDataFormat.append( 1 )
            self.logDataLabels.append( pinslabels[ pinname ] )

    for pinname in digpins: # iterate over digital pins
      if pinname in pinslocal:
        if pinslocal[ pinname ] == 'AnalogOut':
            self.dataOutSizes.append( 1 )

    if libv <= 3:
      for pinname in digpins + anapins: # iterate over all pins
        if pinname in pinslocal:
            if pinslocal[ pinname ] == 'DigitalIn':
                self.dataInSizes.append( 1 )
                self.dataScales.append( 1 )
                self.dataOffsets.append( 0 )
                self.logDataFormat.append( 1 )
                self.logDataLabels.append( self.pinlabels[ pinname ] )
            elif pinslocal[ pinname ] == 'DigitalOut':
                self.dataOutSizes.append( 1 )

    for pinname in anapins: # iterate over analog pins
      if pinname in pinslocal:
        if pinslocal[ pinname ] == 'TWIData':
            #print "library version" , libv
            if libv <= 2:
                #print "libv 2, revision" , rev
                if rev == 'A':
                    self.dataInSizes.extend( [1,1,1] )
                    self.dataScales.extend( [255,255,255] )
                    self.dataOffsets.extend( [0,0,0] )
                    self.logDataFormat.append( 3 )
                    self.logDataLabels.extend( MiniBeeConfig.miniBeeTwiDataLabels['LIS302DL'] )
                    #print( self.dataInSizes )
                elif rev == 'B':
                    self.dataInSizes.extend( [2,2,2] )
                    #self.dataScales.extend( [1,1,1] )
                    self.dataScales.extend( [8191,8191,8191] )
                    self.dataOffsets.extend( [0,0,0] )
                    self.logDataFormat.append( 3 )
                    self.logDataLabels.extend( MiniBeeConfig.miniBeeTwiDataLabels['ADXL345'] )
                    #print( self.dataInSizes )
            elif libv > 2:
                #print "libv 3, checking twis"
                sortedTwis = [ (k,self.twis[k]) for k in sorted(self.twis.keys())]
                #print sortedTwis
                for twiid, twidev in sortedTwis:
                    #print twiid, twidev
                    self.dataInSizes.extend( MiniBeeConfig.miniBeeTwiDataSize[ twidev ] )
                    self.dataScales.extend( MiniBeeConfig.miniBeeTwiDataScale[ twidev ] )
                    self.dataOffsets.extend( MiniBeeConfig.miniBeeTwiDataOffset[ twidev ] )
                    self.logDataFormat.append( len( MiniBeeConfig.miniBeeTwiDataOffset[ twidev ] ) / len( MiniBeeConfig.miniBeeTwiDataLabels[ twidev ] ) )
                    if twiid in self.twislotlabels:
                        sortedSlotLabels = [ (k,self.twislotlabels[twiid][k]) for k in sorted(self.twislotlabels[ twiid ].keys())]
                        for index, twislotlabel in sortedSlotLabels:
                            #print ( "before", index, twislotlabel )
                            if twislotlabel == None: # use the default
                                twislotlabel = MiniBeeConfig.miniBeeTwiDataLabels[ twidev ][ index ]
                            self.logDataLabels.append( twislotlabel )
                            #print ("after", index, twislotlabel )
                    else:
                        self.logDataLabels.extend( MiniBeeConfig.miniBeeTwiDataLabels[ twidev ] )
                    #print self.dataInSizes

    for pinname in digpins + anapins: # iterate over all pins
      if pinname in pinslocal:
        if pinslocal[ pinname ] == 'SHTData':
            self.dataInSizes.extend( [2,2] )
            self.dataScales.extend( [1,1] )
            self.dataOffsets.extend( [0,0] )
            self.logDataFormat.extend( [1,1] )
            self.logDataLabels.extend( ['temperature','humidity'] )

    for pinname in digpins + anapins: # iterate over all pins
      if pinname in pinslocal:
        if pinslocal[ pinname ] == 'Ping':
            self.dataInSizes.append( 2 )
            self.dataScales.append( 61.9195 )
            self.dataOffsets.append( 0 )
            self.logDataFormat.append( 1 )
            self.logDataLabels.append( pinslabels[ pinname ] )  
    #print( "end check config", self.dataInSizes, self.custom.dataInSizes )
    #if self.verbose:
    #print self.digitalIns, self.dataInSizes, self.dataOutSizes, self.dataScales
    #print self.logDataFormat, self.logDataLabels
    #print "-----END CHECKING CONFIG------"
   
# end MiniBee Config

#minibee_example_config = [ 0, 50, 1 ]
#minibee_example_pinconfig = [
#// null, config id, msgInt high byte, msgInt low byte, samples per message
  #'NotUsed', 'NotUsed', 'NotUsed', 'NotUsed', 'NotUsed', 'NotUsed',  #// D3 to D8
  #'NotUsed', 'NotUsed', 'NotUsed', 'NotUsed', 'NotUsed',  #// D9,D10,D11,D12,D13
  #'NotUsed', 'NotUsed', 'NotUsed', 'NotUsed', 'TWIClock', 'TWIData', 'NotUsed', 'NotUsed' #// A0, A1, A2, A3, A4, A5, A6, A7
#];



# class minibee
class MiniBee(object):
  def __init__(self, mid, serial ):
    self.init_with_serial( mid, serial )
    self.msgID = 0
    self.lastRecvMsgID = 255
    self.name = "";
    self.dataOffsets = []
    self.dataScales = []
    self.hasCustom = False
    self.redundancy = 1
    self.custom = MiniBeeCustomConfig()
    #self.customDataInSizes = []
    #self.customLabels = []
    #self.customDataScales = []
    #self.customDataOffsets = []
    self.dataQueue = QueueFifo()
    #self.time_since_last_message = 0
    self.time_since_last_update = 0
      
  def incMsgID( self ):
    self.msgID = self.msgID + 1
    self.msgID = self.msgID%255
  
  def set_lib_revision( self, libv, revision, caps ):
    self.libversion = libv
    if isinstance( revision, int ):
      self.revision = chr( revision )
    else:
      self.revision = revision
    self.caps = caps    
    
  def init_with_serial(self, mid, serial ):
    self.nodeid = mid
    self.serial = serial
    self.cid = -1
    self.status = 'init'
    self.config = None
    
    self.logAction = None
    self.infoAction = None
    self.statusAction = None
    self.dataAction = None
    self.rssiAction = None
    self.firstDataAction = None
    self.triggerDataAction = None
    self.privateDataAction = None
    #self.configid = -1
    self.waiting = 0
    self.count = 0
    
    self.countsincestatus = 0

    self.outrepeated = 0
    self.outMessage = None
    self.customrepeated = 0
    self.customMessage = None
    self.runrepeated = 0
    self.runMessage = None
    self.looprepeated = 0
    self.loopMessage = None
    #self.redundancy = 3
    self.time_of_last_update = time.time()
    
  def set_nodeid( self, mid ):
    self.nodeid = mid

  #def getBeeForFile( self ):
    #filebee = {}
    #filebee[ 'mid' ] = self.nodeid
    #filebee[ 'serial' ] = self.serial
    #filebee[ 'libversion' ] = self.libversion
    #filebee[ 'revision' ] = self.revision
    #filebee[ 'caps' ] = self.caps
    #filebee[ 'configid' ] = self.configid
    #return filebee

  def set_config_id( self, cid ):
    self.cid = cid
    
  def has_new_config_id( self ):
    if self.config.configid != self.cid:
      return True
    return False

  def set_config(self, cid, configuration ):
    #print( "MiniBee:set_config" );
    #print "set_config", self.nodeid, cid, configuration.pins
    self.cid = cid
    self.config = copy.deepcopy( configuration )
    self.dataScales = list(self.custom.dataScales)
    self.dataOffsets = list(self.custom.dataOffsets)

    self.config.check_config( self.libversion, self.revision )
    #self.dataScales = self.customDataScales
    #self.dataOffsets = self.customDataOffsets
    self.dataScales.extend( self.config.dataScales )
    self.dataOffsets.extend( self.config.dataOffsets )
    #self.dataScales.extend( configScales )
    #self.dataOffsets.extend( configOffsets )
    
    self.redundancy = self.config.redundancy
    self.measuredInterval = self.config.messageInterval
    self.measuredSampleInterval = self.config.messageInterval / self.config.samplesPerMessage
    self.currentMessageTime = time.time()
    #print( "set_config", self.dataScales, self.custom.dataInSizes, self.custom.dataScales )

  def set_custom(self, customconf ):
    self.hasCustom = self.custom.set_conf( customconf )
    #print( "set_custom", self.hasCustom, self.custom.dataInsizes )
    #self.customLabels = []
    #self.customDataScales = []
    #self.customDataOffsets = []
    #sortedConf = [ (k,customconf[k]) for k in sorted(customconf.keys())]
    ##print sortedConf
    #for cid, cdat in sortedConf:
      ##print cid, cdat
      #self.hasCustom = True
      #self.customLabels.append( cdat[ "name" ] )
      #self.customDataScales.append( cdat[ "scale" ] )
      #self.customDataOffsets.append( cdat[ "offset" ] )
      #self.customDataInSizes.append( cdat[ "size" ] )
    self.dataScales = list( self.custom.dataScales )
    self.dataScales.extend( self.config.dataScales )
    self.dataOffsets = list( self.custom.dataOffsets )
    self.dataOffsets.extend( self.config.dataOffsets )
    #print( self.customLabels, self.dataScales, self.dataOffsets, self.customDataInSizes )
    #if len(self.dataScales) == 0:
      #self.dataScales = self.config.dataScales
      #self.dataOffsets = self.config.dataOffsets

  def set_log_action( self, action ):
    self.logAction = action

  def set_action( self, action ):
    self.dataAction = action

  def set_rssi_action( self, action ):
    self.rssiAction = action

  def set_trigger_action( self, action ):
    self.triggerDataAction = action

  def set_private_action( self, action ):
    self.privateDataAction = action

  def set_info_action( self, action ):
    self.infoAction = action

  def set_status_action( self, action ):
    self.statusAction = action

  def set_first_action( self, action ):
    self.firstDataAction = action

  def create_msg( self, msgtype, data, serPort ):
    self.incMsgID()
    msgdata = serPort.create_beemsg( msgtype, self.msgID, data, self.nodeid )
    return msgdata
    
  def send_data( self, verbose = False ):
    if self.cid > 0:
      if self.config != None:
        if self.config.samplesPerMessage > 1:
            nowtime = time.time()
            #self.time_since_last_update = self.time_since_last_update + 1
            #if time_since_last_message > self.messageInterval:
            # timeout on data
            if (nowtime - self.time_of_last_update) >= self.measuredSampleInterval: # if time to send new sample:
                newdata = self.dataQueue.pop()
                #if verbose:
                #print( nowtime, self.time_of_last_update, nowtime-self.time_of_last_update, self.measuredSampleInterval, newdata )
                if newdata != None:
                    self.parse_single_data( newdata, verbose )
                    #self.time_since_last_update = 0
                    self.time_of_last_update = time.time()

  def repeat_output( self, serPort, lock, verbose = False ):
    if self.outMessage != None:
      if self.outrepeated < self.redundancy :
          self.outrepeated = self.outrepeated + 1
          lock.acquire()
          #if serPort.verbose:
          #print( "lock acquired by thread ", threading.current_thread().name, "repeat output", self.nodeid )
          serPort.send_msg( self.outMessage, self.nodeid )
          if verbose:
              print( "sending output message", self.nodeid, self.outMessage );
          lock.release()
          time.sleep( 0.001 ) #TODO: why are we waiting here
    #serPort.send_data( self.nodeid, self.msgID, self.outdata )

  def send_output( self, serPort, data ):
    if self.cid > 0:
        if self.config != None:
            if len( data ) == sum( self.config.dataOutSizes ) :
                self.outdata = data
                self.outrepeated = 0
                self.outMessage = self.create_msg( 'O', self.outdata, serPort )
                #DONT SEND UNTIL CALLED IN THE QUEUE
                #serPort.send_msg( self.outMessage, self.nodeid )
                #serPort.send_data_inclid( self.nodeid, self.msgID, data )
    elif self.nodeid == 0xFFFF: #broadcast node
      self.outdata = data
      self.outrepeated = 0
      self.outMessage = self.create_msg( 'O', self.outdata, serPort )
      #DONT SEND UNTIL CALLED IN THE QUEUE
      #serPort.send_msg( self.outMessage, self.nodeid )

  def repeat_custom( self, serPort, lock, verbose = False ):
    if self.customMessage != None:
      if self.customrepeated < self.redundancy :
          self.customrepeated = self.customrepeated + 1
          lock.acquire()
          #if serPort.verbose:
          #print( "lock acquired by thread ", threading.current_thread().name, "repeat custom", self.nodeid )
          serPort.send_msg( self.customMessage, self.nodeid )
          if verbose:
              print( "sending custom message", self.nodeid, self.customMessage );
          lock.release()
          time.sleep( 0.001 )#TODO: why are we waiting here
    #serPort.send_data( self.nodeid, self.msgID, self.outdata )

  def send_custom( self, serPort, data ):
    self.customdata = data
    self.customrepeated = 0
    self.customMessage = self.create_msg( 'E', self.customdata, serPort )
    #DONT SEND UNTIL CALLED IN THE QUEUE
    #serPort.send_msg( self.customMessage, self.nodeid )
    #if len( data ) == sum( self.config.customOutSizes ) :
    #serPort.send_custom( self.nodeid, data )

  def send_run( self, serPort, status ):
    self.runrepeated = 0
    self.runMessage = self.create_msg( 'R', [ status ], serPort )
    #DONT SEND UNTIL CALLED IN THE QUEUE
    #serPort.send_msg( self.runMessage, self.nodeid )

  def send_loopback( self, serPort, status ):
    self.looprepeated = 0
    self.loopMessage = self.create_msg( 'L', [ status ], serPort )
    #DONT SEND UNTIL CALLED IN THE QUEUE
    #serPort.send_msg( self.loopMessage, self.nodeid )

  def repeat_run( self, serPort, lock, verbose = False ):
    if self.runMessage != None:
      if self.runrepeated < self.redundancy :
          self.runrepeated = self.runrepeated + 1
          lock.acquire()
          #if serPort.verbose:
          #print( "lock acquired by thread ", threading.current_thread().name, "repeat run", self.nodeid )
          serPort.send_msg( self.runMessage, self.nodeid )
          if verbose:
              print( "sending run message", self.nodeid, self.runMessage );
          lock.release()
          time.sleep( 0.001 )#TODO: why are we waiting here
          #serPort.send_data( self.nodeid, self.msgID, self.outdata )

  def repeat_loop( self, serPort, lock, verbose = False ):
    if self.loopMessage != None:
      if self.looprepeated < self.redundancy :
          self.looprepeated = self.looprepeated + 1
          lock.acquire()
          #if serPort.verbose:
          #print( "lock acquired by thread ", threading.current_thread().name, "repeat loop", self.nodeid )
          serPort.send_msg( self.loopMessage, self.nodeid )
          if verbose:
              print( "sending loop message", self.nodeid, self.loopMessage );
          lock.release()
          time.sleep( 0.001 )#TODO: why are we waiting here
    #serPort.send_data( self.nodeid, self.msgID, self.outdata )

  #def set_run( self, serPort, status ):
    # TODO: add redundancy
    #serPort.send_run( self.nodeid, status )
  
  ##def set_loopback( self, serPort, status ):
    # TODO: add redundancy
    #serPort.send_loop( self.nodeid, status )
    
  def set_status( self, status, msgid = 0, verbose = False ):
    if self.statusAction != None :
      if self.status != status:
        self.statusAction( self.nodeid, status )
    self.status = status
    self.countsincestatus = 0
    if verbose:
      print( "minibee status changed: ", self.nodeid, self.status ) 

  def parse_private_data( self, msgid, data, verbose = False, rssi = 0 ):
    if verbose:
      print( "private data - msg ids", msgid, self.lastRecvMsgID )
    if msgid != self.lastRecvMsgID:
      self.lastRecvMsgID = msgid
      #self.time_since_last_message = 0
      if self.cid > 0: # the minibee has a configuration
        #if self.config.rssi:
            #data.append( rssi )
        #print( "private data action:", self.nodeid, self.privateDataAction );
        if self.privateDataAction != None :
            self.privateDataAction( self.nodeid, data )
        if self.rssiAction != None :
            self.rssiAction( self.nodeid, rssi )    

  def parse_trigger_data( self, msgid, data, verbose = False, rssi = 0 ):
    print( "parsing trigger data not yet implemented" )
    if verbose:
      print( "trigger data - msg ids", msgid, self.lastRecvMsgID )
    if msgid != self.lastRecvMsgID:
      self.lastRecvMsgID = msgid
      #self.time_since_last_message = 0
      if self.cid > 0: # the minibee has a configuration
        #if self.config.rssi:
            #data.append( rssi )
        if self.rssiAction != None :
            self.rssiAction( self.nodeid, rssi )
      #TODO: make parser for trigger data
      elif verbose:
        print( "no config defined for this minibee", self.nodeid, data )


  def parse_data( self, msgid, data, verbose = False, rssi = 0 ):
    if verbose:
      print( "msg ids", msgid, self.lastRecvMsgID )
    if msgid != self.lastRecvMsgID:
      self.lastRecvMsgID = msgid
      #self.time_since_last_message = 0
      if self.cid > 0: # the minibee has a configuration
        if self.config.samplesPerMessage == 1:
        #if self.config.rssi:
            #data.append( rssi )
            self.parse_single_data( data, verbose )
        else: # multiple samples per message:
            # TODO: adjust message interval to actually measured interval
            self.previousMessageTime = self.currentMessageTime
            self.currentMessageTime = time.time()
            self.measuredInterval = self.currentMessageTime - self.previousMessageTime
            # clump data into number of samples
            blocks = self.config.samplesPerMessage
            blocksize = len( data ) / blocks
            for i in range( blocks ):
                blockdata = data[ i*blocksize: i*blocksize + blocksize ]
                #if self.config.rssi:
                    #blockdata.append( rssi )
                self.dataQueue.push( blockdata )
            #if verbose:
            self.measuredSampleInterval = self.measuredInterval / max( self.dataQueue.size(), blocks )
            #print( self.measuredInterval, self.dataQueue.size(), self.dataQueue )
        if self.rssiAction != None :
            self.rssiAction( self.nodeid, rssi )
      elif verbose:
        print( "no config defined for this minibee", self.nodeid, data )

  def parse_single_data( self, data, verbose = False ):
    #print "minibee", self.nodeid
    idx = 0
    parsedData = []
    scaledData = []
    for sz in self.custom.dataInSizes:
      parsedData.append( data[ idx : idx + sz ] )
      idx += sz
  #print "index after custom data in size", idx
    #print "before dig", idx
    if self.config.digitalIns > 0:
      # digital data as bits
      nodigbytes = int(math.ceil(self.config.digitalIns / 8.))
      digstoparse = self.config.digitalIns
      digitalData = data[idx : idx + nodigbytes]
      idx += nodigbytes
      #print "index after digitalIn", idx, nodigbytes, digitalData
      for byt in digitalData:
        for j in range(0, min(digstoparse,8) ):
            parsedData.append( [ min( (byt & ( 1 << j )), 1 ) ] )
        digstoparse -= 8
    #else: 
      # digital data as bytes
    #print "after dig", idx

    for sz in self.config.dataInSizes:
      parsedData.append( data[ idx : idx + sz ] )
      idx += sz
    #print parsedData, self.dataScales

    for index, dat in enumerate( parsedData ):
      #print index, dat, self.dataOffsets[ index ], self.dataScales[ index ]
      if len( dat ) == 4 :
        scaledData.append(  float( data[0] * 65536 * 256 + dat[1] * 65536 + dat[2]*256 + dat[3] - self.dataOffsets[ index ] ) / float( self.dataScales[ index ] ) )
      if len( dat ) == 3 :
        scaledData.append(  float( dat[0] * 65536 + dat[1]*256 + dat[2] - self.dataOffsets[ index ] ) / float( self.dataScales[ index ] ) )
      if len( dat ) == 2 :
        scaledData.append(  float( dat[0]*256 + dat[1] - self.dataOffsets[ index ] ) / float( self.dataScales[ index ] ) )
      if len( dat ) == 1 :
        scaledData.append( float( dat[0] - self.dataOffsets[ index ] ) / float( self.dataScales[ index ] ) )
    self.data = scaledData
    
    if len(self.data) == ( len( self.config.dataScales ) + len( self.custom.dataInSizes ) ): ## FIXME: not working correctly yet for custom data in packet
      #if self.config.rssi:
        #self.data.append( data[ idx ]/255. )
      if self.status != 'receiving':
        if self.infoAction != None:
            self.infoAction( self )
        if self.firstDataAction != None:
            self.firstDataAction( self.nodeid, self.data )
            #self.serial.send_me( self.bees[beeid].serial, 0 )
            print ( "receiving data from minibee %i."%(self.nodeid) )
            self.set_status( 'receiving' )
      if self.dataAction != None :
        if not self.dataAction( self.data, self.nodeid ): # if datanode not in nodes, repeat the first data action
            if self.firstDataAction != None:
                self.firstDataAction( self.nodeid, self.data )
            #if verbose:
                #print( "did data action", self.dataAction )
        if self.logAction != None :
            self.logAction( self.nodeid, self.getLabels(), self.getLogData() )
      if verbose:
        print( "data length ok", len(self.data), len( self.config.dataScales ), len( self.custom.dataInSizes ) )
    else:
      print( "data length not ok", len(self.data), len( self.config.dataScales ), len( self.custom.dataInSizes ) )
    if verbose:
      print( "data parsed and scaled", self.nodeid, self.data )
    
  def getLabels( self ):
    labels = self.custom.labels
    labels.extend( self.config.logDataLabels )
    #print( labels )
    #labels = self.config.pinlabels
    #labels.extend( self.config.twilabels )
    return labels
    
  def getLogData( self ):
    logdata = []
    index = 0
    for datasize in self.config.logDataFormat:
      logdata.append( self.data[ index : index + datasize ] )
      index += datasize
    return logdata

  def getInputSize( self ):
    if self.cid > 0:
      size = len( self.dataScales )
      #if self.config.rssi:
        #size = size + 1
      return size
    return 0

  def getOutputSize( self ):
    if self.cid > 0:
      return len( self.config.dataOutSizes )
    return 0

  def check_config( self, configid, confirmconfig, verbose ):
    #print( "MiniBee:check_config" )
    configres = True
    if self.status == 'configured':
        return configres
    if configid == self.cid:
      self.config.check_config( self.libversion, self.revision )
      #print confirmconfig
      #print( "CONFIG INFO", configid, confirmconfig, verbose, len( confirmconfig ) )
      #self.digitalIns = 0
      #self.dataScales = []
      #self.dataOffsets = []
      #print( "custom in 1", self.hasCustom, self.custom.dataInSizes, self.config.custom.dataInSizes )
      
      print( "confirmconfig", confirmconfig )
      
      if len( confirmconfig ) > 4:
        customIns = confirmconfig[5]
        customDataSize = confirmconfig[6]
        customPinCfgs = confirmconfig[7:]
        customPinSizes = 0

        self.customPins = {}

        customDataInSizes = list(self.custom.dataInSizes)
        customDataInSizes.extend( self.config.custom.dataInSizes )
        customDataScales = list(self.custom.dataScales)
        customDataScales.extend( self.config.custom.dataScales )

        #print( "custom in 2", self.hasCustom, customDataInSizes, self.custom.dataInSizes, self.config.custom.dataInSizes )

        #if len( self.custom.dataInSizes ) > 0:
        if len( customDataInSizes ) > 0:
            # there is custom config info in the configuration file, so we take the data from there
            myindex = 0
            customError = False
            #for c in self.custom.dataInSizes:
            for c in customDataInSizes:
                #print c,myindex
                #if ( self.customDataInSizes 
                myindex = myindex + 1
            #print( self.customDataInSizes )
        else:
            self.hasCustom = True
            # we create our own set based on the info sent by the minibee
            self.custom.dataInSizes = [ 0 for x in range( customIns ) ]
            for i in range( len( customPinCfgs ) / 2 ):
                #print ( i, customPinCfgs[i*2], customPinCfgs[i*2 + 1] )
                self.customPins[ customPinCfgs[i*2] ] = customPinCfgs[i*2 + 1]
                customPinSizes = customPinSizes + customPinCfgs[i*2 + 1]
                if customPinCfgs[i*2 + 1]>0:
                    self.custom.dataInSizes.append( customPinCfgs[i*2 + 1] )
            for i in range( customIns ):
                self.custom.dataInSizes[i] = (customDataSize - customPinSizes) / customIns
            for size in self.custom.dataInSizes:
                self.custom.dataOffsets.append( 0 )
                self.custom.dataScales.append( 1 )

      self.dataScales = []
      self.dataOffsets = []

      if self.hasCustom:
        self.dataScales = list( self.custom.dataScales )
        self.dataOffsets = list( self.custom.dataOffsets )

      #print( "custom in 3", self.hasCustom, customDataInSizes, self.custom.dataInSizes, self.config.custom.dataInSizes )
      
      self.dataScales.extend( self.config.dataScales )
      self.dataOffsets.extend( self.config.dataOffsets )
      #print( self.dataScales, self.dataOffsets )
      if confirmconfig[0] == self.config.samplesPerMessage:
        if verbose:
            print( "samples per message correct", confirmconfig[0], self.config.samplesPerMessage )
      else:
        configres = False
        print( "ERROR: samples per message NOT correct", confirmconfig[0], self.config.samplesPerMessage )
      if (confirmconfig[1]*256 + confirmconfig[2]) == self.config.messageInterval :
        if verbose:
            print( "message interval correct", confirmconfig[1:3], self.config.messageInterval )
      else:
          configres = False
          print( "ERROR: message interval NOT correct", confirmconfig[1:3], self.config.messageInterval )
      if confirmconfig[3] == (self.config.digitalIns + sum( self.config.dataInSizes ) + sum( self.custom.dataInSizes )):
        if verbose:
            print( "data input size correct", confirmconfig[3], self.config.digitalIns, self.config.dataInSizes, self.custom.dataInSizes )
      else:
        configres = False
        print( "ERROR: data input size NOT correct", confirmconfig[3], self.config.digitalIns, self.config.dataInSizes, self.custom.dataInSizes )
      if confirmconfig[4] == sum( self.config.dataOutSizes ):
        if verbose:
            print( "data output size correct", confirmconfig[4], self.config.dataOutSizes )
      else:
        configres = False
        print( "ERROR: data output size NOT correct", confirmconfig[4], self.config.dataOutSizes )
      # to add custom in and out
    else:
      configres = False
      print( "ERROR: wrong config number", configid, self.cid )
    if configres:
      self.set_status( 'configured' )
    return configres
      

  def __str__(self):
    return "<minibee {id: %s, serial: %s, libversion: %s, revision: %s, caps: %s, configid: %s}>" % (self.nodeid, self.serial, self.libversion, self.revision, self.caps, self.cid )

# end of class minibee

# main program:


if __name__ == "__main__":
  parser = optparse.OptionParser(description='Create a pydonhive to get data from the minibee network.')
  parser.add_option('-c','--config', action='store', type="string", dest="config",default="pydon/configs/hiveconfig.xml",
                    help='the name of the configuration file for the minibees [default:%s]'% 'pydon/configs/hiveconfig.xml')
  parser.add_option('-a','--apimode', action='store', type="string", dest="apimode",default=False,
                    help='use API mode for communication with the minibees [default:%s]'% False)
  parser.add_option('-m','--nr_of_minibees', type=int, action='store',dest="minibees",default=20,
                    help='the number of minibees in the network [default:%i]'% 20)
  parser.add_option('-v','--verbose', action='store',dest="verbose",default=False,\
      help='verbose printing [default:%i]'% False)
  parser.add_option('-s','--serial', action='store',type="string",dest="serial",default="/dev/ttyUSB0",
                    help='the serial port [default:%s]'% '/dev/ttyUSB0')

  (options,args) = parser.parse_args()

  def printDataAction( data, nodeid ):
    print( nodeid, data )

  hive = MiniHive( options.serial, 57600, options.apimode )
  hive.set_id_range( 2, options.minibees + 1 )
  hive.set_verbose( options.verbose )
  
  hive.load_from_file( options.config )
  #hive.bees[ 1 ].set_action( printDataAction )
  hive.bees[ 2 ].set_action( printDataAction )
  #hive.bees[ 3 ].set_action( printDataAction )
  #hive.bees[ 4 ].set_action( printDataAction )
  #print hive
    
  #hive.write_to_file( "hiveconfig2.xml" )
  try:
    hive.run()
  except (SystemExit, RuntimeError, KeyboardInterrupt, IOError ) :
    hive.exit()
    print( "Done; goodbye" )    
    sys.exit()

