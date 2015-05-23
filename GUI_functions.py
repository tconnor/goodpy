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
        win = Tkinter.Tk()
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
        win.destroy()
        outdict[obj] = obj_match
    return outdict


def test_routine():
    instruments = ['guitars', 'keys', 'drums', 'bass', 'harp']
    musicians = ['john', 'paul', 'george', 'ringo']
    find_match(musicians,instruments)
