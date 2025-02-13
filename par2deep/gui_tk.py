import os,threading

from tkinter import Tk
from tkinter import PhotoImage
from tkinter import Toplevel
from tkinter import IntVar
from tkinter import StringVar
from tkinter import filedialog
from tkinter import Menu

from tkinter.ttk import LabelFrame
from tkinter.ttk import Treeview
from tkinter.ttk import Style
from tkinter.ttk import Frame
from tkinter.ttk import Label
from tkinter.ttk import Entry
from tkinter.ttk import Checkbutton
from tkinter.ttk import Scale
from tkinter.ttk import Button
from tkinter.ttk import Progressbar
from tkinter.ttk import Scrollbar

import darkdetect

try:
	from par2deep import *
	from toolbox import *
except:
	from .par2deep import *
	from .toolbox import *


class ToolTip:

	def __init__(
		self,
		widget,
		text="widget info",
		wraplength=None,
		delay=250,    # milliseconds
		**kwargs,
	):
		self.widget = widget
		self.text = text
		self.wraplength = wraplength
		self.toplevel = None
		self.delay = delay
		self.id = None

		# set keyword arguments
		kwargs["overrideredirect"] = True
		kwargs["master"] = self.widget
		if "alpha" not in kwargs:
			kwargs["alpha"] = 0.95
		self.toplevel_kwargs = kwargs

		# create default tooltip style
		Style().configure(
			style="tooltip.TLabel",
			background="#fffddd",
			foreground="#333",
			bordercolor="#888",
			borderwidth=1,
			darkcolor="#fffddd",
			lightcolor="#fffddd",
			relief="RAISED",
		)

		# event binding
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.leave)
		self.widget.bind("<Motion>", self.move_tip)
		self.widget.bind("<ButtonPress>", self.leave)

	def enter(self, event=None):
		self.schedule()

	def leave(self, event=None):
		self.unschedule()
		self.hide_tip()

	def schedule(self):
		self.unschedule()
		self.id = self.widget.after(self.delay, self.show_tip)

	def unschedule(self):
		id = self.id
		self.id = None
		if id:
			self.widget.after_cancel(id)

	def show_tip(self, *_):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 20
		# creates a toplevel window
		self.toplevel = Toplevel(self.widget)
		# Leaves only the label and removes the app window
		self.toplevel.wm_overrideredirect(True)
		self.toplevel.wm_geometry("+%d+%d" % (x, y))

		lbl = Label(
			master=self.toplevel,
			text=self.text,
			justify="left",
			wraplength=self.wraplength,
			padding=10,
		)
		lbl.pack(fill="both", expand="yes")
		lbl.configure(style="tooltip.TLabel")

	def move_tip(self, *_):
	    if self.toplevel:
	        x = self.widget.winfo_pointerx() + 25
	        y = self.widget.winfo_pointery() + 10
	        self.toplevel.geometry(f"+{x}+{y}")

	def hide_tip(self, *_):
		if self.toplevel:
			self.toplevel.destroy()
			self.toplevel = None


class app_frame(Frame):
	def __init__(self, master):
		Frame.__init__(self, master)
		self.grid(row=0, column=0, sticky="NSEW")
		#main window has 1 frame, thats it
		master.grid_rowconfigure(0, weight=1)
		master.grid_columnconfigure(0, weight=1)
		self.waittime = 500     #milliseconds

		#swithin that, frames, row-wise, which are updated as necesary.
		#topbar: displays stage of verification
		#middle screen shows options or info
		#bottom bar shows actions
		self.new_window(self.topbar_frame(0), self.start_options_frame(), self.start_actions_frame())
		return


	def new_window(self,t,m,b):
		#swithin that, frames, row-wise, which are updated as necesary.
		#topbar: displays stage of verification
		#middle screen shows options or info
		#bottom bar shows actions

		for rows in range(3):
			self.grid_rowconfigure(rows, weight=1)
		for columns in range(1):
			self.grid_columnconfigure(columns, weight=1)

		self.grid_rowconfigure(0, weight=0) #override weight: sets size to minimal size
		self.topbar = t
		self.topbar.grid(row=0, column=0, sticky="NSEW",padx=20,pady=(20,0))

		self.mid = m
		self.mid.grid(row=1, column=0, sticky="NSEW",padx=20,pady=(20,0))

		self.grid_columnconfigure(2, weight=0)
		self.actbar = b
		self.actbar.grid(row=2, column=0, sticky="NSEW",padx=20,pady=20)
		return


	def topbar_frame(self,stage):
		subframe = Frame(self)
		labels = list(range(6))
		labels[0] = Label(subframe, text="Start", pad=10)
		labels[1] = Label(subframe, text="Proposed actions", pad=10)
		labels[2] = Label(subframe, text="Executing actions", pad=10)
		labels[3] = Label(subframe, text="Report", pad=10)
		labels[4] = Label(subframe, text="Further actions", pad=10)
		labels[5] = Label(subframe, text="Final report", pad=10)
		labels[stage].configure(font="-weight bold")
		[x.pack(side="left") for x in labels]

		return subframe


	def start_options_frame(self,chosen_dir=None):
		self.p2d = par2deep(chosen_dir)

		self.args = {}

		subframe = Frame(self)

		basicset = LabelFrame(subframe, text="Basic Settings",pad=10)
		basicset.pack(fill="x",pady=(0,20))
		advset = LabelFrame(subframe, text="Advanced Settings",pad=10)
		advset.pack(fill="x")

		def pickdir():
			# self.args["directory"].delete(0,END)
			# self.args["directory"].insert(0,filedialog.askdirectory())
			# self.p2d.__init__(self.args["directory"].get())
			self.new_window(self.topbar_frame(0), self.start_options_frame(filedialog.askdirectory()), self.start_actions_frame())
		Button(basicset, text="Pick directory", command=pickdir).pack(side="left")
		self.args["directory"] = Entry(basicset)
		self.args["directory"].pack(fill="x")
		if chosen_dir == None:
			self.args["directory"].insert(0,self.p2d.args["directory"])
		else:
			self.args["directory"].insert(0,chosen_dir)

		self.args["overwrite"] = IntVar()
		self.args["overwrite"].set(self.p2d.args["overwrite"])
		cb1 = Checkbutton(advset, text="Overwrite all parity data", variable=self.args["overwrite"])
		cb1.pack(fill="x")
		ToolTip(cb1,"Any existing parity data found (any *.par* files) will be removed and overwritten.")

		self.args["noverify"] = IntVar()
		self.args["noverify"].set(self.p2d.args["noverify"])
		cb2 = Checkbutton(advset, text="Skip verification", variable=self.args["noverify"])
		cb2.pack(fill="x")
		ToolTip(cb2,"Skips verification of files with existing parity data. Use when you only want to create parity data for new files.")

		self.args["keep_orphan"] = IntVar()
		self.args["keep_orphan"].set(self.p2d.args["keep_orphan"])
		cb3 = Checkbutton(advset, text="Keep orphaned par2 files.", variable=self.args["keep_orphan"])
		cb3.pack(fill="x")
		ToolTip(cb3,"Do not remove unused parity files (*.par*).")

		self.args["clean_backup"] = IntVar()
		self.args["clean_backup"].set(self.p2d.args["clean_backup"])
		cb3 = Checkbutton(advset, text="Remove backup files", variable=self.args["clean_backup"])
		cb3.pack(fill="x")
		ToolTip(cb3,"Remove backup files (*.[0-9]).")

		Label(advset, text="Exclude directories (comma separated)").pack(fill="x")
		self.args["excludes"] = Entry(advset)
		self.args["excludes"].pack(fill="x")
		self.args["excludes"].insert(0,','.join(self.p2d.args["excludes"]))
		ToolTip(self.args["excludes"],"These subdirectories will be excluded from the analysis. Use 'root' for the root of the directory.")

		Label(advset, text="Exclude extensions (comma separated)").pack(fill="x")
		self.args["extexcludes"] = Entry(advset)
		self.args["extexcludes"].pack(fill="x")
		self.args["extexcludes"].insert(0,','.join(self.p2d.args["extexcludes"]))
		ToolTip(self.args["extexcludes"],"These extensions will be excluded from the analysis.")

		Label(advset, text="Path to par2.exe").pack(fill="x")
		self.args["par_cmd"] = Entry(advset)
		self.args["par_cmd"].pack(fill="x")
		self.args["par_cmd"].insert(0,self.p2d.args["par_cmd"])
		ToolTip(self.args["par_cmd"],"Should be set automatically and correctly, but can be overriden.")

		Label(advset, text="Percentage of protection").pack(fill="x")
		self.args["percentage"] = IntVar()
		self.args["percentage"].set(self.p2d.args["percentage"])
		s1 = Scale(advset,orient="horizontal",from_=5,to=100,variable=self.args["percentage"],command=lambda s:s1label.config(text='%d' % float(s)))
		s1.pack(fill="x")
		s1label = Label(advset, text=self.p2d.args["percentage"])
		s1label.pack()
		ToolTip(s1,"The maximum percentage of corrupted data you will be able to recover from. Higher is safer, but uses more data.")

		return subframe


	def start_actions_frame(self):
		subframe = Frame(self)
		Button(subframe, text="Check directory contents", command=self.set_start_actions).pack()
		return subframe


	def repair_actions_frame(self):
		subframe = Frame(self)
		if self.p2d.len_verified_actions > 0:
			Button(subframe, text="Fix repairable corrupted files and recreate unrepairable files", command=self.repair_action).pack()
			Button(subframe, text="Recreate parity files for the changed and unrepairable files", command=self.recreate_action).pack()
		else:
			Button(subframe, text="Nothing to do. Exit.", command=self.master.destroy).pack()
		return subframe


	def execute_actions_frame(self):
		subframe = Frame(self)
		if self.p2d.len_all_actions > 0:
			Button(subframe, text="Run actions", command=self.execute_actions).pack()
		else:
			Button(subframe, text="Nothing to do. Exit.", command=self.master.destroy).pack()
		return subframe


	def exit_actions_frame(self):
		subframe = Frame(self)
		if hasattr(self.p2d,'len_all_err'):
			Label(subframe, text=f"There were {self.p2d.len_all_err} errors.").pack(fill="x")
		Button(subframe, text="Exit", command=self.master.destroy).pack()
		return subframe


	def exit_frame(self):
		subframe = Frame(self)
		Label(subframe, text="The par2 command you specified is invalid.").pack(fill="x")
		return subframe


	def progress_indef_frame(self):
		subframe = Frame(self)
		self.pb=Progressbar(subframe, mode='indeterminate')
		self.pb.start()
		self.pb.pack(fill="x",expand=True)
		Label(subframe, text="Indexing directory, may take a few moments...").pack(fill="x")
		return subframe


	def progress_frame(self,length):
		subframe = Frame(self)
		self.pb=Progressbar(subframe, mode='determinate',maximum=length+0.01)
		#+.01 to make sure bar is not full when last file processed.
		self.pb.pack(fill="x",expand=True)
		self.pb_currentfile = StringVar()
		self.pb_currentfile.set("Executing actions, may take a few moments...")
		Label(subframe, textvariable = self.pb_currentfile).pack(fill="x")
		return subframe


	def blank_frame(self):
		subframe = Frame(self)
		return subframe


	def repair_action(self):
		self.new_window(self.topbar_frame(4), self.blank_frame(), self.progress_frame(self.p2d.len_verified_actions))
		self.update()

		self.cnt = 0
		self.cnt_stop = False
		def run():
			for i in self.p2d.execute_repair():
				self.cnt+=1
				self.currentfile = i
			dispdict = {
				'verifiedfiles_succes' : 'Verified and in order',
				'createdfiles' : 'Newly created parity files',
				'removedfiles' : 'Files removed',
				'createdfiles_err' : 'Errors during creating parity files',
				'removedfiles_err' : 'Errors during file removal',
				'fixes' : 'Verified files succesfully fixed',
				'fixes_err' : 'Verified files failed to fix',
				'recreate' : 'Succesfully recreated (overwritten) parity files',
				'recreate_err' : 'Failed (overwritten) new parity files'
				}
			self.new_window(self.topbar_frame(5), self.scrollable_treeview_frame(dispdict), self.exit_actions_frame())
			#put p2d.len_all_err somewhere in label of final report
			self.cnt_stop = True
		thread = threading.Thread(target=run)
		thread.daemon = True
		thread.start()

		def upd():
			if not self.cnt_stop:
				self.pb.step(self.cnt)
				self.pb_currentfile.set(f"Processing {os.path.basename(self.currentfile)}")
				self.cnt=0
				self.master.after(self.waittime, upd)
			else:
				return

		upd()
		return


	def recreate_action(self):
		self.new_window(self.topbar_frame(4), self.blank_frame(), self.progress_frame(self.p2d.len_verified_actions))
		self.update()

		self.cnt = 0
		self.cnt_stop = False
		def run():
			for i in self.p2d.execute_recreate():
				self.cnt+=1
				self.currentfile = i
			dispdict = {
				'verifiedfiles_succes' : 'Verified and in order',
				'createdfiles' : 'Newly created parity files',
				'removedfiles' : 'Files removed',
				'createdfiles_err' : 'Errors during creating parity files',
				'removedfiles_err' : 'Errors during file removal',
				'fixes' : 'Verified files succesfully fixed',
				'fixes_err' : 'Verified files failed to fix',
				'recreate' : 'Succesfully recreated (overwritten) parity files',
				'recreate_err' : 'Failed (overwritten) new parity files'
				}
			self.new_window(self.topbar_frame(5), self.scrollable_treeview_frame(dispdict), self.exit_actions_frame())
			#put p2d.len_all_err somewhere in label of final report
			self.cnt_stop = True
		thread = threading.Thread(target=run)
		thread.daemon = True
		thread.start()

		def upd():
			if not self.cnt_stop:
				self.pb.step(self.cnt)
				self.pb_currentfile.set(f"Processing {os.path.basename(self.currentfile)}")
				self.cnt=0
				self.master.after(self.waittime, upd)
			else:
				return

		upd()
		return


	def set_start_actions(self):
		#update p2d args.
		self.p2d.args["quiet"] = False #has no meaning in gui
		self.p2d.args["overwrite"] = self.args["overwrite"].get() == 1
		self.p2d.args["noverify"] = self.args["noverify"].get() == 1
		self.p2d.args["keep_orphan"] = self.args["keep_orphan"].get() == 1
		self.p2d.args["clean_backup"] = self.args["clean_backup"].get() == 1
		self.p2d.args["excludes"] = self.args["excludes"].get().split(',') if self.args["excludes"].get().split(',') != [''] else []
		self.p2d.args["extexcludes"] = self.args["extexcludes"].get().split(',') if self.args["extexcludes"].get().split(',') != [''] else []
		self.p2d.args["directory"] = os.path.abspath(self.args["directory"].get())
		self.p2d.args["par_cmd"] = str(self.args["par_cmd"].get())
		self.p2d.args["percentage"] = str(int(self.args["percentage"].get()))

		#go to second frame
		self.new_window(self.topbar_frame(0), self.blank_frame(), self.progress_indef_frame())
		self.update()
		def run():
			if self.p2d.check_state() == 200:
				self.new_window(self.topbar_frame(0), self.exit_frame(), self.exit_actions_frame())
				return
			dispdict = {
				'create' : 'Create parity files',
				'incomplete' : 'Incomplete parity data found. Create new parity files',
				'verify' : 'Verify files',
				'orphans_delete' : 'Remove these orphaned files',
				'orphans_keep' : 'Keep these orphaned files',
				'backups_delete' : 'Remove old backup files',
				'backups_keep' : 'Keep these backup files'
				}
			self.new_window(self.topbar_frame(1), self.scrollable_treeview_frame(dispdict), self.execute_actions_frame())
		thread = threading.Thread(target=run)
		thread.daemon = True
		thread.start()
		return


	def execute_actions(self):
		#go to third frame
		self.new_window(self.topbar_frame(2), self.blank_frame(), self.progress_frame(self.p2d.len_all_actions))
		self.update()

		self.cnt = 0
		self.cnt_stop = False
		def run():
			for i in self.p2d.execute():
				self.cnt+=1
				self.currentfile = i
			dispdict = {
				'verifiedfiles_succes' : 'Verified and in order',
				'createdfiles' : 'Newly created parity files',
				'removedfiles' : 'Files removed',
				'createdfiles_err' : 'Errors during creating parity files',
				'verifiedfiles_err' : 'Irrepairable damage found',
				'verifiedfiles_repairable' : 'Repairable damage found',
				'removedfiles_err' : 'Errors during file removal'
				}
			self.new_window(self.topbar_frame(3), self.scrollable_treeview_frame(dispdict), self.repair_actions_frame())
			self.cnt_stop = True
		thread = threading.Thread(target=run)
		thread.daemon = True
		thread.start()

		def upd():
			if not self.cnt_stop:
				self.pb.step(self.cnt)
				self.pb_currentfile.set(f"Processing {os.path.basename(self.currentfile)}")
				self.cnt=0
				self.master.after(self.waittime, upd)
			else:
				return

		upd()
		return


	def scrollable_treeview_frame(self,nodes={}):
		subframe = Frame(self)
		tree = Treeview(subframe)
		tree.pack(side="left",fill="both",expand=True)

		ysb = Scrollbar(subframe, orient='vertical', command=tree.yview)
		ysb.pack(side="right", fill="y", expand=False)

		tree.configure(yscroll=ysb.set)
		#tree.heading('#0', text="Category", anchor='w')
		tree["columns"]=("fname","action")
		tree.column("#0", width=20, stretch=False)
		tree.heading("action", text="Action")
		tree.column("action", width=60, stretch=False)
		tree.column("fname", stretch=True)
		tree.heading("fname", text="Filename")


		def doubleclick_tree(event):
			startfile(tree.item(tree.selection()[0],"values")[0])
			return

		def show_contextmenu(event):
			print (tree.selection())
			popup = Menu(self.master, tearoff=0)
			for node,label in nodes.items():
				popup.add_command(label=node)
			try:
				popup.tk_popup(event.x_root, event.y_root)
			finally:
				# make sure to release the grab (Tk 8.0a1 only)
				popup.grab_release()

		tree.bind("<Double-1>", doubleclick_tree)
		tree.bind("<Button-3>", show_contextmenu)

		for node,label in nodes.items():
			if len(getattr(self.p2d,node))==0:
				tree.insert("", 'end', values=(f"{label}: no files.",""), open=False)
			else:
				thing = tree.insert("", 'end', values=(f"{label}: expand to see {len(getattr(self.p2d,node))} files.",""), open=False)
				for item in getattr(self.p2d,node):
					if not isinstance(item, list):
						tree.insert(thing, 'end', values=(f"  {item}",node), open=False)
					else:
						tree.insert(thing, 'end', values=(f"  {item[0]}",node), open=False)

		return subframe


def main():
	root = Tk()

	if darkdetect.isDark():
		root.tk.call('source', os.path.join(os.path.dirname(__file__),"breeze-dark","breeze-dark.tcl"))
		Style().theme_use('breeze-dark')
	else:
		root.tk.call('source', os.path.join(os.path.dirname(__file__),"breeze","breeze.tcl"))
		Style().theme_use('breeze')
	
	app = app_frame(root)

	try:
		ico = PhotoImage(file=os.path.join(os.path.dirname(__file__),"par2deep.png"))
		root.tk.call('wm', 'iconphoto', root._w, ico)
	except:
		pass
	
	w = 800 # width for the Tk root
	h = 700 # height for the Tk root

	# get screen width and height
	ws = root.winfo_screenwidth() # width of the screen
	hs = root.winfo_screenheight() # height of the screen

	# calculate x and y coordinates for the Tk root window
	x = (ws/2) - (w/2)
	y = (hs/2) - (h/2)

	# set the dimensions of the screen
	# and where it is placed
	root.geometry('%dx%d+%d+%d' % (w, h, x, y))
	root.wm_title("par2deep")

	root.mainloop()

	# if app.p2d.len_all_err>0:
	# 	return 1
	# else:
	# 	return 0

