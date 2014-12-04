from pyraf import iraf

def reduce_dimensions(filename):
    iraf.imcopy(filename+'[*,*,1]',filename)
    #iraf.hedit(ccdsec) #What is this supposed to do?
    iraf.hedit(filename,'EPOCH',2000,add=True)
    iraf.wcsreset(filename,filename,wcs='world')
    return
