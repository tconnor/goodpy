import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import Tkinter
import pyfits as pf
from matplotlib import gridspec


class bkgselect:
    def __init__(self,master):
        self.master = master
        self.mask_low = []
        self.mask_hi = []
        self.fits_fig = Figure(figsize=(8,8))
        self.fits_gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
        self.fits_sp = self.fits_fig.add_subplot(self.fits_gs[0])
        self.prof_sp = self.fits_fig.add_subplot(self.fits_gs[1])
        self.plots = Tkinter.Frame(width=800,height=800)
        self.buttons = Tkinter.Frame(width=800, height=200)
        self.b_left = Tkinter.Frame(width=250, height=200, master= self.buttons)
        self.b_cent = Tkinter.Frame(width=250, height=200, master= self.buttons)
        self.b_right = Tkinter.Frame(width=300, height=200, master= self.buttons)
        self.box_min = Tkinter.Entry(self.b_left)
        self.box_min.insert(0,"0")
        self.box_max = Tkinter.Entry(self.b_left)
        self.box_max.insert(0,"0")
        self.mask_button = Tkinter.Button (self.b_cent,text="MASK",
                                           command=self.add_mask)
        self.unmask_button = Tkinter.Button (self.b_cent,text="UNMASK",
                                             command=self.remove_mask)
        self.confirm_button = Tkinter.Button (self.b_right,
                                              text="CONFIRM",command=master.quit)
        self.plots.pack(side=Tkinter.TOP)
        self.buttons.pack(side=Tkinter.BOTTOM) 
        self.Fits_canvas = FigureCanvasTkAgg(self.fits_fig,master=self.plots)
        self.Fits_canvas.get_tk_widget().pack(side=Tkinter.LEFT)
        self.b_left.pack(side=Tkinter.LEFT)
        self.b_cent.pack(side=Tkinter.LEFT)
        self.b_right.pack(side=Tkinter.RIGHT)
        self.box_min.pack(side=Tkinter.TOP)
        self.box_max.pack(side=Tkinter.BOTTOM)
        self.mask_button.pack(side=Tkinter.TOP)
        self.unmask_button.pack(side=Tkinter.BOTTOM)        
        self.confirm_button.pack(side=Tkinter.TOP)
    def load_data(self,indata,x1,y1,ymax,x2=[],y2=[]):
        self.indata = indata
        self.ymax = ymax
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
    def plot_fits(self):
        vmin,vmax = self.find_vmin_vmax(self.indata)
        self.fits_sp.imshow(self.indata,interpolation='nearest',cmap='YlOrBr',
                            vmax=vmax,vmin=vmin,aspect=5,zorder=0)
        for ii in range(len(self.mask_low)):
            self.overplot_region(self.mask_low[ii],self.mask_hi[ii])
        self.fits_sp.set_xlim(0,np.shape(self.indata)[1])
        self.fits_sp.set_ylim(0,np.shape(self.indata)[0])        
        self.Fits_canvas.show()
    def plot_prof(self):
        self.prof_sp.plot(self.x1,self.y1,color='FireBrick',zorder=1)
        if len(self.x2) > 0 and len(self.y2) > 0:
            self.prof_sp.plot(self.x2,self.y2,color='Black',zorder=0,alpha=0.2)
        for ii in range(len(self.mask_low)):
            self.prof_sp.fill_between([np.min(self.x1),np.max(self.x1)],
                                      [self.mask_low[ii],self.mask_low[ii]],
                                      [self.mask_hi[ii],self.mask_hi[ii]],
                                      color='DodgerBlue',alpha=0.4,zorder=1)
        self.prof_sp.set_ylim(1,self.ymax)
        self.prof_sp.set_xlim(self.find_prof_xlims(self.x1))
        self.Fits_canvas.show()
    def draw_fig(self):
        self.fits_fig.clf()
        self.fits_sp = self.fits_fig.add_subplot(self.fits_gs[0])
        self.prof_sp = self.fits_fig.add_subplot(self.fits_gs[1])
        self.plot_fits()
        self.plot_prof()
    def find_prof_xlims(self,x1):
        pk_mn = np.median(x1)
        pk_st = np.std(x1)
        trimmit = np.where(x1 > (pk_mn - 3*pk_st) )
        pk_mn_t = np.median(x1[trimmit])
        pk_st_t = np.std(x1[trimmit])
        xmn = pk_mn_t - 3*pk_st_t
        xmx = pk_mn_t + 3*pk_st_t
        return xmn,xmx
    def find_vmin_vmax(self,indata):
        mdn = np.median(indata)
        sigm = np.std(indata)
        vmin = mdn - 0.1*sigm
        vmax = mdn + 0.1*sigm
        return vmin,vmax
    def overplot_region(self,ymin,ymax):
        self.fits_sp.fill_between([0,5000],[ymin,ymin],[ymax,ymax],
                                  color='Black',alpha=0.55,zorder=1)
        self.prof_sp.fill_between([0,5000],[ymin,ymin],[ymax,ymax],
                                  color='DodgerBlue',alpha=0.25,zorder=2)
        self.Fits_canvas.show()
    def get_mlo_mhi(self):
        try:
            mlo = int(self.box_min.get())
            mhi = int(self.box_max.get())
        except ValueError:
            print 'Cannot evaluate mask region'
            return -1, -1
        if mlo == mhi:
            print '0 pixel wide mask region. Skipping'
            return -1, -1
        if mlo > mhi:
            tmp = mhi
            mhi = mlo + 0
            mlo = tmp + 0
        return mlo,mhi
    def add_mask(self,verbose=False):
        mlo,mhi = self.get_mlo_mhi()
        if mhi == -1:
            return
        if len(self.mask_low) == 0:
            self.mask_low = [mlo]
            self.mask_hi = [mhi]
            self.draw_fig()
            return
        for ii in range(len(self.mask_hi)):
            if mlo >= self.mask_low[ii] and mhi <= self.mask_hi[ii]:
                print 'No new mask region defined. Did you mean to unmask?'
                return
        #Remove masks fully contained in new mask
        rem_list = []
        for ii in range(len(self.mask_hi)):
            if mlo <= self.mask_low[ii] and mhi >= self.mask_hi[ii]:
                rem_list.append(ii)
        if len(rem_list) > 0:
            rem_list.reverse()
            for jj in rem_list:
                foo = self.mask_low.pop(jj)
                foo = self.mask_hi.pop(jj)
        out_lo = []
        out_hi = []
        ii = 0
        icap = len(self.mask_hi)
        while True:
            #Falls in a gap
            if mlo < self.mask_low[ii] and mhi < self.mask_low[ii]:
                out_lo.append(mlo)
                out_hi.append(mhi)
                out_lo.extend(self.mask_low[ii:])
                out_hi.extend(self.mask_hi[ii:])
                if verbose: print 'Falls in Gap'
                break
            if (mlo <= self.mask_low[ii] and mhi >= self.mask_low[ii]
                and mhi <= self.mask_hi[ii]):
                out_lo.append(mlo)
                out_hi.append(self.mask_hi[ii])
                out_lo.extend(self.mask_low[ii+1:])
                out_hi.extend(self.mask_hi[ii+1:])
                if verbose: print 'Lowers a Limit'                
                break
            if (mlo >= self.mask_low[ii] and mlo <= self.mask_hi[ii] and mhi >= self.mask_hi[ii]):
                if ii == icap - 1:
                    out_lo.append(self.mask_low[ii])
                    out_hi.append(mhi)
                    if verbose: print 'Extends the last limit'                    
                    break
                else:
                    jj = ii + 1
                    while True:
                        if mhi >= self.mask_low[jj] and mhi <= self.mask_hi[jj]:
                            out_lo.append(self.mask_low[ii])
                            out_hi.append(self.mask_hi[jj])
                            out_lo.extend(self.mask_low[jj+1:])
                            out_hi.extend(self.mask_hi[jj+1:])
                            if verbose: print 'Extends into another mask'
                            break
                        if mhi < self.mask_low[jj]:
                            out_lo.append(self.mask_low[ii])
                            out_hi.append(mhi)
                            out_lo.extend(self.mask_low[jj:])
                            out_hi.extend(self.mask_hi[jj:])
                            if verbose: print 'Extends below another mask'
                            break
                        jj +=1
                        if jj == jcap:
                            out_lo.append(self.mask_low[ii])
                            out_hi.append(mhi)
                            if verbose: print 'Extends the new last limit'
                            break
                    break
            #Iterate to the next checkpoint
            out_lo.append(self.mask_low[ii])
            out_hi.append(self.mask_hi[ii])
            if verbose: print out_lo
            if verbose: print out_hi
            ii +=1
            #If at the end, slap the mask on the end and finish
            if ii == icap:
                out_lo.append(mlo)
                out_hi.append(mhi)
                if verbose: print 'Last mask'
                break
        self.mask_low = out_lo
        self.mask_hi = out_hi
        self.draw_fig()
        if verbose: print self.mask_low, self.mask_hi
    def remove_mask(self):
        if len(self.mask_low) == 0:
            print 'Nothing to unmask!'
            return
        mlo,mhi = self.get_mlo_mhi()
        if mhi == -1:
            return
        rem_list = []
        cut_out = False
        for ii in range(len(self.mask_hi)):
            if mlo <= self.mask_low[ii] and mhi >= self.mask_hi[ii]:
                rem_list.append(ii)
        if len(rem_list) > 0:
            cut_out = True
            rem_list.reverse()
            for jj in rem_list:
                foo = self.mask_low.pop(jj)
                foo = self.mask_hi.pop(jj)
        out_lo = []
        out_hi = []
        ii = 0
        icap = len(self.mask_low)
        while True:
            if (self.mask_low[ii] <= mlo and self.mask_hi[ii] >= mlo and
                self.mask_low[ii] <= mhi and self.mask_hi[ii] >= mhi):
                out_lo.append(self.mask_low[ii])
                out_hi.append(mlo)
                out_lo.append(mhi)
                out_hi.append(self.mask_hi[ii])
                out_lo.extend(self.mask_low[ii+1:])
                out_hi.extend(self.mask_hi[ii+1:])
                break
            if (self.mask_low[ii] < mlo and self.mask_hi[ii] >= mlo and
                self.mask_hi[ii] < mhi):
                out_lo.append(self.mask_low[ii])
                out_hi.append(mlo)
                cut_out = True
            elif (self.mask_low[ii] >= mlo and self.mask_low[ii] < mhi and
                  self.mask_hi[ii] > mhi):
                out_lo.append(mhi)
                out_hi.append(self.mask_hi[ii])
                cut_out = True
            else:
                out_lo.append(self.mask_low[ii])
                out_hi.append(self.mask_hi[ii])
            ii += 1
            if ii == icap and not cut_out:
                print 'Nothing needed unmasking!'
                break
            elif ii == icap:
                break
        self.mask_low = out_lo
        self.mask_hi = out_hi
        self.draw_fig()
        print self.mask_low, self.mask_hi


        
def get_mask_regions(infile,median_binwidth=20,sum_binwidth=20,
                     peak_min=150,peak_max=250):
    data = pf.open(infile)[0].data
    ypix,xpix = np.shape(data)
    med_data = stack_median(data,binwidth=median_binwidth)
    sum_data = stack_sum(med_data,binwidth=sum_binwidth)
    profile_x = extract_peak_profile(sum_data,peak_min,peak_max)
    profile_y = np.linspace(0,len(profile_x) - 1,len(profile_x))
    profile_y *= sum_binwidth
    nosum_data = stack_sum(med_data,binwidth=1)
    profile_x2 = extract_peak_profile(nosum_data,peak_min,peak_max)
    profile_y2 = np.linspace(1,len(profile_x2),len(profile_x2))
    profile_x2 *= np.median(profile_x) / np.median(profile_x2)
    win = Tkinter.Toplevel()
    pygui = bkgselect(win)
    pygui.load_data(data,profile_x,profile_y,ypix,x2= profile_x2, y2=profile_y2)
    pygui.draw_fig()
    win.mainloop()
    mask_low = pygui.mask_low
    mask_hi = pygui.mask_hi
    pygui.plots.destroy()
    pygui.buttons.destroy()
    win.destroy()
    return mask_low, mask_hi, ypix


def stack_median(inarray,binwidth=20):
    steps_a = np.shape(inarray)[1]/binwidth
    steps = int(np.floor(steps_a))
    output = []
    for ss in range(steps):
        bgn_i, end_i = ss * binwidth, (ss+1) * binwidth
        stack = np.median(inarray[:,bgn_i:end_i],axis=1)
        stack /= np.median(stack)
        output.append(stack)
    bgn_i= (ss+1) * binwidth
    if steps_a > steps:
        output.append(np.median(inarray[:,bgn_i:],axis=1))
    output = np.array(output)
    return output

def stack_sum(inarray,binwidth=20):
    steps_a = np.shape(inarray)[1]/binwidth
    steps = int(np.floor(steps_a))
    output = []
    for ss in range(steps):
        bgn_i, end_i = ss * binwidth, (ss+1) * binwidth
        stack = np.sum(inarray[:,bgn_i:end_i],axis=1)
        output.append(stack)
    bgn_i= (ss+1) * binwidth
    if steps_a > steps:
        output.append(np.median(inarray[:,bgn_i:] * binwidth,axis=1))
    output = np.array(output)
    return output



def extract_peak_profile(inarray,lowb,hib):
    selected = inarray[:,lowb:hib]
    output = np.sum(selected,axis=1)
    return output

def make_bsplines_input(inarray,mask_low,mask_hi):
    bspl_x, bspl_y, bspl_f, bspl_w = [], [], [], []
    y_dim, x_dim = np.shape(inarray)
    min_y = 0
    yvals = []
    for ii in range(len(mask_low)):
        yvals.extend(range(min_y,mask_low[ii]))
        min_y = mask_hi[ii]
    yvals.extend(range(min_y,y_dim))
    for yy in range(y_dim):
        if yy in yvals:
            bspl_x.extend(range(x_dim))
            bspl_y.extend([yy] * x_dim)
            bspl_f.extend([f for f in data[yy,:]])
            #bspl_w.extend([1] * x_dim)
        else:
            pass
            #bspl_w.extend([0] * x_dim)
    return bspl_x, bspl_y, bspl_f#, bspl_w

def plot_peak_extraction(peak_profile,ax,upscale):
    xvals = np.linspace(0,len(peak_profile)-1,len(peak_profile)) * upscale + 1
    pk_mn = np.median(peak_profile)
    pk_st = np.std(peak_profile)
    trimmit = np.where(peak_profile > (pk_mn - 3*pk_st) )
    pk_mn_t = np.median(peak_profile[trimmit])
    pk_st_t = np.std(peak_profile[trimmit])
    ymn = pk_mn_t - 3*pk_st_t
    ymx = pk_mn_t + 3*pk_st_t
    return xvals,peak_profile,ymn,ymx

    
