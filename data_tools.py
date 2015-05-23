from glob import glob
import numpy as np

def run_through_idb(filename,x_max,x_min):
    '''Makes x0,x1,dx from reidentify database file'''
    indata = False
    xpix = []
    lambdalist = []
    with open(filename,'r') as f:
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
        x0 = x_min * dx + xint
        x1 = x_max * dx + xint
    return dx,x0,x1
