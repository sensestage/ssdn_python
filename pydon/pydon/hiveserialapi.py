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

# -*- coding: utf-8 -*-
import serial
import time
#import sys
import os
#import datetime

#print time

from xbee import XBee
from xbee.helpers.dispatch import Dispatch

import binascii
import struct

#from pydon 
#import minibeexml

#from collections import deque

## {{{ http://code.activestate.com/recipes/510399/ (r1)
"""
HexByteConversion

Convert a byte string to it's hex representation for output or visa versa.

ByteToHex converts byte string "\xFF\xFE\x00\x01" to the string "FF FE 00 01"
HexToByte converts string "FF FE 00 01" to the byte string "\xFF\xFE\x00\x01"
"""

#-------------------------------------------------------------------------------

def ByteToHex( byteStr ):
    """
    Convert a byte string to it's hex string representation e.g. for output.
    """
    
    # Uses list comprehension which is a fractionally faster implementation than
    # the alternative, more readable, implementation below
    #   
    #    hex = []
    #    for aChar in byteStr:
    #        hex.append( "%02X " % ord( aChar ) )
    #
    #    return ''.join( hex ).strip()        

    return ''.join( [ "%02X" % ord( x ) for x in byteStr ] ).strip()

#-------------------------------------------------------------------------------

def HexToByte( hexStr ):
    """
    Convert a string hex byte values into a byte string. The Hex Byte values may
    or may not be space separated.
    """
    # The list comprehension implementation is fractionally slower in this case    
    #
    #    hexStr = ''.join( hexStr.split(" ") )
    #    return ''.join( ["%c" % chr( int ( hexStr[i:i+2],16 ) ) \
    #                                   for i in range(0, len( hexStr ), 2) ] )
 
    bytes = []

    hexStr = ''.join( hexStr.split(" ") )

    for i in range(0, len(hexStr), 2):
        bytes.append( chr( int (hexStr[i:i+2], 16 ) ) )

    return ''.join( bytes )

class TappedSerial(object):
    def __init__(self, ser):
        self.ser = ser
        
    def inWaiting( self ):
      return self.ser.inWaiting()

    def read(self, *args, **kwargs):
        data = self.ser.read(*args, **kwargs)
        print "Read:", repr(data)
        return data

    def write(self, data, **kwargs):
        print "Wrote:", repr(data)
        return self.ser.write(data, **kwargs)

class HiveSerialAPI(object):
  def __init__(self, serial_port, baudrate = 57600 ):
    #self.init_with_serial( mid, serial, libv, revision, caps)
    #self.serialOpened = False
    #self.hive = hive
    #self.serialport = serial_port
    #self.serialbaudrate = baudrate
    self.serial = serial.Serial()  # open first serial port
    self.serial.baudrate = baudrate
    self.serial.port = serial_port
    
    self.ack_cnt = 0
    self.framecnt = 1
    self.hiveMsgId = 1
    self.logAction = None
    self.verbose = False
    self.open_serial_port()
    
  def init_comm( self ):
    print( "initialising communication through serial port")
    self.tapped_ser = self.serial
    if self.verbose:
      self.tapped_ser = TappedSerial( self.serial )
    self.dispatch = Dispatch( self.tapped_ser )
    self.register_callbacks()
    self.xbee = XBee( self.tapped_ser, callback=self.dispatch.dispatch, escaped=True)
    self.xbee.name = "xbee-thread"

  #def start( self ):
    #self.xbee.start()

  def halt( self ):
    self.xbee.halt()
    self.xbee.join(1) # 1 second timeout to join thread

  def hasXBeeError( self ):
    return self.xbee.hasXBeeError

  def isRunning( self ):
    return self.xbee.is_alive()

  def isOpen( self ):
    return self.serial.isOpen()

  def open_serial_port( self ):
    print( "trying to open serial port" )
    try:
      self.serial.open()      
      #self.serial = serial.Serial( self.serialport, self.serialbaudrate )  # open first serial port
      #self.serialOpened = self.serial.isOpen()
      print( "Opening serial port", self.serial.port, self.serial.isOpen() )
    except:
      #self.serialOpened = False
      print( "could not open serial port", self.serial.port )
      print( "Please make sure your coordinator node is connected to the computer and pass in the right serial port location upon startup, e.g. \'python swpydonhive.py -s /dev/ttyUSB1\'" )
      #os._exit(1)
      #raise SystemExit
      #sys.exit()
      #raise KeyboardInterrupt

  def register_callbacks( self ):
    self.dispatch.register(
      "rfdata", 
      self.rfdata_handler,
      lambda packet: packet['id']=='rx'
    )

    self.dispatch.register(
      "status",
      self.generic_handler, 
      lambda packet: packet['id']=='status'
    )

    self.dispatch.register(
      "tx_status",
      self.txstatus_handler, 
      lambda packet: packet['id']=='tx_status'
    )

    self.dispatch.register(
      "remote_at_response", 
      self.generic_handler, 
      lambda packet: packet['id']=='remote_at_response'
    )

    self.dispatch.register(
      "at_response", 
      self.generic_handler, 
      lambda packet: packet['id']=='at_response'
    )

    self.dispatch.register(
      "rx_io_data", 
      self.generic_handler,
      lambda packet: packet['id']=='rx_io_data'
    )

    self.dispatch.register(
      "rx_io_data_long", 
      self.generic_handler,
      lambda packet: packet['id']=='rx_io_data_long_addr'
    )

    self.dispatch.register(
      "rfdata_long", 
      self.generic_handler,
      lambda packet: packet['id']=='rx_long_addr'
    )

  def generic_handler( self, name, packet ):
    if self.verbose:
      print( name, packet )

  def txstatus_handler( self, name, packet ):
    if self.verbose:
      print "TXStatus Received: ", packet
    if packet['status'] == 0:
      self.ack_cnt = self.ack_cnt - 1
    elif self.verbose:
      if packet['status'] == 1:
	print( "TX, No ACK (Acknowledgement) received" )
      elif packet['status'] == 2:
	print( "TX, CCA failure" )
      elif packet['status'] == 3:
	print( "TX, Purged" )
      #0 = Success
      #1 = No ACK (Acknowledgement) received
      #2 = CCA failure
      #3 = Purged


  def rfdata_handler(self, name, packet):
    if self.verbose:
      print "RFData Received: ", packet
    if packet['rf_data'][0] == 'd' and len( packet[ 'rf_data' ] ) > 1: # minibee sending data
      self.recv_data( packet[ 'rf_data' ][1:], packet[ 'source_addr'], packet['rssi'] )
    elif packet['rf_data'][0] == 't' and len( packet[ 'rf_data' ] ) > 1: # minibee sending trigger data
      self.recv_triggerdata( packet[ 'rf_data' ][1:], packet[ 'source_addr'], packet['rssi'] )      
    elif packet['rf_data'][0] == 'e' and len( packet[ 'rf_data' ] ) > 1: # minibee sending private data
      self.recv_privatedata( packet[ 'rf_data' ][1:], packet[ 'source_addr'], packet['rssi'] )      
    elif packet['rf_data'][0] == 's' and len( packet[ 'rf_data' ] ) > 12:
      if len( packet[ 'rf_data' ] ) > 13 :
	self.parse_serial( packet[ 'rf_data' ][2:10], ord( packet[ 'rf_data' ][10] ), packet[ 'rf_data' ][11], ord( packet[ 'rf_data' ][12] ), ord( packet[ 'rf_data' ][13] ) )
      else:
	self.parse_serial( packet[ 'rf_data' ][2:10], ord( packet[ 'rf_data' ][10] ), packet[ 'rf_data' ][11], ord( packet[ 'rf_data' ][12] ), 1 )
    elif packet['rf_data'][0] == 'w' and len( packet[ 'rf_data' ] ) > 3:
      if self.verbose:
	print( "wait config", packet[ 'rf_data' ][2], packet[ 'rf_data' ][3] )
      self.hive.wait_config( ord(packet[ 'rf_data' ][2]), ord(packet[ 'rf_data' ][3]) )
    elif packet['rf_data'][0] == 'c' and len( packet[ 'rf_data' ] ) > 6: # configuration confirmation
      self.hive.check_config( ord(packet[ 'rf_data' ][2]), ord(packet[ 'rf_data' ][3] ), [ ord(x) for x in packet[ 'rf_data' ][4:] ] )
    elif packet['rf_data'][0] == 'i' and len( packet[ 'rf_data' ] ) > 2: # info message
      print( "info message",  packet, [ ord(x) for x in packet[ 'rf_data' ][2:] ] )
    elif packet['rf_data'][0] == 'p' and len( packet[ 'rf_data' ] ) > 1: # minibee sending pause message
      self.recv_paused( packet['rf_data'][1], packet[ 'source_addr'], packet['rssi'] )      
    elif packet['rf_data'][0] == 'a' and len( packet[ 'rf_data' ] ) > 1: # minibee sending active message
      self.recv_active( packet['rf_data'][1], packet[ 'source_addr'], packet['rssi'] )      
    self.hive.gotData()
    self.log_data( packet )
    
  def set_verbose( self, onoff ):
    self.verbose = onoff
    if onoff:
      print( self.serial )
      print( self.serial.portstr )       # check which port was really used

    
  def set_hive( self, hive ):
    self.hive = hive
    
  def announce( self, nodeid = 0xFFFF ):
    self.send_msg_inc( nodeid, 'A', [] );

  def closePort( self ):
    self.serial.close()

  def quit( self ):
    self.send_msg_inc( 0xFFFF, 'Q', [] );
    self.xbee.halt()
    self.xbee.join() # no timeout to join thread
    self.serial.close()
    
  def incMsgID( self ):
    self.hiveMsgId = self.hiveMsgId + 1
    if self.hiveMsgId > 255:
      self.hiveMsgId = 1

  def send_me( self, ser, onoff ):
    if self.verbose:
      print( "sending bee me", ser, onoff )
    self.send_msg64( ser, 'M', [ chr(onoff) ] )

  def send_id( self, ser, nodeid, configid = 0 ):
    #print ser
    if self.verbose:
      print( "sending bee id", ser, nodeid, configid )
    self.assign_remote_my( ser, nodeid )
    if configid > 0:
      time.sleep(.02)

      datalist = []
      datalist.append( HexToByte( ser ) )
      #datalist.append( ser )
      datalist.append( chr( nodeid ) )
      datalist.append( chr( configid ) )
      self.send_msg_inc( nodeid, 'I', datalist )
    
  def send_config( self, nodeid, configuration ):
    if self.verbose:
      print( "sending configuration", configuration )
    config = [ chr(x) for x in configuration ]
    self.send_msg_inc( nodeid, 'C', config )

  def set_digital_out3( self, serial, rmmy ):
    if self.serial.isOpen():
      rfser = HexToByte( serial )
      #rfser = serial
      destaddr = ''.join( rfser )
      hrm = struct.pack('>H', rmmy)
      self.xbee.send('remote_at', 
	    frame_id='B',
	    dest_addr_long=destaddr,
	    options='\x02',
	    command='D3',
	    parameter=hrm
	    )
    #FIXME: this should be a setting or a separate osc message or something
    #self.store_remote_at64( serial )

  def reset_minibee( self, serial ):
    if self.serial.isOpen():
      rfser = HexToByte( serial )
      #rfser = serial
      destaddr = ''.join( rfser )
      hrm = struct.pack('>H', 8 )
      self.xbee.send('remote_at', 
	    frame_id='C',
	    dest_addr_long=destaddr,
	    options='\x02',
	    command='IO',
	    parameter=hrm
	    )

  def restart_minibee( self, serial ):
    if self.serial.isOpen():
      rfser = HexToByte( serial )
      #rfser = serial
      destaddr = ''.join( rfser )
      hrm = struct.pack('>H', 0 )
      self.xbee.send('remote_at', 
	    frame_id='D',
	    dest_addr_long=destaddr,
	    options='\x02',
	    command='IO',
	    parameter=hrm
	    )

  def assign_remote_my( self, serial, rmmy ):
    if self.serial.isOpen():
      rfser = HexToByte( serial )
      #rfser = serial
      destaddr = ''.join( rfser )
      hrm = struct.pack('>H', rmmy)
      self.xbee.send('remote_at', 
	    frame_id='A',
	    dest_addr_long=destaddr,
	    options='\x02',
	    command='MY',
	    parameter=hrm
	    )
    #FIXME: this should be a setting or a separate osc message or something
    #self.store_remote_at64( serial )

  def store_remote_at64( self, serial ):
    if self.serial.isOpen():
      rfser = HexToByte( serial )
      #rfser = serial
      destaddr = ''.join( rfser )
      #hrm = struct.pack('>H', rmmy)
      self.xbee.send('remote_at', 
	    frame_id='8',
	    dest_addr_long=destaddr,
	    options='\x02',
	    command='WR'
	    #parameter=hrm
	    )

  def store_remote_at16( self, nodeid ):
    if self.serial.isOpen():
      #rfser = HexToByte( serial )
      #rfser = serial
      #destaddr = ''.join( rfser )
      hrm = struct.pack('>H', nodeid)
      self.xbee.send('remote_at', 
	    frame_id='9',
	    dest_addr=hrm,
	    options='\x02',
	    command='WR'
	    #parameter=hrm
	    )

  def create_beemsg( self, msgtype, msgid, msgdata, mid ):
    datalist = [ msgtype ]
    datalist.append( chr(msgid) )
    datalist.extend( [ chr(int(x)) for x in msgdata ] )
    return datalist

  def send_msg( self, datalistin, rmmy ):
    if self.serial.isOpen():
      self.framecnt = self.framecnt + 1
      if self.framecnt == 16:
	self.framecnt = 1
      msgid = chr( self.framecnt )
      self.ack_cnt = self.ack_cnt + 1
      datalist = []
      datalist.extend( datalistin )
      data = ''.join( datalist )
      hrm = struct.pack('>H', rmmy)
      self.xbee.send('tx',
          dest_addr=hrm,
          data=data,
          frame_id=msgid,
          options='\x02'
          )
      if self.verbose:
	print( "sending message to minibee", rmmy, hrm, data, self.ack_cnt )
    
  def send_msg_inc( self, rmmy, msgtype, datalistin ):
    if self.serial.isOpen():
      self.framecnt = self.framecnt + 1
      if self.framecnt == 16:
	self.framecnt = 1
      msgid = chr( self.framecnt )
      self.ack_cnt = self.ack_cnt + 1
      self.incMsgID()
      datalist = [ msgtype ]
      datalist.append( chr( self.hiveMsgId ) )
      datalist.extend( datalistin )
      data = ''.join( datalist )
      hrm = struct.pack('>H', rmmy)
      self.xbee.send('tx',
          dest_addr=hrm,
          options='\x02',
          frame_id=msgid,
          data=data
          )
      if self.verbose:
	print( "sending message to minibee", rmmy, hrm, data, self.ack_cnt )

  def send_msg64( self, ser, msgtype, datalistin ):
    if self.serial.isOpen():
      self.framecnt = self.framecnt + 1
      if self.framecnt == 16:
	self.framecnt = 1
      msgid = chr( self.framecnt )
      self.ack_cnt = self.ack_cnt + 1
      self.incMsgID()
      rfser = HexToByte( ser )
      destaddr = ''.join( rfser )
      datalist = [ msgtype ]
      datalist.append( chr( self.hiveMsgId) )
      datalist.extend( datalistin )
      data = ''.join( datalist )
      self.xbee.send('tx_long_addr',
	    dest_addr=destaddr,
	    data=data,
	    frame_id=msgid,
	    options='\x02'
	    )
      if self.verbose:
	print( "sending message to minibee with long addr", ser, rfser, data, self.ack_cnt )

  def send_run( self, mid, run ):
    if self.verbose:
      print( "sending bee run", mid, run )
    self.send_msg_inc( mid, 'R', [ chr(run) ] )

  def send_loop( self, mid, loop ):
    if self.verbose:
      print( "sending bee loop", mid, loop )
    self.send_msg_inc( mid, 'L', [ chr(loop) ] )

  def parse_serial( self, rfser, libv, rev, caps, remConf ): # later also libv, rev, caps
    sser = ByteToHex( rfser )
    if self.verbose:
      print( sser, libv, rev, caps, remConf )
    #self.hive.new_bee_no_config( sser )
    self.hive.new_bee( sser, libv, rev, caps, remConf )

  def recv_data( self, rfdata, source, rfrssi ):
    data = []
    for x in rfdata[1:]:
      data.append( int( ByteToHex( x ), 16 ) )    
    nid = int( ByteToHex( source ), 16 )
    rssi = int( ByteToHex( rfrssi ), 16 )
    msgid = int( ByteToHex( rfdata[0] ), 16 )
    if self.verbose:
      print( "receiving data from minibee", nid, msgid, data, rssi )
    self.hive.new_data( nid, msgid, data, rssi )

  def recv_triggerdata( self, rfdata, source, rfrssi ):
    data = []
    for x in rfdata[1:]:
      data.append( int( ByteToHex( x ), 16 ) )    
    nid = int( ByteToHex( source ), 16 )
    rssi = int( ByteToHex( rfrssi ), 16 )
    msgid = int( ByteToHex( rfdata[0] ), 16 )
    if self.verbose:
      print( "receiving trigger data from minibee", nid, msgid, data, rssi )
    self.hive.new_trigger_data( nid, msgid, data, rssi )

  def recv_privatedata( self, rfdata, source, rfrssi ):
    data = []
    for x in rfdata[1:]:
      data.append( int( ByteToHex( x ), 16 ) )    
    nid = int( ByteToHex( source ), 16 )
    rssi = int( ByteToHex( rfrssi ), 16 )
    msgid = int( ByteToHex( rfdata[0] ), 16 )
    if self.verbose:
      print( "receiving private data from minibee", nid, msgid, data, rssi )
    self.hive.new_private_data( nid, msgid, data, rssi )

  def recv_paused( self, msgid, source, rfrssi ):
    nid = int( ByteToHex( source ), 16 )
    rssi = int( ByteToHex( rfrssi ), 16 )
    msgid = int( ByteToHex( msgid ), 16 )
    if self.verbose:
      print( "receiving paused data from minibee", nid, msgid, rssi )
    self.hive.new_paused( nid, msgid, rssi )

  def recv_active( self, msgid, source, rfrssi ):
    nid = int( ByteToHex( source ), 16 )
    rssi = int( ByteToHex( rfrssi ), 16 )
    msgid = int( ByteToHex( msgid ), 16 )
    if self.verbose:
      print( "receiving active data from minibee", nid, msgid, rssi )
    self.hive.new_active( nid, msgid, rssi )

  def set_log_action( self, action ):
    self.logAction = action

  def log_data( self, packet ):
    nid = int( ByteToHex( packet[ 'source_addr' ] ), 16 )
    rssi = int( ByteToHex( packet[ 'rssi' ] ), 16 )
    #msgid = int( ByteToHex( packet[ 'rfdata' ][1] ), 16 )    
    data = []
    data.append( nid )
    data.append( rssi )
    data.append( packet[ 'rf_data' ][0] )
    for x in packet[ 'rf_data' ][1:]:
      data.append( int( ByteToHex( x ), 16 ) )    
    #print "receiving data"
    if self.logAction != None :
      self.logAction( data )

# end of HiveSerialAPI
