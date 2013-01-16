# File: hello2.py

from serial.tools import list_ports
import socket

from Tkinter import *
import tkFileDialog

import metapydonhive
import pydonlogger

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

    def __init__(self, master):
      
      
      vcmd = (master.register(self.OnValidateInteger), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
      #vcmdip = (master.register(self.OnValidateIP), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

      self.advanced = "basic"
      
      self.frame = Frame(master)
      self.frame.pack()
      
      modeframe = LabelFrame( self.frame, text="Communication Mode", padx=5, pady=5, background="LightYellow" )
      modeframe.grid( row=0, column=0, columnspan=4, rowspan=1, sticky="W" )
            
      #Label( modeframe, text="mode" ).grid( row=0, columnspan=4)
      
      MODES = [
        ("datanetwork", "D"),
        ("osc", "O"),
        ("junxion", "J"),
        ("libmapper", "M"),
      ]
    
      self.mode = StringVar()
      self.mode.set("D") # initialize
      
      cl = 0
    
      for text, mode in MODES:
        b = Radiobutton( modeframe, text=text, variable=self.mode, value=mode, command = self.setMode )
        b.grid( row=0, column = cl )
        cl = cl + 1
        
      cfframe = LabelFrame( self.frame, text="MiniBee Configuration File", padx=5, pady=5, background="LightYellow" )
      cfframe.grid( row=1, column=0, columnspan=4, sticky="W" )
        
      self.config =      self.addTextEntry( cfframe, "path", 0, 0, 2, 60 )
      openConfig = Button( cfframe, text="...", command = self.openXMLConfig )
      openConfig.grid( row=0, column=3, columnspan=4 )
      
      serialframe = LabelFrame( self.frame, text="Serial Port", padx=5, pady=5 )
      serialframe.grid( row=2, column=0, columnspan=2, sticky="W" )
      
      self.serialentry = self.createSerialBox( serialframe, 0, 0 )
      #self.serialentry = self.addTextEntry( serialframe, "port", 0, 0, 1, 40 ) #TODO: should select from list of available ports
      self.baudrate = self.createBaudrateBox( serialframe, 0, 2 )
      #self.baudrate =    self.addIntEntry( serialframe, vcmd, "baudrate", 0, 2, 1, 10 ) #TODO: should select from list of possible baudrates ## advanced setting

      vbframe = LabelFrame( self.frame, text="Verbosity and logging", padx=5, pady=5 )
      vbframe.grid( row=2, column=2, columnspan=2, sticky="W" )
      
      self.verbose = self.addCheckbox( vbframe, "verbose", self.hello, 0, 0 )
      self.log = self.addCheckbox( vbframe, "log data", self.hello, 0, 1 )


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

      self.api = self.addCheckbox( xbframe, "api mode", self.hello, 8, 0 ) ## advanced setting
      self.ignore = self.addCheckbox( xbframe, "ignore new minibees", self.hello, 8, 1 ) ## advanced setting
      self.xbeeerror = self.addCheckbox( xbframe, "reset serial on error", self.hello, 8, 2 ) ## advanced setting
      
      self.start = Button( self.frame, text="START", command = self.startPydon, background="Red", foreground="Black" )
      self.start.grid( row=9, column=0, columnspan=4 )
      
      self.updateSerialPorts()
      
    def openXMLConfig(self):
      cfile = tkFileDialog.askopenfilename(defaultextension="*.xml", filetypes=[('xml files', '.xml'),('all files', '.*')],initialfile='configs/example_hiveconfig.xml')
      self.config.delete(0, END)
      self.config.insert(0, cfile )
    
    def setTextEntry( self, entry, text ):
      entry.delete(0, END)
      entry.insert(0, text )
      
    def setCheckBox( self, cb, value ):
      if value == 'True': cb['box'].select()
      else: cb['box'].deselect()
      #print cb, text

    #def setOptionMenuItem( self, menu, text ):
      #print menu, text
      #entry.delete(0, END)
      #entry.insert(0, text )

    def setOptions( self, options ):
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
      
      self.setCheckBox( self.verbose, options.verbose )
      self.setCheckBox( self.api, options.apimode )
      self.setCheckBox( self.ignore, options.ignore )
      self.setCheckBox( self.xbeeerror, options.xbeeerror )
      self.setCheckBox( self.log, options.logdata )

      self.setTextEntry( self.config, options.config )
      
    def getOptions( self, options ):
      options.host = self.hostip.get()
      options.hport = self.hostport.get()
      options.ip = self.myip.get()
      options.port = self.myport.get()
      options.name = self.name.get()
      options.minibees = self.minibees.get()
      options.mboffset = self.mboffset.get()
      options.serial = self.serialentry.get()
      options.baudrate = self.baudrate.get()
      options.verbose = self.verbose.get()
      options.apimode = self.api.get()
      options.ignore = self.ignore.get()
      options.xbeeerror = self.xbeeerror.get()
      options.config = self.config.get()
      return options
      
    def OnValidateInteger(self, d, i, P, s, S, v, V, W):
	# valid percent substitutions (from the Tk entry man page)
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget        print "OnValidate:"
        #print "d='%s'" % d
        #print "i='%s'" % i
        #print "P='%s'" % P
        #print "s='%s'" % s
        #print "S='%s'" % S
        #print "v='%s'" % v
        #print "V='%s'" % V
        #print "W='%s'" % W
        # only allow if the string is translatable to an integer
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

    def createMyIPBox( self, frame, row, col ):
      ips = [ '0.0.0.0', '127.0.0.1' ]
      exips = socket.gethostbyname_ex( socket.gethostname() )[2]
      ips.extend( exips )
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
      self.serialportvar.set( serialoptions[0] ) # default value
      w = OptionMenu( frame, self.serialportvar, *serialoptions )
      w.grid( row=row, column=col )
      return w
      
    
    def updateSerialPorts( self ):
      sports = list_ports.comports()
      #print sports
      a = [x[0] for x in sports ]
      return a
      #return sports
    
    def startPydon( self ):
      print( "starting pydon" )
    
    def setMode( self ):
      #print self.mode.get()
      for widget in [ self.name, self.hostip, self.hostport, self.myip, self.myport ]:
	widget.configure( state="disabled" )
      if self.mode.get() == "D":
	#datanetwork
	for widget in [ self.hostip, self.hostport ]:
	  widget.configure( state="normal" )
	if self.advanced == "advanced":
	  for widget in [ self.name, self.myip, self.myport ]:
	    widget.configure( state="normal" )
      elif self.mode.get() == "M":
	for widget in [ self.hostip, self.hostport ]:
	  widget.configure( state="normal" )
	if self.advanced == "advanced":
	  for widget in [ self.name, self.myip ]:
	    widget.configure( state="normal" )
      else:
	for widget in [ self.hostip, self.hostport ]:
	  widget.configure( state="normal" )
	if self.advanced == "advanced":
	  for widget in [ self.hostip, self.myport ]:
	    widget.configure( state="normal" )
    
    def setAdvanced( self, onoff ):
      self.advanced = onoff
      #print self.advanced
      if self.advanced == "basic":
	#print "basic mode"
	for widget in [ self.baudrate, self.name, self.minibees, self.mboffset, self.myip, self.myport, self.api['box'], self.ignore['box'], self.xbeeerror['box'] ]:
	  widget.configure(state="disabled")
      else:
	#print "advanced mode"
	for widget in [ self.baudrate, self.name, self.minibees, self.mboffset, self.myip, self.myport, self.api['box'], self.ignore['box'], self.xbeeerror['box'] ]:
	  widget.configure(state="normal")
      self.setMode()

    
    def addCheckbox( self, frame, text, command, row, column ):
      myvar = IntVar()
      ch = Checkbutton( frame, text=text, variable=myvar, command=command)
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

    def hello(self):
        print( "hi there, everyone!" )


class HiveApp:

    def __init__(self, master):
      
      menubar = Menu(master)

      # create a pulldown menu, and add it to the menu bar
      filemenu = Menu(menubar, tearoff=0)
      filemenu.add_command(label="Open Defaults", command=self.openDefaultsFile)
      filemenu.add_command(label="Save Defaults", command=self.saveDefaultsFile)
      filemenu.add_separator()
      filemenu.add_command(label="Open Configuration", command=self.openXMLConfig)
      filemenu.add_command(label="Save Configuration", command=self.saveXMLConfig)
      filemenu.add_separator()
      filemenu.add_command(label="Exit", command=master.quit)
      menubar.add_cascade(label="File", menu=filemenu)
      
      optionsmenu = Menu(menubar, tearoff=0)
      self.advanced = StringVar()
      optionsmenu.add_radiobutton(label='Basic', variable=self.advanced, value="basic", command=self.setAdvanced )
      optionsmenu.add_radiobutton(label='Advanced', variable=self.advanced, value="advanced", command=self.setAdvanced )
      self.advanced.set( "basic" )
      menubar.add_cascade(label="Options", menu=optionsmenu)
      

      helpmenu = Menu(menubar, tearoff=0)
      helpmenu.add_command(label="About", command=self.hello)
      menubar.add_cascade(label="Help", menu=helpmenu)

      # display the menu
      master.config(menu=menubar)


      self.frame = Frame(master, height=512)
      self.frame.pack()
            
      self.status = StatusBar(master)
      self.status.pack(side=BOTTOM, fill=X)
    
    def openMPD( self ):
      self.mpd = metapydonhive.MetaPydonHive()
      self.options = self.mpd.readOptions()
      self.configure.setOptions( self.options )
      #print self.options

      
    def setAdvanced( self ):
      #print self.advanced.get()
      self.status.set( "%s configuration mode", self.advanced.get() )
      self.configure.setAdvanced( self.advanced.get() )
      
    def openConfigMenu(self):
      self.configure = ConfigureMenu(self.frame)
      self.openMPD()
      self.setAdvanced()
      
    def openLogWindow( self ):
      self.logFrame = LabelFrame( self.frame, text="Output" )
      self.logFrame.pack()
      
      self.logtext = Text( self.logFrame )
      self.logtext.pack()
      
      logfile = pydonlogger.LogFile( self.options, 'stdoutAndErr')
      loghandler = pydonlogger.WidgetLogger( self.logtext )
      logfile.addWidgetHandler( loghandler )
      sys.stdout = logfile
      sys.stderr = logfile

      
    def openDefaultsFile(self):
      tkFileDialog.askopenfilename(defaultextension="*.ini", filetypes=[('ini files', '.ini'), ('all files', '.*')],initialfile='pydondefaults.ini')

    def openXMLConfig(self):
      tkFileDialog.askopenfilename(defaultextension="*.xml", filetypes=[('xml files', '.xml'),('all files', '.*')],initialfile='example_hiveconfig.xml')

    def saveDefaultsFile(self):
      tkFileDialog.asksaveasfilename(defaultextension="*.ini", filetypes=[('ini files', '.ini'), ('all files', '.*')],initialfile='pydondefaults.ini')

    def saveXMLConfig(self):
      tkFileDialog.asksaveasfilename(defaultextension="*.xml", filetypes=[('xml files', '.xml'),('all files', '.*')],initialfile='example_hiveconfig.xml')

    def hello(self):
        print( "hi there, everyone! - main window" )


if __name__ == "__main__":

  root = Tk()
  root.title( "Sense/Stage MiniHive" )
  app = HiveApp(root)
  app.openConfigMenu()
  app.openLogWindow()

  root.mainloop()
