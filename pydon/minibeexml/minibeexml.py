# -*- coding: utf-8 -*-

#!/usr/bin/python
# Filename: minibeexml.py

import xml.etree.ElementTree as ET

from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


class HiveConfigFile():
  
  #def set_hive( self, hive ):
    #self.hive = hive
    
  def write_file( self, filename, hive ):
    # build a tree structure
    root = ET.Element("xml")

    el_hive = ET.SubElement(root, "hive")
    el_hive.set( "name", hive.name )

    for bid, bee in hive.bees.items():
      #print bee
      el_bee = ET.SubElement(el_hive, "minibee")
      el_bee.set( "serial", str(bee.serial) )
      el_bee.set( "id", str(bee.nodeid) )
      comment = ET.Comment('the id given inside the minibee tag is the unique id or number of the minibee')
      el_bee.append(comment)
      el_bee.set( "revision", str(bee.revision) )
      el_bee.set( "libversion", str(bee.libversion) )
      el_bee.set( "caps", str(bee.caps) )
      el_bee.set( "name", str(bee.name) )
      if bee.cid > 0:
	el_beeConfig = ET.SubElement( el_bee, "configuration" )
	comment = ET.Comment('the id given inside the configuration tag is the unique id of the configuration that is used')
	el_beeConfig.append(comment)
	el_beeConfig.set( "id", str(bee.config.configid) )
	el_beeConfig.set( "name", str(bee.config.name) )
      else:
	comment = ET.Comment('This minibee has no configuration yet!')
	el_bee.append(comment)
	el_beeConfig = ET.SubElement( el_bee, "configuration" )
	comment = ET.Comment('the id given inside the configuration tag is the unique id of the configuration that is used; change it to one of the configurations in this file')
	el_beeConfig.append(comment)
	el_beeConfig.set( "id", str(bee.cid) )

      if bee.hasCustom:
	el_beeCustom = ET.SubElement( el_bee, "custom" )
	for cusD in bee.customData.items():
	  el_customData = ET.SubElement( el_beeCustom, "data" )
	  el_customData.set( "id", str(cusD.cid) )
	  el_customData.set( "size", str(cusD.size) )
	  el_customData.set( "offset", str(cusD.offset) )
	  el_customData.set( "scale", str(cusD.scale) )
	  el_customData.set( "name", str(cusD.name) )

      #el_beeConfig.set( "name", "" )
      #ET.dump( el_bee )
      #el_beeCustom = ET.SubElement( el_bee, "custom" )
      #for pin in bee.custompins:
	#el_pin = ET.SubElement( el_bee, "pin" )
	#el_pin.set( "id", pin.name )
	#el_pin.set( "type", pin.type )
	#el_pin.set( "size", pin.size )

      #el_beeCustom.set( "id", bee.config.configid )
      #el_beeCustom.set( "name", bee.config.name )

 
    for cid, cfg in hive.configs.items():
      #print cfg
      el_cfg = ET.SubElement(el_hive, "configuration")
      el_cfg.set( "name", str( cfg.name ) )
      el_cfg.set( "id", str( cfg.configid ) )
      el_cfg.set( "message_interval", str( cfg.messageInterval ) )
      el_cfg.set( "samples_per_message", str( cfg.samplesPerMessage ) )
      for pinkey, pincfg in cfg.pins.items():
	el_pin = ET.SubElement( el_cfg, "pin" )
	el_pin.set( "id", pinkey )
	el_pin.set( "config", pincfg )
	el_pin.set( "name", str( cfg.pinlabels[ pinkey ] ) )
      for did, dev in cfg.twis.items():
	el_twi = ET.SubElement( el_cfg, "twi" )
	el_twi.set( "id", did )
	el_twi.set( "device", dev )
	el_twi.set( "name", str( cfg.twilabels[ did ] ) )
	for sid, sname in cfg.twislotlabels[ did ].items():
	  el_twisl = ET.SubElement( el_twi, "twislot" )
	  el_twisl.set( "id", sid )
	  el_twisl.set( "name", str( sname ) )
    # wrap it in an ElementTree instance, and save as XML
    #tree = ET.ElementTree( root )
    #tree.indent()
    #print root
    #tree.write( filename )
    xmlfile = open(filename,"w")
    xmlfile.write( prettify( root ) )
    xmlfile.close()

    
  def read_file( self, filename ):
    tree = ET.parse( filename )
    # if you need the root element, use getroot
    root = tree.getroot()
    # ...manipulate tree...
    #print root.tag
    hiveconfig = {}
    for node in root:
      hiveconfig['name'] = node.get( "name" )
      hiveconfig['bees'] = {}
      for bee in node.getiterator("minibee"):
	hiveconfig['bees'][ bee.get( "serial" ) ] = {}
	hiveconfig['bees'][ bee.get( "serial" ) ][ "revision" ] = bee.get( "revision" )
	hiveconfig['bees'][ bee.get( "serial" ) ][ "libversion" ] = int( bee.get( "libversion" ) )
	hiveconfig['bees'][ bee.get( "serial" ) ][ "caps" ] = int( bee.get( "caps" ) )
	hiveconfig['bees'][ bee.get( "serial" ) ][ "serial" ] = bee.get( "serial" )
	hiveconfig['bees'][ bee.get( "serial" ) ][ "mid" ] = int( bee.get( "id" ) )
	hiveconfig['bees'][ bee.get( "serial" ) ][ "name" ] = bee.get( "name" )
	for conf in bee.getiterator("config"):
	  hiveconfig['bees'][ bee.get( "serial" ) ][ "configid" ] = int( conf.get( "id" ) )
	  hiveconfig['bees'][ bee.get( "serial" ) ][ "configname" ] = conf.get( "name" )
	for conf in bee.getiterator("configuration"):
	  hiveconfig['bees'][ bee.get( "serial" ) ][ "configid" ] = int( conf.get( "id" ) )
	  hiveconfig['bees'][ bee.get( "serial" ) ][ "configname" ] = conf.get( "name" )
	for custom in bee.getiterator("custom"):
	  hiveconfig['bees'][ bee.get( "serial" ) ][ "customdata" ] = {}
	  for data in custom.getiterator("data"):
	    hiveconfig['bees'][ bee.get( "serial" ) ][ "customdata" ][ int( data.get( "id" ) ) ] = {}
	    hiveconfig['bees'][ bee.get( "serial" ) ][ "customdata" ][ int( data.get( "id" ) ) ][ "size" ] = int( data.get( "size" ) )
	    hiveconfig['bees'][ bee.get( "serial" ) ][ "customdata" ][ int( data.get( "id" ) ) ][ "offset" ] = int( data.get( "offset" ) )
	    hiveconfig['bees'][ bee.get( "serial" ) ][ "customdata" ][ int( data.get( "id" ) ) ][ "scale" ] = int( data.get( "scale" ) )
	    hiveconfig['bees'][ bee.get( "serial" ) ][ "customdata" ][ int( data.get( "id" ) ) ][ "name" ] = data.get( "name" )
	print hiveconfig['bees'][ bee.get( "serial" ) ]

      hiveconfig['configs'] = {}
      for configs in node.getiterator("configuration"):
	hiveconfig['configs'][ configs.get( "id" ) ] = {}
	hiveconfig['configs'][ configs.get( "id" ) ]["cid"] = int( configs.get( "id" ) )
	hiveconfig['configs'][ configs.get( "id" ) ]["name"] = configs.get( "name" )
	hiveconfig['configs'][ configs.get( "id" ) ]["samples_per_message"] = int( configs.get( "samples_per_message" ) )
	hiveconfig['configs'][ configs.get( "id" ) ]["message_interval"] = int( configs.get( "message_interval" ) )
	hiveconfig['configs'][ configs.get( "id" ) ]["pins"] = {}
	hiveconfig['configs'][ configs.get( "id" ) ]["pinlabels"] = {}
	#print configs.getiterator("pin")
	for pin in configs.getiterator("pin"):
	  #print pin
	  hiveconfig['configs'][ configs.get( "id" ) ]["pins"][ pin.get("id") ] = pin.get( "config" )
	  hiveconfig['configs'][ configs.get( "id" ) ]["pinlabels"][ pin.get("id") ] = pin.get( "name" )
	hiveconfig['configs'][ configs.get( "id" ) ]["twis"] = {}
	hiveconfig['configs'][ configs.get( "id" ) ]["twilabels"] = {}
	hiveconfig['configs'][ configs.get( "id" ) ]["twislots"] = {}
	for twi in configs.getiterator("twi"):
	  #print twi
	  hiveconfig['configs'][ configs.get( "id" ) ]["twis"][ twi.get("id") ] = twi.get( "device" )
	  hiveconfig['configs'][ configs.get( "id" ) ]["twilabels"][ twi.get("id") ] = twi.get( "name" )
	  hiveconfig['configs'][ configs.get( "id" ) ]["twislots"][ twi.get("id") ] = {}
	  for twislot in configs.getiterator("twislot"):
	    hiveconfig['configs'][ configs.get( "id" ) ]["twislots"][ twi.get("id") ][ twislot.get("id") ] = twislot.get( "name" )
      #print hiveconfig
      return hiveconfig

#<twislot id="0" label="x">

# main program

if __name__ == "__main__":
  cfgfile = HiveConfigFile()
  cfgfile.read_file( "hiveconfig.xml" )
