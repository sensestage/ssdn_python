#! /usr/bin/env python2

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

import os
import serial

#if os.name == 'nt': #sys.platform == 'win32':
#	#from pydon.windows.pydon_list_ports_windows import *
#	import pydon_list_ports_windows
#else:

from serial.tools import list_ports
import os

import socket
import sys
import threading

try:
  from Tkinter import *
  import tkFileDialog
except ImportError:
    sys.exit("Tkinter not found")


#import pydon 
import metapydonhive
import pydonlogger

def list_serial_ports():
    # Windows
    if os.name == 'nt':
        # Scan for available ports.
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append('COM'+str(i + 1))
                s.close()
            except serial.SerialException:
                pass
        return available
    else:
        # Mac / Linux
        available = [port[0] for port in list_ports.comports()]
        available.append( '/dev/ttyAMA0' ) # raspberry pi
        return available

class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

class ConfigureMenu:

    def __init__(self, master, hiveapp):
      
      self.hiveapp = hiveapp
      
      vcmd = (master.register(self.OnValidateInteger), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
      #vcmdip = (master.register(self.OnValidateIP), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

      self.advanced = "basic"
      
      self.frame = Frame(master)
      self.frame.pack()
      self.visible = True


      autoframe = LabelFrame( self.frame, text="Autostart", padx=5, pady=5, background="LightBlue" )
      autoframe.grid( row=0, column=3, columnspan=1, rowspan=1, sticky="W" )

      self.autostart = self.addCheckbox( autoframe, "Start automatically next time", 0, 0 )
      #self.autostart[ 'box' ].grid( row=0, column=5, sticky="E" )

      
      modeframe = LabelFrame( self.frame, text="Communication Mode", padx=5, pady=5, background="LightYellow" )
      modeframe.grid( row=0, column=0, columnspan=2, rowspan=1, sticky="W" )
      #Label( modeframe, text="mode" ).grid( row=0, columnspan=4)
      
      if self.hiveapp.mpd.haveLibmapper:
	MODES = [ "datanetwork", "osc", "junxion", "libmapper" ]
      else:
	MODES = [ "datanetwork", "osc", "junxion" ]
    
    
      self.mode = StringVar()
      self.mode.set("datanetwork") # initialize
      #print "initialisation", self.mode.get()
      
      cl = 0
    
      for text in MODES:
            b = Radiobutton( modeframe, text=text, variable=self.mode, value=text, command = self.setMode )
            b.grid( row=0, column = cl )
            cl = cl + 1

      cfframe = LabelFrame( self.frame, text="MiniBee Configuration File", padx=5, pady=5, background="LightYellow" )
      cfframe.grid( row=1, column=0, columnspan=4, sticky="W" )

      self.config =      self.addTextEntry( cfframe, "path", 0, 0, 2, 60 )
      openConfig = Button( cfframe, text="...", command = self.openXMLConfig )
      openConfig.grid( row=0, column=3, columnspan=4 )
      
      serialframe = LabelFrame( self.frame, text="Serial Port", padx=5, pady=5 )
      serialframe.grid( row=2, column=0, columnspan=3, sticky="W" )
      
      self.serialentry = self.createSerialBox( serialframe, 0, 0 )
      #self.serialentry = self.addTextEntry( serialframe, "port", 0, 0, 1, 40 ) #TODO: should select from list of available ports
      self.baudrate = self.createBaudrateBox( serialframe, 0, 1 )
      #self.baudrate =    self.addIntEntry( serialframe, vcmd, "baudrate", 0, 2, 1, 10 ) #TODO: should select from list of possible baudrates ## advanced setting
      updateSerial = Button( serialframe, text="update", command = self.updateSerialBox )
      updateSerial.grid( row=0, column=3, columnspan=1 )


      vbframe = LabelFrame( self.frame, text="Verbosity and logging", padx=5, pady=5 )
      vbframe.grid( row=2, column=3, columnspan=2, sticky="W" )
      
      self.verbose = self.addCheckbox( vbframe, "verbose", 0, 0 )
      self.log = self.addCheckbox( vbframe, "log data", 0, 1 )


      oscframe = LabelFrame( self.frame, text="OpenSoundControl", padx=5, pady=5 )
      oscframe.grid( row=4, column=0, columnspan=4, sticky="W" )

      self.hostip =      self.addTextEntry( oscframe, "IP to send OSC to", 0, 0, 1, 20 )
      self.hostport =    self.addIntEntry( oscframe, vcmd, "Port to send OSC to", 0, 2, 1, 10 )
      
      self.myip = self.createMyIPBox( oscframe, 1, 0 )
      #self.myip =        self.addTextEntry( oscframe, "IP to listen on", 1, 0, 1, 20 ) ## advanced setting #TODO: select from (all = 0.0.0.0; only localhost: 127.0.0.1; only external: check current ip address)
      self.myport =      self.addIntEntry( oscframe, vcmd, "Port to listen on", 1, 2, 1, 10 ) ## advanced setting

      dnframe = LabelFrame( self.frame, text="DataNetwork and MiniBees", padx=5, pady=5 )
      dnframe.grid( row=5, column=0, columnspan=4,  sticky="W" )
      
      self.name =        self.addTextEntry( dnframe, "name in datanetwork", 0, 0, 3, 40 ) ## advanced setting
      self.minibees =    self.addIntEntry( dnframe, vcmd, "max number of minibees", 1, 0, 1, 10 ) ## advanced setting
      self.mboffset =    self.addIntEntry( dnframe, vcmd, "offset of minibees", 1, 2, 1, 10 ) ## advanced setting

      xbframe = LabelFrame( self.frame, text="XBee communication", padx=5, pady=5 )
      xbframe.grid( row=6, column=0, columnspan=4, sticky="W" )

      self.api = self.addCheckbox( xbframe, "api mode", 0, 0 ) ## advanced setting
      self.ignore = self.addCheckbox( xbframe, "ignore new minibees",  0, 1 ) ## advanced setting
      self.xbeeerror = self.addCheckbox( xbframe, "reset serial on error", 0, 2 ) ## advanced setting
      
      lgframe = LabelFrame( self.frame, text="Output logging", padx=5, pady=5 )
      lgframe.grid( row=7, column=0, columnspan=5,  sticky="W" )
      
      self.logfile =  self.addTextEntry( lgframe, "log filename", 0, 0, 3, 60 )
      self.logdir =  self.addTextEntry( lgframe, "log directory", 1, 0, 3, 60 )
      openLogDir = Button( lgframe, text="...", command = self.openLogDirDialog )
      openLogDir.grid( row=1, column=4  )
      self.logclean = self.addCheckbox( lgframe, "delete old log files", 2, 2 ) ## advanced setting
      self.logquiet = self.addCheckbox( lgframe, "no output to console",  2, 3 ) ## advanced setting
      self.loglevel = self.createLogLevelBox( lgframe, 2, 0 )
      
      self.start = Button( self.frame, text="START", command = self.startPydon, background="Red", foreground="Black" )
      self.start.grid( row=8, column=0, columnspan=4 )
      
      self.updateSerialPorts()
      
    def openXMLConfig(self):
      cfile = tkFileDialog.askopenfilename(defaultextension="*.xml", filetypes=[('xml files', '.xml'),('all files', '.*')],initialfile='configs/example_hiveconfig.xml')
      self.config.delete(0, END)
      self.config.insert(0, cfile )
    
    def openLogDirDialog(self):
      cdir = tkFileDialog.askdirectory(initialdir='.', title="choose directory for logfiles")
      self.config.delete(0, END)
      self.config.insert(0, cdir )
    
    def setTextEntry( self, entry, text ):
      entry.delete(0, END)
      entry.insert(0, text )
      
    def setCheckBox( self, cb, value ):
      if value == 'True' or value == True: cb['box'].select()
      else: cb['box'].deselect()
      #print cb, text

    #def setOptionMenuItem( self, menu, text ):
      #print menu, text
      #entry.delete(0, END)
      #entry.insert(0, text )

    def setOptions( self, options ):
      self.mode.set( options.program )
      #print "set options", self.mode.get(), options.program
      #self.setMode( options.program )
      
      self.setTextEntry( self.hostip, options.host )
      self.setTextEntry( self.hostport, options.hport )
      self.myipvar.set( options.ip )
      #self.setOptionMenuItem( self.myip, options.ip )
      
      self.setTextEntry( self.myport, options.port )
      self.setTextEntry( self.name, options.name )
      self.setTextEntry( self.minibees, options.minibees )
      self.setTextEntry( self.mboffset, options.mboffset )
      
      self.serialportvar.set( options.serial )
      self.baudvar.set( options.baudrate )

      self.setCheckBox( self.autostart, options.autostart )
      
      self.setCheckBox( self.verbose, options.verbose )
      self.setCheckBox( self.api, options.apimode )
      self.setCheckBox( self.ignore, options.ignore )
      self.setCheckBox( self.xbeeerror, options.xbeeerror )
      self.setCheckBox( self.log, options.logdata )

      self.setTextEntry( self.config, options.config )
      
      self.loglevelvar.set( options.loglevel )
      self.setCheckBox( self.logclean, options.clean )
      self.setCheckBox( self.logquiet, options.quiet )
      self.setTextEntry( self.logfile, options.logname )
      self.setTextEntry( self.logdir, options.logdir )
      
    def getOptions( self, options ):
      options.program = self.mode.get()
      
      #print "get options", self.mode.get()

      options.host = self.hostip.get()
      options.hport = int(self.hostport.get())
      options.ip = self.myipvar.get()
      options.port = int(self.myport.get())
      options.name = self.name.get()
      options.minibees = int(self.minibees.get())
      options.mboffset = int(self.mboffset.get())
      options.serial = self.serialportvar.get()
      options.baudrate = int(self.baudvar.get())
      options.autostart = self.autostart[ 'var' ].get()
      options.verbose = self.verbose['var'].get()
      options.logdata = self.log['var'].get()
      options.apimode = self.api['var'].get()      
      options.ignore = self.ignore['var'].get()
      options.xbeeerror = self.xbeeerror['var'].get()
      options.config = self.config.get()
      
      options.clean = self.logclean['var'].get()
      options.quiet = self.logquiet['var'].get()
      options.logdir = self.logdir.get()
      options.logname = self.logfile.get()
      options.loglevel = self.loglevelvar.get()
      #print options
      return options
      
    def OnValidateInteger(self, d, i, P, s, S, v, V, W):
        try:
            if S:
              S = int(S)
              returnval = True
            else:
              returnval = False
        except ValueError:
            returnval = False 
        return returnval

    #def OnValidateIP(self, d, i, P, s, S, v, V, W):
	#try: socket.inet_aton(S)
	#except socket.error: return False
	#else: return True
	##else: return S.count('.') == 3

    def createLogLevelBox( self, frame, row, col ):
      logleveloptions = [ 'error', 'info', 'debug' ]
      self.loglevelvar = StringVar()
      self.loglevelvar.set( logleveloptions[0] ) # default value
      Label( frame, text="loglevel" ).grid( row=row, column=col, sticky=W)
      w = OptionMenu( frame, self.loglevelvar, *logleveloptions )
      w.grid( row=row, column=col+1 )
      return w


    def createMyIPBox( self, frame, row, col ):
      ips = [ '0.0.0.0', '127.0.0.1' ]
      try:
	  exips = socket.gethostbyname_ex( socket.gethostname() )[2]
	  ips.extend( exips )
      except socket.gaierror as e:
	  print e
      #print ips
      self.myipvar = StringVar()
      self.myipvar.set( ips[0] ) # default value
      Label( frame, text="IP to listen on" ).grid( row=row, column=col, sticky=W)
      w = OptionMenu( frame, self.myipvar, *ips )
      w.grid( row=row, column=col+1 )
      return w

    def createBaudrateBox( self, frame, row, col ):
      baudrateoptions = [ 57600, 19200 ]
      self.baudvar = IntVar()
      self.baudvar.set( baudrateoptions[0] ) # default value
      Label( frame, text="baudrate" ).grid( row=row, column=col, sticky=W)
      w = OptionMenu( frame, self.baudvar, *baudrateoptions )
      w.grid( row=row, column=col+1 )
      return w
    
    def createSerialBox( self, frame, row, col ):
      serialoptions = self.updateSerialPorts()      
      self.serialportvar = StringVar()
      if len( serialoptions ) == 0:
	serialoptions.append( '' )
      self.serialportvar.set( serialoptions[0] ) # default value
      w = OptionMenu( frame, self.serialportvar, *serialoptions )
      w.grid( row=row, column=col )
      return w
    
    def updateSerialBox( self ):
      serialoptions = self.updateSerialPorts()      
      self.serialportvar = StringVar()
      if len( serialoptions ) == 0:
	serialoptions.append( '' )
      self.serialportvar.set( serialoptions[0] ) # default value
      menu = self.serialentry["menu"]
      menu.delete(0, "end")
      for string in serialoptions:
	menu.add_command(label=string, command=lambda value=string: self.serialportvar.set(value))

    def updateSerialPorts( self ):
        #if os.name == 'nt': #sys.platform == 'win32':
        #    sports = pydon_list_ports_windows.comports()
        #else:
        #    sports = list_ports.comports()
        #print sports
        #a = [x[0] for x in sports ]
        a = list_serial_ports()
        return a
        #return sports

    def startPydon( self ):
      #print( "starting pydon" )
      self.hiveapp.startMPD()
    
    def setMode( self ):
      #print self.mode.get()
        for widget in [ self.name, self.hostip, self.hostport, self.myip, self.myport ]:
            widget.configure( state="disabled" )
        if self.mode.get() == "datanetwork":
        #datanetwork
            for widget in [ self.hostip, self.hostport ]:
                widget.configure( state="normal" )
            if self.advanced == "advanced":
                for widget in [ self.name, self.myip, self.myport ]:
                    widget.configure( state="normal" )
        elif self.mode.get() == "libmapper":
            for widget in [ self.hostip, self.hostport ]:
                widget.configure( state="normal" )
            if self.advanced == "advanced":
                for widget in [ self.name, self.myip ]:
                    widget.configure( state="normal" )
        else:
            for widget in [ self.hostip, self.hostport ]:
                widget.configure( state="normal" )
            if self.advanced == "advanced":
                for widget in [ self.myip, self.myport ]:
                    widget.configure( state="normal" )
    
    def setAdvanced( self, onoff ):
        self.advanced = onoff
        #print self.advanced
        if self.advanced == "basic":
            #print "basic mode"
            for widget in [ self.baudrate, self.name, self.minibees, self.mboffset, self.myip, self.myport, self.api['box'], self.ignore['box'], self.xbeeerror['box'], self.loglevel, self.logfile, self.logdir, self.logclean['box'], self.logquiet['box'] ]:
                widget.configure(state="disabled")
        else:
            #print "advanced mode"
            for widget in [ self.baudrate, self.name, self.minibees, self.mboffset, self.myip, self.myport, self.api['box'], self.ignore['box'], self.xbeeerror['box'], self.loglevel, self.logfile, self.logdir, self.logclean['box'], self.logquiet['box']  ]:
                widget.configure(state="normal")
        self.setMode()

    
    def addCheckbox( self, frame, text, row, column ):
      #myvar = IntVar()
      myvar = BooleanVar()
      ch = Checkbutton( frame, text=text, variable=myvar)
      ch.grid( row=row, column=column )
      return {'var':myvar, 'box':ch }

    def addTextEntry( self, frame, text, row, col=0, colspan=4, width=20 ):
      Label( frame, text=text ).grid( row=row, column=col, sticky=W)
      te = Entry( frame, width=width )
      te.grid( row=row, column=col+1, columnspan=colspan )
      return te

    def addIntEntry( self, frame, validator, text, row, col=0, colspan=4, width=20 ):
      Label( frame, text=text ).grid( row=row, column=col, sticky=W)
      te = Entry( frame, width=width, validate="key", validatecommand = validator )
      te.grid( row=row, column=col+1, columnspan=colspan )
      return te

    def addIPEntry( self, frame, validator, text, row, col=0, colspan=4, width=20 ):
      Label( frame, text=text ).grid( row=row, column=col, sticky=W)
      te = Entry( frame, width=width, validate="key", validatecommand = validator )
      te.grid( row=row, column=col+1, columnspan=colspan )
      return te

    def toggleShow( self ):
        if self.visible:
            self.pi = self.frame.place_info()
            self.frame.pack_forget()
        else:
            self.frame.pack(self.pi)
        self.visible = not self.visible

    #def hello(self):
	#print( "hi there, everyone!" )


class HiveApp( Tk ):

    def __init__(self):
      
      Tk.__init__(self)
      self.title( "Sense/Stage MiniHive - v0.38-dev" )
      
      menubar = Menu(self)

      # create a pulldown menu, and add it to the menu bar
      filemenu = Menu(menubar, tearoff=0)
      #filemenu.add_command(label="Open Defaults", command=self.openDefaultsFile)
      #filemenu.add_command(label="Save Defaults", command=self.saveDefaultsFile)
      #filemenu.add_separator()
      #filemenu.add_command(label="Open Configuration", command=self.openXMLConfig)
      filemenu.add_command(label="Save Configuration", command=self.saveXMLConfig)
      filemenu.add_separator()
      filemenu.add_command(label="Quit", underline=0, command=self.quitProgram, accelerator='Ctrl+Q')
      menubar.add_cascade(label="File", menu=filemenu)
      
      self.bind_all("<Control-q>", self.quitEvent)
      
      optionsmenu = Menu(menubar, tearoff=0)
      self.advanced = StringVar()
      optionsmenu.add_radiobutton(label='Basic', variable=self.advanced, value="basic", command=self.setAdvanced )
      optionsmenu.add_radiobutton(label='Advanced', variable=self.advanced, value="advanced", command=self.setAdvanced )
      self.advanced.set( "basic" )
      menubar.add_cascade(label="Options", menu=optionsmenu)
      

      #helpmenu = Menu(menubar, tearoff=0)
      #helpmenu.add_command(label="About", command=self.hello)
      #menubar.add_cascade(label="Help", menu=helpmenu)

      # display the menu
      self.config(menu=menubar)


      self.frame = Frame(self, height=400)
      self.frame.pack()
    
      self.status = StatusBar(self)
      self.status.pack(side=BOTTOM, fill=X)
      
      self.logOpen = False
      self.logvisible = False
      
      self.pydonRunning = False

    def quitEvent( self, event ):
      self.quitProgram()
    
    def quitProgram( self ):
      if self.pydonRunning:
        self.stopMPD()
      quit()
    
    def openMPD( self ):
      #self.mpd = metapydonhive.MetaPydonHive()
      self.mpd = metapydonhive.MetaPydonHive()
      self.options = self.mpd.readOptions( False )
      #print self.options

    def startMPD( self ):
      self.options = self.configure.getOptions( self.options )
      #print "start MPD", self.options
      self.mpd.setOptions( self.options )
      self.mpd.writeOptions()

      #self.openLogWindow()
      self.toggleLog()
      self.configure.toggleShow()
      self.status.set( "pydon running in %s mode", self.options.program )
      
      self.pydonRunning = True
      
      # Set up the thread to do asynchronous I/O
      # More can be made if necessary
      #self.running = 1
      self.mpdthread = threading.Thread( target=self.mpd.startHive )
      self.mpdthread.start()
      
    
    def stopMPD( self ):
        self.logfile.removeWidgetHandler( self.loghandler )
        #print "stopping mpd"
        self.mpd.stopHive()
        #print "mpd stopped"
        self.mpdthread.join()
        #print "mpdthread joined"
        self.toggleLog()
        self.configure.toggleShow()
        self.setAdvanced()
        self.pydonRunning = False
      
    def setAdvanced( self ):
      #print self.advanced.get()
      self.status.set( "%s configuration mode", self.advanced.get() )
      self.configure.setAdvanced( self.advanced.get() )
      
    def openConfigMenu(self):
      self.openMPD()
      self.configure = ConfigureMenu(self.frame, self )
      self.configure.setOptions( self.options )
      self.setAdvanced()
      if self.options.autostart == 'True' or self.options.autostart == True:
        self.startMPD()
      
    def openLogWindow( self ):
      self.logOpen = True
      self.logvisible = True
      self.logFrame = LabelFrame( self.frame, text="Output" )
      self.logFrame.pack()
      
      self.stopButton = Button( self.logFrame, text="STOP", command=self.stopMPD, background="Red", foreground="Black" )
      self.stopButton.pack()
      
      self.logtext = Text( self.logFrame )
      self.logtext.pack()
      
      self.logfile = pydonlogger.LogFile( self.options, 'stdoutAndErr')
      self.loghandler = pydonlogger.WidgetLogger( self.logtext )
      self.logfile.addWidgetHandler( self.loghandler )
      sys.stdout = self.logfile
      sys.stderr = self.logfile

    def toggleLog( self ):
        #print self.logOpen, s   elf.logvisible
        if self.logOpen:
            if self.logvisible:
                self.logpi = self.logFrame.place_info()
                self.logFrame.pack_forget()
            else:
                self.logfile.addWidgetHandler( self.loghandler )
                self.logtext.delete(1.0, END)
                self.logFrame.pack(self.logpi)
            self.logvisible = not self.logvisible
        else:
            self.openLogWindow()
      
      
    def openDefaultsFile(self):
      tkFileDialog.askopenfilename(defaultextension="*.ini", filetypes=[('ini files', '.ini'), ('all files', '.*')],initialfile='pydondefaults.ini')

    def openXMLConfig(self):
      tkFileDialog.askopenfilename(defaultextension="*.xml", filetypes=[('xml files', '.xml'),('all files', '.*')],initialfile='example_hiveconfig.xml')

    def saveDefaultsFile(self):
      tkFileDialog.asksaveasfilename(defaultextension="*.ini", filetypes=[('ini files', '.ini'), ('all files', '.*')],initialfile='pydondefaults.ini')

    def saveXMLConfig(self):
      filename = tkFileDialog.asksaveasfilename(defaultextension="*.xml", filetypes=[('xml files', '.xml'),('all files', '.*')],initialfile=self.options.config)
      if filename:
        self.mpd.saveConfiguration( filename )

    #def hello(self):
        #p rint( "hi there, everyone! - main window" )


if __name__ == "__main__":

  #root = Tk()
  #root.title( "Sense/Stage MiniHive" )
  #app = HiveApp(root)
  app = HiveApp()
  app.openConfigMenu()
  #app.openLogWindow()

  app.mainloop()
