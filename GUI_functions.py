import Tkinter

class GoodPyGUI:
    def __init__(self,master):
        self.master = master
        master.title('GUI')
    def add_frame(self,master,bg='white'):
        mapframe = Tkinter.Frame(master,bg=bg)
        return mapframe
    def add_close_button(self,master,clabel='Close'):
        self.close_button = Tkinter.Button(master, text = clabel, command=master.quit)
        self.close_button.pack()
    def add_checkbox(self,master,boxname,scoredict):
        scoredict[boxname] = Tkinter.BooleanVar()
        scoredict[boxname].set(False)
        self.l = Tkinter.Checkbutton(master,text=boxname,variable=scoredict[boxname],onvalue=True,offvalue=False)
        self.l.pack()
        return scoredict
    def add_specific_checkbox(self,master,boxname,variab):
        self.spl = Tkinter.Checkbutton(master,text=boxname,variable=variab)
        self.spl.pack()
    def add_radiobutton(self,master,buttonname,var):
        self.rb = Tkinter.Radiobutton(master,text=buttonname,variable=var,value=buttonname)
        self.rb.pack()
    def set_title(self,master,newtitle):
        master.title(newtitle)
    def read(self,boxname,scoredict):
        return scoredict[boxname].get()
    def add_caption(self,master,caption):
        self.cpt = Tkinter.Label(master,text=caption)
        self.cpt.pack()
    def add_radio_list(self,master,objkey,buttons,variab,initval):
        mapframe = self.add_frame(master)
        self.cpt = Tkinter.Label(mapframe,text=objkey)
        self.cpt.pack(side=Tkinter.LEFT)
        for possval in buttons:
            self.rb = Tkinter.Radiobutton(mapframe,text=possval,variable=variab,value=possval)
            self.rb.pack(side=Tkinter.LEFT)
        variab.set(initval)
        mapframe.pack()

class GoodPyGUI_scroll(Tkinter.Frame):
    def __init__(self,master):
        Tkinter.Frame.__init__(self,master)
        self.master = master
        master.title('GUI')
        self.vsb = Tkinter.Scrollbar(master,orient="vertical")
        self.text = Tkinter.Text(master,width=200,height=200,yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.pack(side="right",fill="y")
        self.text.pack(side="left",fill="both",expand=True)
    def add_frame(self,master,bg='white'):
        mapframe = Tkinter.Frame(master,bg=bg)
        return mapframe
    def add_close_button(self,master,clabel='Close'):
        self.close_button = Tkinter.Button(master, text = clabel, command=master.quit)
        self.text.window_create("end",window=self.close_button)
        #self.close_button.pack()
    def add_checkbox(self,master,boxname,scoredict):
        scoredict[boxname] = Tkinter.BooleanVar()
        scoredict[boxname].set(False)
        self.l = Tkinter.Checkbutton(master,text=boxname,variable=scoredict[boxname],onvalue=True,offvalue=False)
        self.text.window_create("end",window=self.l)
        self.text.insert("end",'\n')
        #self.l.pack()
        return scoredict
    def add_specific_checkbox(self,master,boxname,variab):
        self.spl = Tkinter.Checkbutton(master,text=boxname,variable=variab)
        self.text.window_create("end",window=self.spl)
        #self.spl.pack()
    def add_radiobutton(self,master,buttonname,var):
        self.rb = Tkinter.Radiobutton(master,text=buttonname,variable=var,value=buttonname)
        self.text.window_create("end",window=self.rb)
        #self.rb.pack()
    def set_title(self,master,newtitle):
        master.title(newtitle)
    def read(self,boxname,scoredict):
        return scoredict[boxname].get()
    def add_caption(self,master,caption):
        self.cpt = Tkinter.Label(master,text=caption)
        self.text.window_create("end",window=self.cpt)
        #self.cpt.pack()
    def add_radio_list(self,master,objkey,buttons,variab,initval):
        self.mapframe = self.add_frame(master)
        self.cpt = Tkinter.Label(self.mapframe,text=objkey)
        self.cpt.pack(side=Tkinter.LEFT)
        for possval in buttons:
            self.rb = Tkinter.Radiobutton(self.mapframe,text=possval,variable=variab,value=possval)
            self.rb.pack(side=Tkinter.LEFT)
        variab.set(initval)
        self.text.window_create("end",align=Tkinter.BOTTOM,window=self.mapframe)
        #mapframe.pack()


def find_match(principle, associate,title='GUI',caption_tail=' Selection'):
    '''Uses GoodPyGUI to list a selection of possible matches, and returns user selection'''
    outdict = {}
    for obj in principle:
        win = Tkinter.Toplevel()
        if len(associate) > 40:
            pygui = GoodPyGUI_scroll(win)
        else:
            pygui = GoodPyGUI(win)
        pygui.set_title(win,title)
        pygui.add_caption(win,obj+caption_tail)
        scoredict = {}
        obj_match = []
        for assoc in associate:
            scoredict = pygui.add_checkbox(win,assoc,scoredict)
        pygui.add_close_button(win,'Confirm')
        needs_match = True
        while needs_match:
            win.mainloop()
            for assoc in associate:
                if scoredict[assoc].get():
                    obj_match.append(assoc)
                    needs_match=False
                else:
                    pass
            if len(obj_match) < 1:
                print 'You need to select at least one object!'
                for assoc in associate:
                    print assoc
                    print scoredict[assoc].get()
        win.destroy()
        outdict[obj] = obj_match
    return outdict

def delete_by_values(lst, values):
    values_as_set = set(values)
    return [ x for x in lst if x not in values_as_set ]

def find_single_match(principle, associate,title='GUI',caption_tail=' Selection'):
    '''Uses GoodPyGUI to list a selection of possible matches, and returns only one match'''
    outdict = {}
    if len(associate)==1:
        outdict = {}
        for obj in principle:
            outdict[obj] = associate[0]
        return outdict
    else:
        pass
    
    for obj in principle:
        win = Tkinter.Toplevel()
        if len(associate) > 40:
            pygui = GoodPyGUI_scroll(win)
        else:
            pygui = GoodPyGUI(win)
        pygui.set_title(win,title)
        pygui.add_caption(win,obj+caption_tail)
        obj_match = []
        var=Tkinter.StringVar()
        for assoc in associate:
            pygui.add_radiobutton(win,assoc,var)
        pygui.add_close_button(win,'Confirm')
        needs_match = True
        while needs_match:
            win.mainloop()
            if var.get() not in associate:
                print 'You need to select an object!'
            else:
                needs_match=False
        win.destroy()
        outdict[obj] = var.get()
    return outdict

def select_subgroup(mainlist,subunit="Subunits"):
    outlist = []
    win = Tkinter.Toplevel()
    if len(mainlist) > 40:
        pygui = GoodPyGUI_scroll(win)
    else:
        pygui = GoodPyGUI(win)
    pygui.set_title(win,'Select '+subunit)
    scoredict = {}
    abortvar = Tkinter.IntVar()
    for choice in mainlist:
        scoredict = pygui.add_checkbox(win,choice,scoredict)
    pygui.add_specific_checkbox(win,'None in this List',abortvar)
    pygui.add_close_button(win,'Confirm')
    needs_match = True
    while needs_match:
        win.mainloop()
        for choice in mainlist:
            if scoredict[choice].get():
                outlist.append(choice)
                needs_match=False
            else:
                pass
        if len(outlist) < 1:
            if abortvar.get():
                print 'No objects in this list, proceeding.'
                needs_match=False
            else:
                print 'You need to select at least one object or specify that none are in the list'
        else:
            if abortvar.get():
                print 'Incompatible answers selected! Please repeat.'
                needs_match = True
            else:
                pass
    win.destroy()
    return outlist    


def break_apart(superlist,title='Break Apart',caption='Select from group'):
    outlist = []
    more_left = True
    while more_left:
        choicelist = []
        win = Tkinter.Toplevel()
        if len(superlist) > 40:
            pygui = GoodPyGUI_scroll(win)
        else:
            pygui = GoodPyGUI(win)
        pygui.set_title(win,title)
        scoredict = {}
        for obj in superlist:
            scoredict = pygui.add_checkbox(win,obj,scoredict)
        pygui.add_close_button(win,'Confirm')
        needs_match = True
        while needs_match:
            win.mainloop()
            dellist = []
            for choice in superlist:
                if scoredict[choice].get():
                    choicelist.append(choice)
                    dellist.append(choice)
                    needs_match=False
                else:
                    pass
            if len(choicelist) < 1:
                print 'You need to select at least one object'
            else:
                superlist = delete_by_values(superlist,dellist)
        if len(superlist) == 0:
            more_left = False
        else:
            pass
        outlist.append(choicelist)
        win.destroy()
    return outlist

def establish_type(mainlist,typedict,buttons):
    win = Tkinter.Toplevel()
    if len(mainlist) > 40:
        pygui = GoodPyGUI_scroll(win)
    else:
        pygui = GoodPyGUI(win)
    pygui.set_title(win,'Select FITS File Type')
    pygui.add_caption(win,'Verify Each File Type')
    outdict = {}
    for filename in mainlist:
        f_obj = filename.split('.')[0]
        ftype = typedict[f_obj]
        outdict[f_obj] = Tkinter.Variable()
        pygui.add_radio_list(win,f_obj,buttons,outdict[f_obj],typedict[f_obj])
    pygui.add_close_button(win,'Confirm')
    win.mainloop()
    for filename in mainlist:
        f_obj = filename.split('.')[0]
        typedict[f_obj] = outdict[f_obj].get()
    win.destroy()
    return typedict


def test_routine():
    instruments = ['guitars', 'keys', 'drums', 'bass', 'harp']
    musicians = ['john', 'paul', 'george', 'ringo']
    find_match(musicians,instruments)
    superlist = ['a','b','c','d','e','f','g','h','i','j','k']
    break_apart(superlist)


