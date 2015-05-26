from glob import glob
import numpy as np

def scrub_file(filen):
    tmpf = open(filen,'r')
    frd = tmpf.read()
    outf = open('tempdoc.cat','w')
    outf.write(frd.replace('\t',''))
    outf.close()
    tmpf.close()
    return

def run_through_idb(filen,xmin='18',xmax='4111'):
    '''Makes x1,x2,dx from reidentify database file'''
    indata = False
    xpix = []
    lambdalist = []
    with open(filen,'r') as f:
        for line in f:
            try:
                #line0 = line.split()[0]
                if line.split()[0] == 'features':
                    indata = True
                elif line.split()[0] == 'function':
                    indata = False
                elif indata:
                    xpix.append(float(line.split()[0]))
                    lambdalist.append(float(line.split()[1]))
            except:
                pass                #Handles blank lines
        try:
            dx,x_int = np.polyfit(xpix,lambdalist,1)
        except TypeError:
            print xpix
            print lambdalist
            dx,x_int = np.polyfit(xpix,lambdalist,1)
        x1 = float(xmin) * float(dx) + float(x_int)
        x2 = float(xmax) * float(dx) + float(x_int)
    return x1,x2,dx


def get_dx_params(arc_list,xmin='18',xmax='4111'):
    outdict = {}
    for arc in arc_list:
        filen = 'database/id'+arc[:-5]
        dx_params = run_through_idb(filen,xmin=xmin,xmax=xmax)
        outdict[arc] = dx_params
    return outdict

def std_options():
    std_options = []
    std_options.append('cd32')
    std_options.append('eg21')
    std_options.append('eg274')
    std_options.append('f110')
    std_options.append('f56')
    std_options.append('h600')
    std_options.append('l1020')
    std_options.append('l1788')
    std_options.append('l2415')
    std_options.append('l3218')
    std_options.append('l377')
    std_options.append('l3864')
    std_options.append('l4364')
    std_options.append('l4816')
    std_options.append('l6248')
    std_options.append('l7379')
    std_options.append('l745')
    std_options.append('l7987')
    std_options.append('l9239')
    std_options.append('l9491')
    return std_options


