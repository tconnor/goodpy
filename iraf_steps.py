from pyraf import iraf
import iraf_parameters as irf_prm
def initialize_iraf():
    iraf.noao()
    iraf.imred()
    iraf.ccdred()
    iraf.specred()
    iraf.twodspec()
    iraf.longslit()
    return

def reduce_dimensions(filename):
    iraf.imcopy(filename+'[*,*,1]',filename)
    #iraf.hedit(ccdsec) #What is this supposed to do?
    iraf.hedit(filename,'EPOCH',2000,add=True,verify='No')
    iraf.wcsreset(image=filename,wcs='world')
    return

def bias_correct(file_list,xmin='18',xmax='4111',ymin='350',ymax='1570'):
    irf_prm.set_ccdproc(iraf.ccdproc)
    iraf.ccdproc.biassec = '[4114:4142,1:1896]'
    iraf.ccdproc.trimsec = '['+xmin+':'+xmax+','+ymin+':'+ymax+']'
    for ff in file_list:
        output = 'b'+ff
        iraf.ccdproc(images=ff,output=output)
    return

def normalize_quartzes(quartz_list):
    '''Normalizes the files in quartz_list using noao>twodspec>longslit>response'''
    #This needs more intelligent Failure Handling; current version is alpha.
    irf_prm.set_response(iraf.response)
    for quartz in quartz_list:
        iraf.response(calibrat=quartz,normaliz=quartz,response='n'+quartz)
    return
