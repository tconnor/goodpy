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

def quartz_divide(science_list,object_match):
    '''Divides science frames by user-selected quartz frames'''
    for obj in science_list:
        if len(object_match[obj]) > 1:
            qtzinpt = ''
            for qtz in object_match[obj]:
                qtzinpt += qtz +','
            iraf.imcombine(input=qtzinpt,output='tempquartz')
            iraf.imarith(operand1=obj,operand2='tempquartz',operator='/',result='f'+obj)
            heditstr = 'Flat field images are '+qtzinpt[:-1]
            if len(heditstr) > 65:
                nfields = int(len(heditstr)/65) #Declare int for py3 compatibility
                for ii in range(nfields+1):
                    writestr = heditstr[(ii*65):(ii+1)*65]
                    iraf.hedit(images='f'+obj,fields='flatcor'+str(ii),value=writestr,add='yes',verify='No')
            else:
                iraf.hedit(images='f'+obj,fields='flatcor',value=heditstr,add='yes',verify='No')
        else:
            iraf.imarith(operand1=obj,operand2=object_match[obj][0],operator='/',result='f'+obj)
            heditstr = 'Flat field image is '+object_match[obj][0]
            if len(heditstr) > 65:
                nfields = int(len(heditstr)/65) #Declare int for py3 compatibility
                for ii in range(nfields+1):
                    writestr = heditstr[(ii*65):(ii+1)*65]
                    iraf.hedit(images='f'+obj,fields='flatcor'+str(ii),value=writestr,add='yes',verify='No')
            else:
                iraf.hedit(images='f'+obj,fields='flatcor',value=heditstr,add='yes',verify='No')
    return
    
def transform(filename,fcstar,fcarc,x1,x2,dx):
    '''Transforms filename to t+filename using noao>twodspec>longslit>transform'''
    irf_prm.set_transform(iraf.transform)
    iraf.transform.fitnames = fcstar+','+fcarc
    iraf.transform.x1 = x1
    iraf.transform.x2 = x2
    iraf.transform.dx = dx
    print 'FEATURE SET IS NOT COMPLETE! IF YOU SEE THIS, TELL TOM TO GET TO WORK!'
    
iraf.imarith(operand1=obj,operand2=tmpqtz,op='/',result='f'+obj)
iraf.imcombine(input=qtzlist,output='tempquartz',expname='EXPTIME')
