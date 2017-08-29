from pyraf import iraf
import iraf_parameters as irf_prm
import fits_tools as ftl

def gui_alert():
    print 'An IRAF GUI has been opened and requires your input'
    
def initialize_iraf():
    iraf.noao(_doprint=0)
    iraf.imred(_doprint=0)
    iraf.ccdred(_doprint=0)
    iraf.specred(_doprint=0)
    iraf.twodspec(_doprint=0)
    iraf.apextract(_doprint=0)
    iraf.longslit(_doprint=0)
    return

def reduce_dimensions(filename):
    iraf.imcopy(filename+'[*,*,1]',filename)
    #iraf.hedit(ccdsec) #What is this supposed to do?
    iraf.hedit(filename,'EPOCH',2000,add=True,verify='No')
    iraf.wcsreset(image=filename,wcs='world')
    return

def bias_correct(file_list,xmin='18',xmax='4111',ymin='350',
                 ymax='1570',bindefault=1):
    irf_prm.set_ccdproc(iraf.ccdproc)
    biassecs = {1:'[4114:4142,1:1896]',2:'[4114:4142,1:1896]',
                3:'[4114:4142,1:1896]',4:'[4114:4142,1:1896]'} #NEED UPDATED
    #iraf.ccdproc.biassec = biassecs[binsize]
    iraf.ccdproc.trimsec = '['+xmin+':'+xmax+','+ymin+':'+ymax+']'
    for ff in file_list:
        comm = ftl.get_comment(ff,'PARAM18')
        if comm == '1 / Serial Binning,Pixels':
            binsize = iraf.hselect(ff,'PARAM18','yes')
        else:
            prm_com = '1 / Serial Binning,Pixels'
            param_name = ftl.find_param_with_comment(ff,prm_com)
            if param_name == 'NullReturn':
                binsize=bindefault
            else:
                binsize = iraf.hselect(ff,param_name,'yes')
        iraf.ccdproc.biassec = biassecs[binsize]
        output = 'b'+ff
        iraf.ccdproc(images=ff,output=output,ccdtype = "")
    return

def artifact_imcombine(inlist,outname):
    imcinpt = ''
    for obj in inlist:
        imcinpt += obj +','
    imcinpt = imcinpt[:-1] #Drop trailing comma
    iraf.imcombine(input=imcinpt,output=outname,sigmas=outname+'_sig',
                   combine='median')
    return

def normalize_artifact(artifact,nartifact):
    print 'When you are prompt to edit aperture, you will be facing a '
    print 'columns cut (usually) in the middle of the image without any'
    print 'aperture. Include a new aperture in the center of the image'
    print 'with "n" and resize the aperture to fit the entire range '
    print '(I use "l" for lower and "u" for upper, in the borders),'
    print 'Hit "q" and the fitting window will appear in place of '
    print 'the aperture selection.'
    irf_prm.set_apflatten(iraf.apflatten)
    iraf.apflatten(input=artifact,output=nartifact)
    
def artifact_create(artifact,theta,output):
    iraf.imarith(operand1=artifact,operand2=theta,op='*',
                 result='tmpartifact.fits')
    iraf.imarith(operand1='tmpartifact.fits',operand2=1-theta,op='+',
                 result=output)
    iraf.imdelete(images='tmpartifact.fits',go_ahead='yes',verify='no')
    return

def correct_artifact(wnartifact,qtz):
    iraf.imarith(operand1=qtz,operand2=wnartifact,op='/',result='a'+qtz)
    return

def normalize_quartzes(quartz_list,dont_norm_list):
    '''Normalize files in quartz_list using noao>twodspec>longslit>response'''
    irf_prm.set_response(iraf.response)
    for quartz in quartz_list:
        if quartz in dont_norm_list:
            continue
        iraf.response(calibrat=quartz,normaliz=quartz,response='n'+quartz)
        dont_norm_list.append(quartz)
    return

def quartz_divide(science_list,object_match):
    '''Divide science frames by user-selected quartz frames'''
    for obj in science_list:
        if len(object_match[obj]) > 1:
            qtzinpt = ''
            for qtz in object_match[obj]:
                qtzinpt += qtz +','
            iraf.imcombine(input=qtzinpt,output='tempquartz')
            iraf.imarith(operand1=obj,operand2='tempquartz',op='/',
                         result='f'+obj)
            heditstr = 'Flat field images are '+qtzinpt[:-1]
            iraf.imdelete(images='tempquartz',go_ahead='yes',verify='no')
            if len(heditstr) > 65:
                nfields = int(len(heditstr)/65)#Declare int for py3 compatibility
                for ii in range(nfields+1):
                    writestr = heditstr[(ii*65):(ii+1)*65]
                    iraf.hedit(images='f'+obj,fields='flatcor'+str(ii),
                               value=writestr,add='yes',verify='No')
            else:
                iraf.hedit(images='f'+obj,fields='flatcor',
                           value=heditstr,add='yes',verify='No')
        else:
            iraf.imarith(operand1=obj,operand2=object_match[obj][0],op='/',
                         result='f'+obj)
            heditstr = 'Flat field image is '+object_match[obj][0]
            if len(heditstr) > 65:
                nfields = int(len(heditstr)/65)#Declare int for py3 compatibility
                for ii in range(nfields+1):
                    writestr = heditstr[(ii*65):(ii+1)*65]
                    iraf.hedit(images='f'+obj,fields='flatcor'+str(ii),
                               value=writestr,add='yes',verify='No')
            else:
                iraf.hedit(images='f'+obj,fields='flatcor',
                           value=heditstr,add='yes',verify='No')
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

def make_lambda_solution(arc_list,fcnamedict,dont_ident_list):
    irf_prm.set_identify_calibration(iraf.identify)
    irf_prm.set_reidentify_calibration(iraf.reidentify)
    irf_prm.set_fitcoords_calibration(iraf.fitcoords)
    for arc in arc_list:
        if arc in dont_ident_list:
            continue
        iraf.identify(images=arc)
        iraf.reidentify(reference=arc,images=arc)
        iraf.fitcoords(images=arc[:-5],fitname=fcnamedict[arc])
        dont_ident_list.append(arc)
    return

def transform(science_list,object_match,arc_fc_dict,arc_coords,fcstar='star'):
    '''Transform filename to t+filename using noao>twodspec>longslit>transform'''
    irf_prm.set_transform(iraf.transform)
    for obj in science_list:
        fcarc = arc_fc_dict[object_match[obj]]
        dx_param = arc_coords[object_match[obj]]
        #These should be the same for each observing mode
        #Because then they're all mapped together for
        #Accurate flux calibration and imcombining
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
        iraf.specred.calibrate(input=clbobj,output='l'+clbobj,
                               airmass=None,exptime=None,
                               sensitivity='sens'+str(stdidx))
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
    iraf.imcombine(input=imcinpt,output=outname,sigmas=outname+'_sig',
                   combine='median')
    return
