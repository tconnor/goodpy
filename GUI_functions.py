import Tkinter

class GoodPyGUI:
    def __init__(self,master):
        self.master = master
        master.title('GUI')
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
        

        
        
def find_match(principle, associate,title='GUI',caption_tail=' Selection'):
    '''Uses GoodPyGUI to list a selection of possible matches, and returns user selection'''
    outdict = {}
    for obj in principle:
        win = Tkinter.Toplevel()
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
    for obj in principle:
        win = Tkinter.Toplevel()
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



def test_routine():
    instruments = ['guitars', 'keys', 'drums', 'bass', 'harp']
    musicians = ['john', 'paul', 'george', 'ringo']
    find_match(musicians,instruments)
    superlist = ['a','b','c','d','e','f','g','h','i','j','k']
    break_apart(superlist)


