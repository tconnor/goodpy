from glob import glob
import numpy as np

def run_through_idb(filename,xmin='18',xmax='4111'):
    '''Makes x1,x2,dx from reidentify database file'''
    indata = False
    xpix = []
    lambdalist = []
    with open(filen,'r') as f:
        for line in f:
            try:
                line0 = line.split()[0]
                if line.split()[0] == 'features':
                    indata = True
                elif line.split()[0] == 'function':
                    indata = False
                elif indata:
                    xpix.append(float(line.split()[0]))
                    lambdalist.append(float(line.split()[1]))
            except:
                pass
        dx,x_int = np.polyfit(xpix,lambdalist,1)
        x1 = float(xmin) * float(dx) + float(x_int)
        x2 = float(xmax) * float(dx) + float(x_int)
    return x1,x2,dx


def get_dx_params(arc_list,xmin='18',xmax='4111'):
    outdict = {}
    for arc in arc_list:
        filen = 'database/id'+arc[:-5]
        dx_params = run_through_idb(arc,xmin=xmin,xmax=xmax)
        outdict[arc] = dx_params
    return outdict



