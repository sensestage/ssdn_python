from pydonlogger import *
import metapydonhive
import swpydonhive
import minihiveosc
import minihivejunxion

try:
  import lmpydonhive
  #from lmpydonhive import *
except:
  pydon_have_libmapper = False
  #print( "libmapper not available" )
