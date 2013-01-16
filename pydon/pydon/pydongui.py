# File: hello2.py

from Tkinter import *
import tkFileDialog

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
      
      self.frame = Frame(master)
      self.frame.pack()
      #frame2 = Frame( frame )
      #frame2.pack()
            
      Label( self.frame, text="mode" ).grid( row=0, sticky=W)
      
      MODES = [
        ("datanetwork", "D"),
        ("osc", "O"),
        ("junxion", "J"),
        ("libmapper", "M"),
      ]
    
      v = StringVar()
      v.set("D") # initialize
      
      cl = 1
    
      for text, mode in MODES:
        b = Radiobutton(self.frame, text=text, variable=v, value=mode)
        b.grid( row=0, column = cl )
        cl = cl + 1
      
      self.verbosevar = self.addCheckbox( "verbose", self.hello, 1, 0 )
      self.logvar = self.addCheckbox( "log data", self.hello, 1, 1 )
      self.apivar = self.addCheckbox( "api mode", self.hello, 1, 2 ) ## advanced setting
      self.ignorevar = self.addCheckbox( "ignore new minibees", self.hello, 1, 3 ) ## advanced setting
      self.xbeeerrorvar = self.addCheckbox( "reset serial on error", self.hello, 1, 4 ) ## advanced setting
      
      self.serialentry = self.addTextEntry( "serial port", 2 ) #TODO: should select from list of available ports
      self.baudrate = self.addTextEntry( "baudrate", 4 ) #TODO: should select from list of possible baudrates ## advanced setting
      self.name = self.addTextEntry( "name in datanetwork", 3 ) ## advanced setting
      self.minibees = self.addTextEntry( "max number of minibees", 4 ) ## advanced setting
      self.mboffset = self.addTextEntry( "offset of minibees", 5 ) ## advanced setting
      self.hostip = self.addTextEntry( "IP to send OSC to", 6 )
      self.hostport = self.addTextEntry( "Port to send OSC to", 7 )
      self.myip = self.addTextEntry( "IP to listen on", 8 ) ## advanced setting #TODO: select from (all = 0.0.0.0; only localhost: 127.0.0.1; only external: check current ip address)
      self.myport = self.addTextEntry( "port to listen on", 9 ) ## advanced setting      
      
    def addCheckbox( self, text, command, row, column ):
      myvar = IntVar()
      ch = Checkbutton(self.frame, text=text, variable=myvar, command=command)
      ch.grid( row=row, column=column )
      return myvar

    def addTextEntry( self, text, row ):
      Label( self.frame, text=text ).grid( row=row, column=0, sticky=W)
      te = Entry( self.frame, width=60 )
      te.grid( row=row, column=1, columnspan=4 )
      return te

    def hello(self):
        print "hi there, everyone!"


class App:

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

      helpmenu = Menu(menubar, tearoff=0)
      helpmenu.add_command(label="About", command=self.hello)
      menubar.add_cascade(label="Help", menu=helpmenu)

      # display the menu
      master.config(menu=menubar)


      self.frame = Frame(master, height=512)
      self.frame.pack()
      
      status = StatusBar(master)
      status.pack(side=BOTTOM, fill=X)
      
    def openConfigMenu(self):
      self.configure = ConfigureMenu(self.frame)
      
    def openDefaultsFile(self):
      tkFileDialog.askopenfilename(defaultextension="*.ini", filetypes=[('ini files', '.ini'), ('all files', '.*')],initialfile='pydondefaults.ini')

    def openXMLConfig(self):
      tkFileDialog.askopenfilename(defaultextension="*.xml", filetypes=[('xml files', '.xml'),('all files', '.*')],initialfile='example_hiveconfig.xml')

    def saveDefaultsFile(self):
      tkFileDialog.asksaveasfilename(defaultextension="*.ini", filetypes=[('ini files', '.ini'), ('all files', '.*')],initialfile='pydondefaults.ini')

    def saveXMLConfig(self):
      tkFileDialog.asksaveasfilename(defaultextension="*.xml", filetypes=[('xml files', '.xml'),('all files', '.*')],initialfile='example_hiveconfig.xml')

    def hello(self):
        print "hi there, everyone! - main window"

root = Tk()
root.title( "Sense/Stage MiniHive" )
app = App(root)
app.openConfigMenu()

root.mainloop()
