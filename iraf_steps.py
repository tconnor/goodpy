from pyraf import iraf
import iraf_parameters as irf_prm
import secondary_tasks as scnd
def gui_alert():
    print 'An IRAF GUI has been opened and requires your input'
    
def initialize_iraf():
    iraf.noao(_doprint=0)
    iraf.imred(_doprint=0)
    iraf.ccdred(_doprint=0)
    iraf.specred(_doprint=0)
    iraf.twodspec(_doprint=0)
    iraf.longslit(_doprint=0)
    return

def reduce_dimensions(filename):
    iraf.imcopy(filename+'[*,*,1]',filename)
    #iraf.hedit(ccdsec) #What is this supposed to do?
    iraf.hedit(filename,'EPOCH',2000,add=True,verify='No')
    iraf.wcsreset(image=filename,wcs='world')
    return

def bias_correct(file_list,xmin='18',xmax='4111',ymin='350',ymax='1570',bindefault=1):
    irf_prm.set_ccdproc(iraf.ccdproc)
    biassecs = {1:'[4114:4142,1:1896]',2:'[4114:4142,1:1896]',3:'[4114:4142,1:1896]',4:'[4114:4142,1:1896]'} #NEED UPDATED
    #iraf.ccdproc.biassec = biassecs[binsize]
    iraf.ccdproc.trimsec = '['+xmin+':'+xmax+','+ymin+':'+ymax+']'
    for ff in file_list:
        comm = scnd.get_comment(ff,'PARAM18')
        if comm == '1 / Serial Binning,Pixels':
            binsize = iraf.hselect(ff,'PARAM18','yes')
        else:
            param_name = scnd.find_param_with_comment(ff,'1 / Serial Binning,Pixels')
            if param_name == 'NullReturn':
                binsize=bindefault
            else:
                binsize = iraf.hselect(ff,param_name,'yes')
        iraf.ccdproc.biassec = biassecs[binsize]
        output = 'b'+ff
        iraf.ccdproc(images=ff,output=output,ccdtype = "")
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
            iraf.imarith(operand1=obj,operand2='tempquartz',op='/',result='f'+obj)
            heditstr = 'Flat field images are '+qtzinpt[:-1]
            iraf.imdelete(images='tempquartz',go_ahead='yes',verify='no')
            if len(heditstr) > 65:
                nfields = int(len(heditstr)/65) #Declare int for py3 compatibility
                for ii in range(nfields+1):
                    writestr = heditstr[(ii*65):(ii+1)*65]
                    iraf.hedit(images='f'+obj,fields='flatcor'+str(ii),value=writestr,add='yes',verify='No')
            else:
                iraf.hedit(images='f'+obj,fields='flatcor',value=heditstr,add='yes',verify='No')
        else:
            iraf.imarith(operand1=obj,operand2=object_match[obj][0],op='/',result='f'+obj)
            heditstr = 'Flat field image is '+object_match[obj][0]
            if len(heditstr) > 65:
                nfields = int(len(heditstr)/65) #Declare int for py3 compatibility
                for ii in range(nfields+1):
                    writestr = heditstr[(ii*65):(ii+1)*65]
                    iraf.hedit(images='f'+obj,fields='flatcor'+str(ii),value=writestr,add='yes',verify='No')
            else:
                iraf.hedit(images='f'+obj,fields='flatcor',value=heditstr,add='yes',verify='No')
    return


def standard_trace(standard_list,supplement_list,outname='star'):
    irf_prm.set_identify_standard(iraf.identify)
    irf_prm.set_reidentify_standard(iraf.reidentify)
    irf_prm.set_fitcoords_standard(iraf.fitcoords)
    all_standards = ''
    for standrd in standard_list:
        iraf.identify(images=standrd)
        iraf.reidentify(reference=standrd,images=standrd)
        all_standards += standrd[:-5]+','
    for supplement in supplement_list:
        iraf.identify(images=supplement)
        iraf.reidentify(reference=supplement,images=supplement)
        all_standards += supplement[:-5]+','
    iraf.fitcoords(images=all_standards,fitname=outname)
    return

def make_lambda_solution(arc_list,fcnamedict):
    irf_prm.set_identify_calibration(iraf.identify)
    irf_prm.set_reidentify_calibration(iraf.reidentify)
    irf_prm.set_fitcoords_calibration(iraf.fitcoords)
    for arc in arc_list:
        iraf.identify(images=arc)
        iraf.reidentify(reference=arc,images=arc)
        iraf.fitcoords(images=arc[:-5],fitname=fcnamedict[arc])
    return

def transform(science_list,object_match,arc_fc_dict,arc_coords,fcstar='star'):
    '''Transforms filename to t+filename using noao>twodspec>longslit>transform'''
    irf_prm.set_transform(iraf.transform)
    for obj in science_list:
        fcarc = arc_fc_dict[object_match[obj]]
        dx_param = arc_coords[object_match[obj]]
        iraf.transform.x1 = dx_param[0]
        iraf.transform.x2 = dx_param[1]
        iraf.transform.dx = dx_param[2]
        iraf.transform(input=obj,output='t'+obj,fitnames=fcstar+','+fcarc)
    return
    
def apall_std(stdlist):
    irf_prm.set_apall_std(iraf.apall)
    for std in stdlist:
        iraf.apall(input=std,output = 's'+std,nfind=0)#,interactive='no')
    return

def standard(stdlist,std_name,stdidx):
    irf_prm.set_standard(iraf.standard)
    for std in stdlist:
        iraf.standard(input='s'+std,output='std'+str(stdidx),star_name=std_name)
    return

def sensfunc(stdidx):
    iraf.sensfunc(standards='std'+str(stdidx),sensitivity='sens'+str(stdidx))
    return

def flux_calibrate(objlist,stdidx):
    irf_prm.set_calibrate(iraf.specred.calibrate)
    for clbobj in objlist:
        iraf.specred.calibrate(input=clbobj,output='l'+clbobj,airmass=None,exptime=None,sensitivity='sens'+str(stdidx))
    return

def background(objlist):
    irf_prm.set_background(iraf.background)
    for bkgobj in objlist:
        iraf.background(input='l'+bkgobj,output='sl'+bkgobj)
    return

def imcombine(inlist,outname):
    imcinpt = ''
    for obj in inlist:
        imcinpt += 'sl'+obj +','
    iraf.imcombine(input=imcinpt,output=outname,sigmas=outname+'_sig',combine='median')
    return
