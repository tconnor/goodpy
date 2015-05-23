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



instruments = ['guitars', 'keys', 'drums', 'bass', 'harp']
musicians = ['john', 'paul', 'george', 'ringo']
find_match(musicians,instruments)


    #For each principle
    #Make a Gui
    #And in this gui place all the associates
    #Display the Gui, letting the user abort it
    #Check that at least one object is checked
    #If not, reset
    #Then, write all selected objects to the output list

                
for poss in posslist:
    score_dict = go_gui.add_checkbox(win,poss,score_dict)

scoredict = {}
win = Tkinter.Tk()
go_gui = GoodPyGUI(win)
posslist = ['keys', 'guitar', 'drums', 'bass', 'tuba', 'horn', 'harp']

for poss in posslist:
    scoredict = go_gui.add_checkbox(win,poss,scoredict)


go_gui.add_close_button(win)
scoredict['drums'].get()
#scoredict = go_gui.add_checkbox(win,'test1',scoredict)
#scoredict = go_gui.add_checkbox(win,'test2',scoredict)

#scoredict['test1'].get()
#win.mainloop()
#chk = Tkinter.Checkbutton(win,text='Goo',variable=scoredict[boxname])



scoredict = {}
win = Tkinter.Tk()
go_gui = GoodPyGUI(win)
vars = []
for poss in posslist:
    var = Tkinter.IntVar()
    chk = Tkinter.Checkbutton(win,text=poss,variable=var)
    chk.pack()
    vars.append(var)




go_gui.add_close_button(win)

import Tkinter
root = Tkinter.Tk()
var = Tkinter.IntVar()
chk = Tkinter.Checkbutton(root,text='foo',variable=var)
chk.pack(side=Tkinter.LEFT)

var.get()
root = Tkinter.Tk()
var = Tkinter.IntVar()
chk = Tkinter.Checkbutton(root,text='foo',variable=var)
chk.pack(side=Tkinter.LEFT)
root.mainloop()

win = Tkinter.Tk()
foo = Tkinter.IntVar()
checkbutton = Tkinter.Checkbutton(win,text='foo',variable=foo)
checkbutton.pack()
